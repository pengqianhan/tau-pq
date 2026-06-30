# Phase 6: Non-interactive Print-mode CLI

Source: [dev-notes/architecture/phase-6-print-mode-cli.md](../../dev-notes/architecture/phase-6-print-mode-cli.md)

这一 phase 把前面的 provider、harness、coding tools 拼成一个最小 CLI。

## 要抓住的主线

Print-mode CLI 是最早的真实前端。它还不是 TUI，只做一件事：

```text
用户传 prompt -> session/harness 跑 agent -> renderer 打印最终结果
```

它证明了核心 agent 层可以被应用层调用。

## 源码阅读路线

读 [src/tau_coding/cli.py](../../src/tau_coding/cli.py)。

重点看：

- Typer app 如何定义命令。
- `run_print_mode`
- provider 如何传入。
- coding tools 如何创建。
- system prompt 如何组装。

这里先不要深挖 provider config，Phase 18 会系统处理。

## 关键理解

CLI 不是 agent brain。CLI 只是前端之一。

核心形状和教程示例一样：

```python
async for event in session.prompt(prompt):
    renderer.render(event)
```

Phase 6 的 renderer 还比较简单，后面 Phase 11 会扩展成 text/json/transcript。

## 测试入口

```bash
uv run pytest tests/test_cli.py::test_version_command \
              tests/test_cli.py::test_run_print_mode_prints_final_assistant_text -q
```

## 自检问题

- `tau_agent` 是否知道 Typer?
- CLI 是如何拿到工具列表的?
- 为什么 print mode 应该先于 Textual TUI?
- 为什么测试里仍然用 `FakeProvider`?
