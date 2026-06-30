# Phase 20.2: Thinking Mode Controls

Source: [dev-notes/architecture/phase-20-2-thinking-controls.md](../../dev-notes/architecture/phase-20-2-thinking-controls.md)

这一 phase 加入 thinking/reasoning effort 控制。

## 要抓住的主线

不同 provider 和模型对 reasoning/thinking 的支持不同。Tau 需要统一用户层控制，同时尊重 provider 能力。

Thinking controls 涉及：

- 可用 thinking levels。
- 默认 thinking level。
- session 持久化。
- slash command / keybinding / TUI picker。
- provider runtime 参数映射。

## 源码阅读路线

读：

- [src/tau_coding/thinking.py](../../src/tau_coding/thinking.py)
- [src/tau_coding/provider_config.py](../../src/tau_coding/provider_config.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)
- [src/tau_ai/openai_compatible.py](../../src/tau_ai/openai_compatible.py)
- [src/tau_ai/anthropic.py](../../src/tau_ai/anthropic.py)

## 关键理解

UI 里显示的 thinking level 是 Tau 的应用概念。真正发给 provider 的字段可能叫 `reasoning_effort`、thinking budget，或者根本不支持。

## 测试入口

```bash
uv run pytest tests/test_thinking.py tests/test_provider_config.py::test_builtin_openai_declares_model_scoped_thinking_capabilities -q
```

## 自检问题

- `off` 和 unsupported 是一回事吗?
- thinking level 如何持久化到 session?
- provider 不支持 thinking 时 UI 应该怎么提示?
- 为什么 thinking 映射不应该写死在 TUI?
