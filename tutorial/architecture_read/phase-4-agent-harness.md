# Phase 4: AgentHarness

Source: [dev-notes/architecture/phase-4-agent-harness.md](../../dev-notes/architecture/phase-4-agent-harness.md)

这一 phase 给纯 loop 外面套了一层有状态 harness。它是可复用 agent brain 的主要入口。

## 要抓住的主线

`run_agent_loop` 是函数，`AgentHarness` 是对象。

Harness 负责：

- 持有 transcript。
- 暴露 `prompt()` 和 `continue_()`。
- 管理 event listener。
- 管理 cancellation token。
- 防止同一个 harness 上并发跑多个 prompt。
- 支持 queued steering 和 follow-up。

但它不负责 CLI、TUI、session 文件位置，也不负责资源发现。

## 源码阅读路线

读 [src/tau_agent/harness.py](../../src/tau_agent/harness.py)。

重点看：

- `AgentHarnessConfig`
- `AgentHarness.prompt`
- `AgentHarness.continue_`
- `AgentHarness._run`
- `SimpleCancellationToken`

`prompt()` 会把用户输入变成 `UserMessage` 并 append 到 harness 的 `_messages`。真正执行仍然委托给 `run_agent_loop`。

## 与 loop 的分工

Loop 关心一次 run 的算法。Harness 关心跨 run 的状态。

可以这样记：

```text
run_agent_loop = 怎么跑一轮 agent
AgentHarness   = 一个 agent 实例如何保存状态并多次运行
```

## 测试入口

```bash
uv run pytest tests/test_agent_harness.py -q
```

重点看：

- `test_prompt_appends_user_message_and_assistant_response`
- `test_continue_runs_without_adding_user_message`
- `test_messages_property_returns_immutable_snapshot`
- `test_harness_rejects_overlapping_prompt_runs`

## 自检问题

- 为什么 harness 要返回 transcript 的 immutable snapshot?
- `prompt()` 和 `continue_()` 的区别是什么?
- 为什么防止 overlapping prompt 很重要?
- Harness 为什么仍然不能依赖 Textual 或 Rich?
