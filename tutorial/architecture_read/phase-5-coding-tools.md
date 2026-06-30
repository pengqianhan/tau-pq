# Phase 5: Built-in Coding Tools

Source: [dev-notes/architecture/phase-5-coding-tools.md](../../dev-notes/architecture/phase-5-coding-tools.md)

这一 phase 加入真正的编码工具：`read`、`write`、`edit`、`bash`。

## 要抓住的主线

工具实现放在 `tau_coding`，不是 `tau_agent`。

原因是：读写文件、执行 shell、路径约束、命令超时都属于 coding-agent 应用环境。可复用的 agent brain 只需要知道 `AgentTool` 接口。

## 源码阅读路线

读 [src/tau_coding/tools.py](../../src/tau_coding/tools.py)。

重点看：

- `ToolDefinition`
- `ToolDefinition.to_agent_tool`
- `create_read_tool_definition`
- `create_write_tool_definition`
- `create_edit_tool_definition`
- `create_bash_tool_definition`
- `create_coding_tools`

`ToolDefinition` 比 `AgentTool` 多 prompt metadata。`to_agent_tool()` 把应用层的富定义降级成 agent 层可执行工具。

## 四个工具怎么理解

- `read`: 读文件，支持 offset / limit，避免一次塞爆上下文。
- `write`: 写文件，必要时创建父目录。
- `edit`: 精确替换文本，失败时不能留下半成品。
- `bash`: 执行 shell 命令，记录 stdout、exit code、timeout、cancellation。

## 测试入口

```bash
uv run pytest tests/test_coding_tools.py::test_read_tool_reads_file_with_offset_and_limit \
              tests/test_coding_tools.py::test_write_tool_creates_parent_directories \
              tests/test_coding_tools.py::test_edit_tool_rolls_back_when_any_edit_fails -q
```

## 自检问题

- 为什么真实工具不放在 `tau_agent`?
- `ToolDefinition` 和 `AgentTool` 的区别是什么?
- `edit` 为什么需要 rollback?
- 工具抛异常后，哪里负责转成 `ok=False`?
