# Phase 19: Project Context Discovery and Reload

Source: [dev-notes/architecture/phase-19-context-discovery.md](../../dev-notes/architecture/phase-19-context-discovery.md)

这一 phase 让 Tau 自动发现项目上下文文件，例如 `AGENTS.md`，并支持 reload。

## 要抓住的主线

Coding agent 需要知道项目规则。Context discovery 负责从当前项目和上级路径中找规则文件，并把它们加入 system prompt。

Reload 让用户在 TUI 中更新资源和上下文，而不用重启应用。

## 源码阅读路线

读：

- [src/tau_coding/context.py](../../src/tau_coding/context.py)
- [src/tau_coding/system_prompt.py](../../src/tau_coding/system_prompt.py)
- [src/tau_coding/reload.py](../../src/tau_coding/reload.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)

## 关键理解

项目上下文是 system prompt 的输入，不是 transcript message。它描述规则和环境，不是用户对话。

Reload 需要刷新 skills、prompt templates、context files 和 system prompt，但要避免破坏当前 transcript。

## 测试入口

```bash
uv run pytest tests/test_context.py \
              tests/test_coding_session.py::test_session_reload_refreshes_resources_and_system_prompt -q
```

## 自检问题

- 项目上下文为什么进入 system prompt 而不是普通 user message?
- reload 应该刷新哪些内容?
- 为什么 context discovery 属于 `tau_coding`?
- 多个上下文文件的顺序为什么重要?
