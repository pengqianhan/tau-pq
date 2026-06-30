# Phase 10: System Prompt Assembly

Source: [dev-notes/architecture/phase-10-system-prompt.md](../../dev-notes/architecture/phase-10-system-prompt.md)

这一 phase 把工具说明、项目上下文、skills、日期、工作目录等组装成 system prompt。

## 要抓住的主线

System prompt 是 coding app 的运行说明。它把 agent brain 和当前项目环境连接起来。

默认 prompt 包含：

- 当前日期和 cwd。
- 工具使用规则。
- 可用工具说明。
- 项目上下文。
- skill index。

## 源码阅读路线

读 [src/tau_coding/system_prompt.py](../../src/tau_coding/system_prompt.py)。

重点看：

- `BuildSystemPromptOptions`
- `build_system_prompt`
- 工具 prompt snippets 如何加入。
- project context 如何加入。
- skills 如何格式化。

## 关键理解

System prompt 不是 `tau_agent` 的一部分，因为它知道 coding app 的工具、文件路径、项目上下文和资源目录。

同时它也不是 UI 的一部分。CLI 和 TUI 应该拿到同样的 session/system prompt 逻辑。

## 测试入口

```bash
uv run pytest tests/test_system_prompt.py -q
```

## 自检问题

- 为什么自定义 system prompt 仍然可能要保留日期和上下文?
- 工具没有 prompt snippet 时会怎样?
- Skills 为什么需要 XML-like 格式?
- system prompt 组装为什么属于 `tau_coding`?
