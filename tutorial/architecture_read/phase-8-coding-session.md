# Phase 8: Coding Session Wrapper

Source: [dev-notes/architecture/phase-8-coding-session.md](../../dev-notes/architecture/phase-8-coding-session.md)

这一 phase 在 `tau_coding` 里创建 `CodingSession`。它把 harness、工具、session storage、应用命令组合起来。

## 要抓住的主线

`AgentHarness` 是可复用大脑，`CodingSession` 是编码 agent 的运行环境。

`CodingSession` 负责：

- 加载和 replay session storage。
- 创建 coding tools。
- 构建 system prompt。
- 调用 harness prompt/continue。
- 持久化新消息和 leaf。
- 处理最小命令。

## 源码阅读路线

读 [src/tau_coding/session.py](../../src/tau_coding/session.py)。

重点看：

- `CodingSessionConfig`
- `CodingSession.load`
- `CodingSession.prompt`
- `CodingSession.continue_`
- persistence 相关辅助函数
- minimal command handling

读的时候反复问：这段逻辑是通用 agent brain，还是 coding app 环境? 如果是后者，就应该在 `tau_coding`。

## 关键理解

`CodingSession` 是后续 CLI 和 TUI 的共享应用层。CLI/TUI 不应该自己管理 transcript replay、工具创建、system prompt 组装。

## 测试入口

```bash
uv run pytest tests/test_coding_session.py::test_load_empty_session_defers_transcript_file \
              tests/test_coding_session.py::test_prompt_persists_user_assistant_and_leaf_entries -q
```

## 自检问题

- `CodingSession` 为什么不放在 `tau_agent`?
- 它内部持有什么核心对象?
- prompt 结束后需要持久化哪些 entry?
- CLI 和 TUI 为什么都应该复用它?
