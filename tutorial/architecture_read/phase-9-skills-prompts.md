# Phase 9: Skills and Prompt Templates

Source: [dev-notes/architecture/phase-9-skills-prompts.md](../../dev-notes/architecture/phase-9-skills-prompts.md)

这一 phase 引入本地资源：skills 和 prompt templates。

## 要抓住的主线

Skills 和 prompt templates 都是 coding app 层的资源，不属于 agent brain。

- Skill: 一段可被系统提示词索引、必要时可被 agent 读取的能力说明。
- Prompt template: 用户可通过 slash-style 命令展开的提示词模板。

## 源码阅读路线

读：

- [src/tau_coding/resources.py](../../src/tau_coding/resources.py)
- [src/tau_coding/skills.py](../../src/tau_coding/skills.py)
- [src/tau_coding/prompt_templates.py](../../src/tau_coding/prompt_templates.py)

再回到 [src/tau_coding/session.py](../../src/tau_coding/session.py)，看 session 如何加载这些资源。

## 关键理解

Skill invocation 不等于提前把所有 skill 内容塞进上下文。更合理的方式是把 skill index 放进 system prompt，agent 需要时再用 `read` 工具读取具体 skill 文件。

Prompt template 更像用户命令展开，它在 prompt 进入 agent 之前改写用户输入。

## 测试入口

```bash
uv run pytest tests/test_skills.py tests/test_prompt_templates.py -q
```

## 自检问题

- Skill 和 prompt template 的区别是什么?
- 为什么资源发现属于 `tau_coding`?
- Skill index 为什么比直接塞完整 skill 更可控?
- Prompt template 展开是在 agent loop 之前还是之后?
