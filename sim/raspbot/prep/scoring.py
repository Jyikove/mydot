"""Finite-cylinder containment in a closed, world-XY goal rectangle."""

from dataclasses import dataclass
from math import hypot
from typing import Iterable

from interface import Bounds, finite

Vec3 = tuple[float, float, float]


@dataclass(frozen=True)
class Rectangle:
    x: Bounds
    y: Bounds


DEFAULT_GOAL = Rectangle(Bounds(2.70, 3.00), Bounds(0.50, 1.50))


@dataclass(frozen=True)
class Cylinder:
    center: Vec3
    axis: Vec3
    radius: float
    half_height: float

    def __post_init__(self) -> None:
        if len(self.center) != 3 or len(self.axis) != 3:
            raise ValueError("center and axis must be three-dimensional")
        for value in self.center + self.axis:
            finite(value, "center/axis component")
        finite(self.radius, "radius")
        finite(self.half_height, "half_height")
        if self.radius <= 0 or self.half_height <= 0:
            raise ValueError("radius and half_height must be positive")
        if not any(self.axis):
            raise ValueError("axis must be nonzero")

    def xy_extent(self) -> tuple[float, float]:
        # Scale before normalizing so even large/small finite directions work.
        scale = max(abs(component) for component in self.axis)
        scaled = tuple(component / scale for component in self.axis)
        length = hypot(*scaled)
        ux, uy, uz = (component / length for component in scaled)
        # hypot(other components) equals sqrt(1 - u_i**2), but is stable
        # when the axis is nearly parallel to the coordinate being projected.
        return (
            self.half_height * abs(ux) + self.radius * hypot(uy, uz),
            self.half_height * abs(uy) + self.radius * hypot(ux, uz),
        )


@dataclass(frozen=True)
class PieceScore:
    """Signed clearances to the left/right/bottom/top sides in metres."""

    left: float
    right: float
    bottom: float
    top: float

    @property
    def min_clearance(self) -> float:
        return min(self.left, self.right, self.bottom, self.top)

    @property
    def contained(self) -> bool:
        return self.min_clearance >= 0.0


@dataclass(frozen=True)
class GoalScore:
    pieces: tuple[PieceScore, ...]

    @property
    def count(self) -> int:
        return sum(piece.contained for piece in self.pieces)

    @property
    def fraction(self) -> float:
        return self.count / len(self.pieces) if self.pieces else 0.0

    @property
    def success(self) -> bool:
        return bool(self.pieces) and self.count == len(self.pieces)


def score_goal(cylinders: Iterable[Cylinder], goal: Rectangle = DEFAULT_GOAL) -> GoalScore:
    pieces = []
    for cylinder in cylinders:
        x, y, _ = cylinder.center
        dx, dy = cylinder.xy_extent()
        pieces.append(
            PieceScore(
                (x - dx) - goal.x.lower,
                goal.x.upper - (x + dx),
                (y - dy) - goal.y.lower,
                goal.y.upper - (y + dy),
            )
        )
    return GoalScore(tuple(pieces))
