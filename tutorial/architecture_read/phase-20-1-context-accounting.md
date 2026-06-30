# Phase 20.1: Context Accounting Refresh

Source: [dev-notes/architecture/phase-20-1-context-accounting.md](../../dev-notes/architecture/phase-20-1-context-accounting.md)

这一 phase 引入上下文 token 估算和 UI 刷新边界。

## 要抓住的主线

Agent 需要知道当前上下文大概用了多少 token，尤其后面要做 compaction。

Context accounting 估算：

- system prompt tokens
- message tokens
- tool schema tokens
- total usage

## 源码阅读路线

读：

- [src/tau_coding/context_window.py](../../src/tau_coding/context_window.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)
- [src/tau_coding/tui/app.py](../../src/tau_coding/tui/app.py)

## 关键理解

这是估算，不是 provider 官方 tokenizer。目的不是精确计费，而是给 UI 和 auto-compaction 一个稳定信号。

TUI 应该在消息变化、compaction、resume 等时候刷新 context usage。

## 测试入口

```bash
uv run pytest tests/test_context_window.py \
              tests/test_coding_session.py::test_context_usage_recalculates_after_prompt_and_compaction -q
```

## 自检问题

- 为什么这里可以用估算而不是精确 tokenizer?
- 哪些输入会影响 context usage?
- context accounting 为什么在 `tau_coding`?
- UI 刷新应该由 agent event 直接驱动，还是 session state 驱动?
