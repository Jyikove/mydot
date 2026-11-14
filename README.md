# mydot

> Dot 的长期任务协作仓库（Long-running Agent Workspace）

这个仓库用于**存放计划、记录执行状态、保存任务证据和交付成果**。它是人类与 Dot / Codex / Work 协作时可审查的共享工作区，不代表 GitHub 会自动触发 Dot，也不代表 Dot 天然具有本仓库的访问权限。

## 从哪里开始

| 文件或目录 | 用途 | 主要维护者 |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | Agent 的工作流程、安全边界和交付规范 | 人类审核，Agent 遵守 |
| [PERSONA.md](PERSONA.md) | Fairy 的完整人设、自然情绪表达和交流风格 | 人类定义，Dot 采用 |
| [plan.md](plan.md) | 目标、优先级、任务清单及验收标准 | 人类主导 |
| [status.md](status.md) | 当前任务、阻塞、下一步和运行记录 | Agent 更新 |
| [tasks/](tasks/) | 每项任务的独立说明和验收证据 | 人类 / Agent |
| [logs/](logs/) | 结构化执行日志（不存敏感信息） | Agent |
| [reports/](reports/) | 阶段总结与最终报告 | Agent |
| [docs/DOT_START_PROMPT.md](docs/DOT_START_PROMPT.md) | 给 Dot 的首次接入指令 | 人类复制使用 |
| [docs/FAIRY_CUSTOM_INSTRUCTIONS.md](docs/FAIRY_CUSTOM_INSTRUCTIONS.md) | 适合粘贴至 Dot 设置的短版人设 | 人类复制使用 |

## 推荐工作流

1. **你**在本地修改 `plan.md`，并提交到 GitHub。
2. **你**在 Dot 中明确授权 GitHub 访问，并发送 [接入指令](docs/DOT_START_PROMPT.md)。
3. **Dot**读取 `AGENTS.md`、`PERSONA.md`、`plan.md`、`status.md`，确认权限、风格、环境和下一项可执行任务。
4. **Dot / Codex / Work**在已授权的环境中执行任务；把进度、测试证据和产物记录到仓库。
5. **你**审核需确认的操作、代码 PR 和重要决策，再进入下一阶段。

**注意：** GitHub 仓库本身不会自动运行任务。每次执行需要 Dot 已连接仓库并实际启动相关工作；若要定时检查，还需要单独配置支持的定时工作流。

## 初始化后的第一步

- [ ] 在 Dot 中确认可以读取此仓库。
- [ ] 确认 Dot 是否有提交 / PR 权限；原则上优先通过工作分支和 PR 提交代码。
- [ ] 在 `plan.md` 写下**第一个真实项目任务**与验收标准。
- [ ] 让 Dot 开始执行并更新 `status.md`。

## 安全原则

- 仓库为 **Public（公开）**。不要写入密码、SSH 私钥、Token、`.env`、个人隐私或服务器敏感配置。
- `plan.md` 是任务意图，**不是**运行任意命令的安全许可。
- 破坏性操作、权限升级、生产环境变更、外部发送及费用相关操作，必须事先得到明确授权。
- 未经明确许可，不应修改 `main` 上的代码或覆盖已有成果。
- 将仓库视为**协作与审计记录**，而不是持久化机密或云端计算环境的替代品。

_初始化日期：2026-11-13。_
