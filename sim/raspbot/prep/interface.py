"""Pure-Python simulation interface contract. No physics or hardware backend."""

from dataclasses import dataclass
from math import isfinite
from typing import Literal, Mapping, Protocol, TypedDict


def finite(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be a finite real number")


@dataclass(frozen=True)
class Bounds:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        finite(self.lower, "lower")
        finite(self.upper, "upper")
        if self.lower > self.upper:
            raise ValueError("lower must not exceed upper")

    def validate(self, value: float, label: str) -> None:
        finite(value, label)
        if not self.lower <= value <= self.upper:
            raise ValueError(f"{label} must lie in [{self.lower}, {self.upper}]")


@dataclass(frozen=True)
class Action:
    """Body-frame velocities (m/s, rad/s) and gimbal targets (rad)."""

    vx: float
    vy: float
    wz: float
    pan: float
    tilt: float

    def __post_init__(self) -> None:
        for name in ("vx", "vy", "wz", "pan", "tilt"):
            finite(getattr(self, name), name)


@dataclass(frozen=True)
class ActionLimits:
    """Provisional simulator limits, not measured hardware capabilities."""

    vx: Bounds
    vy: Bounds
    wz: Bounds
    pan: Bounds
    tilt: Bounds

    def validate(self, action: Action) -> Action:
        for name in ("vx", "vy", "wz", "pan", "tilt"):
            getattr(self, name).validate(getattr(action, name), name)
        return action


PHYSICS_HZ = 240
CONTROL_HZ = 20
CAMERA_HZ = 15
CONTROL_TICKS = PHYSICS_HZ // CONTROL_HZ
CAMERA_TICKS = PHYSICS_HZ // CAMERA_HZ


@dataclass(frozen=True)
class StepWindow:
    """Ticks elapsed after each integration; initial capture at tick zero is separate."""

    start_tick: int
    end_tick: int
    camera_ticks: tuple[int, ...]

    @property
    def time_s(self) -> float:
        return self.end_tick / PHYSICS_HZ


class SimClock:
    """Schedule control/camera events on integer physics ticks, not wall time."""

    def __init__(self) -> None:
        self.reset()

    @property
    def tick(self) -> int:
        return self._tick

    def reset(self) -> None:
        self._tick = 0

    def next_control(self) -> StepWindow:
        start = self._tick
        end = start + CONTROL_TICKS
        first_camera = (start // CAMERA_TICKS + 1) * CAMERA_TICKS
        self._tick = end
        return StepWindow(start, end, tuple(range(first_camera, end + 1, CAMERA_TICKS)))


@dataclass(frozen=True)
class RGBFrame:
    """Packed RGB8 in row-major order, tagged by capture tick."""

    tick: int
    width: int
    height: int
    data: bytes


@dataclass(frozen=True)
class Observation:
    """Default policy inputs only; onboard can be absent until the first capture."""

    tick: int
    onboard: RGBFrame | None


class StepInfo(TypedDict, total=False):
    camera_fresh: bool


class RobotEnv(Protocol):
    def reset(
        self, *, seed: int = 0, layout: str = "single", options: Mapping[str, object] | None = None
    ) -> Observation: ...

    def step(self, action: Action) -> tuple[Observation, float, bool, bool, StepInfo]: ...

    def render(
        self, camera: str = "onboard", channels: tuple[Literal["rgb"], ...] = ("rgb",)
    ) -> Mapping[str, RGBFrame]: ...

    def get_ground_truth(self) -> Mapping[str, object]: ...

    def close(self) -> None: ...
