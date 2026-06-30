# Phase 16: Robust Resource Discovery

Source: [dev-notes/architecture/phase-16-resource-discovery.md](../../dev-notes/architecture/phase-16-resource-discovery.md)

这一 phase 强化 skills 和 prompt templates 的发现过程，让坏资源不会让整个 session 崩掉。

## 要抓住的主线

资源发现可能遇到：

- 文件格式不对。
- frontmatter 不合法。
- 同名覆盖。
- 用户目录和项目目录冲突。

Phase 16 的目标是报告 diagnostics，而不是直接失败。

## 源码阅读路线

读：

- [src/tau_coding/resources.py](../../src/tau_coding/resources.py)
- [src/tau_coding/skills.py](../../src/tau_coding/skills.py)
- [src/tau_coding/prompt_templates.py](../../src/tau_coding/prompt_templates.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)

## 关键理解

对 coding agent 来说，资源错误应该可见但不应该总是致命。用户仍然应该能启动 TUI，然后看到资源诊断。

这也是应用层职责：核心 agent 不知道资源目录，因此也不应该知道 diagnostics。

## 测试入口

```bash
uv run pytest tests/test_skills.py tests/test_prompt_templates.py tests/test_resources.py -q
```

## 自检问题

- 为什么资源发现失败不一定要阻止 session 启动?
- diagnostics 应该在哪里展示?
- 项目资源覆盖用户资源时，用户如何知道发生了覆盖?
- 这类逻辑为什么不能进 `tau_agent`?
