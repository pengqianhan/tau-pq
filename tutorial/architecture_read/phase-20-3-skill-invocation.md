# Phase 20.3: Skill Invocation Reliability

Source: [dev-notes/architecture/phase-20-3-skill-invocation.md](../../dev-notes/architecture/phase-20-3-skill-invocation.md)

这一 phase 强化 skills 的可发现性、手动调用和 TUI 展示。

## 要抓住的主线

Skill 不只是静态文档。它需要在合适时候被 agent 发现、读取、显示，并能被用户手动触发。

这 phase 关注可靠性：

- system prompt 中明确 skill 可用性。
- `/skill:name` 手动调用。
- skill file read 在 TUI 中用特殊样式显示。
- ordinary read 和 skill read 要区分。

## 源码阅读路线

读：

- [src/tau_coding/skills.py](../../src/tau_coding/skills.py)
- [src/tau_coding/system_prompt.py](../../src/tau_coding/system_prompt.py)
- [src/tau_coding/tui/adapter.py](../../src/tau_coding/tui/adapter.py)
- [src/tau_coding/tui/state.py](../../src/tau_coding/tui/state.py)

## 关键理解

Skill invocation 的关键是让 agent 能准确读取对应 skill 文件，而不是把所有 skill 都塞进上下文。

TUI 特殊展示只是可视化，不改变 tool result 的语义。

## 测试入口

```bash
uv run pytest tests/test_skills.py \
              tests/test_tui_adapter.py::test_tui_adapter_renders_skill_file_reads_with_skill_style -q
```

## 自检问题

- `/skill:name` 最终变成什么 prompt?
- 如何判断一次 read 是 skill read?
- 为什么 skill 展示逻辑不能改变 tool result?
- 自动 skill availability 和手动 invocation 有什么区别?
