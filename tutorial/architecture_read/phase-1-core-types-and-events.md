# Phase 1: Core Types and Events

Source: [dev-notes/architecture/phase-1-core-types-and-events.md](../../dev-notes/architecture/phase-1-core-types-and-events.md)

这一 phase 的目标是先定义 Tau 的共同语言。后面无论是 provider、loop、tool、session 还是 UI，都要围绕这些类型交换数据。

## 要抓住的主线

Phase 1 加了四类核心模块：

- `types.py`: JSON-like 类型别名。
- `messages.py`: transcript 里的消息类型。
- `tools.py`: 工具调用、工具定义、工具结果。
- `events.py`: agent 层向外发出的事件。

这些都在 `tau_agent`，所以它们必须保持 provider-neutral 和 UI-neutral。这里不应该出现 OpenAI、Anthropic、Rich、Textual、CLI、项目路径等概念。

## `types.py` 怎么读

先读 [src/tau_agent/types.py](../../src/tau_agent/types.py)。

```python
type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]
type JSONObject = dict[str, JSONValue]
```

这里用了 Python 3.12+ 的 `type` 类型别名语法。`JSONValue` 是递归类型：一个 JSON 值可以是基础值、JSON 数组，或者 JSON 对象。Tau 用它约束工具参数、工具 schema、事件 data、provider payload 等结构化数据。

关键理解：这些类型不是运行时解析器，它们主要服务类型检查、Pydantic 字段声明和代码阅读。运行时校验仍然发生在模型、工具参数解析和 Pydantic model 中。

## 消息模型怎么读

读 [src/tau_agent/messages.py](../../src/tau_agent/messages.py)。

- `UserMessage`: 用户输入。
- `AssistantMessage`: assistant 文本和可选 `tool_calls`。
- `ToolResultMessage`: 某次工具调用的结果。
- `AgentMessage`: 三者的 union，代表 transcript 中任意一条消息。

读的时候重点看 `role` 字段和 `extra="forbid"`。前者让 transcript 可序列化，后者禁止脏字段混进核心状态。

## 工具模型怎么读

读 [src/tau_agent/tools.py](../../src/tau_agent/tools.py)。

- `ToolCall` 是模型发出的调用请求，不是工具本身。
- `AgentTool` 是 Tau 暴露给模型的工具定义。
- `AgentToolResult` 是工具执行后的结构化输出。

`AgentTool.execute()` 本质上只是 `await self.executor(...)`。真正的文件读写、bash 执行等实现不在 `tau_agent`，后面 Phase 5 才会放到 `tau_coding`。

## 事件模型怎么读

读 [src/tau_agent/events.py](../../src/tau_agent/events.py)。

每个事件都有稳定的 `type` 字段，例如 `agent_start`、`message_delta`、`tool_execution_end`。这就是后面 CLI、Rich renderer、Textual TUI 都能消费同一串事件的基础。

## 测试入口

```bash
uv run pytest tests/test_agent_types.py -q
```

重点看：

- `test_models_reject_unknown_fields`
- `test_agent_tool_executes_with_json_arguments`
- `test_events_have_stable_type_names`

## 自检问题

- 为什么 `types.py` 只定义 JSON-like 类型，而不定义 provider payload?
- 为什么 `AssistantMessage` 要允许同时有 `content` 和 `tool_calls`?
- 为什么事件要用稳定的 `type` 字段?
- 为什么这些类型必须放在 `tau_agent` 而不是 `tau_coding`?
