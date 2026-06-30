# Phase 3: Pure Agent Loop

Source: [dev-notes/architecture/phase-3-agent-loop.md](../../dev-notes/architecture/phase-3-agent-loop.md)

这一 phase 是 Tau 的核心循环。它把 provider 事件翻译成 agent 事件，执行工具，并维护 transcript。

## 要抓住的主线

`run_agent_loop(...)` 是纯 agent 逻辑：

1. 调 provider 获取流式事件。
2. 把 provider event 翻译成 agent event。
3. 收集最终 `AssistantMessage`。
4. 如果 assistant 请求工具，就执行工具。
5. 把 `ToolResultMessage` 追加回 transcript。
6. 继续下一轮，直到没有 tool calls。

## 源码阅读路线

读 [src/tau_agent/loop.py](../../src/tau_agent/loop.py)。

重点函数：

- `run_agent_loop`
- `_execute_tool_calls`
- `_execute_tool`
- `_tool_result_message`

读 `run_agent_loop` 时不要先纠结异常边界，先看主线：`agent_start` -> `turn_start` -> provider stream -> assistant message -> tool calls -> next turn。

## 关键边界

Loop 会改变 `messages` 列表：它会 append assistant message 和 tool result message。调用方拥有 transcript，但 loop 负责把本次 run 的新消息补进去。

Loop 不负责 UI，也不 print。它只 yield `AgentEvent`。

工具异常不会直接炸掉 loop。`_execute_tool` 会把异常转成 `AgentToolResult(ok=False)`，让模型看到失败结果。

## 测试入口

```bash
uv run pytest tests/test_agent_loop.py -q
```

重点看：

- `test_agent_loop_streams_text_and_appends_assistant_message`
- `test_agent_loop_executes_tools_and_continues_until_no_tool_calls`
- `test_agent_loop_records_unknown_tool_as_failed_tool_result`
- `test_agent_loop_converts_provider_error_to_agent_error`

## 自检问题

- `messages` 是谁传入的? loop 对它做什么?
- loop 根据什么判断是否进入下一轮?
- provider event 和 agent event 的区别是什么?
- 为什么工具异常要转成 tool result，而不是直接 raise 出去?
