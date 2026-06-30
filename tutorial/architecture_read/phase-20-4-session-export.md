# Phase 20.4: Session Export and Visualization

Source: [dev-notes/architecture/phase-20-4-session-export.md](../../dev-notes/architecture/phase-20-4-session-export.md)

这一 phase 加入 session 导出和可视化。

## 要抓住的主线

Session JSONL 对机器友好，但不适合人直接读。Export 负责把 session tree 转成 HTML 或 JSONL 输出。

导出要保留：

- message 内容。
- branch tree。
- tool result。
- compaction / branch summary。
- 原始 session 路径和 metadata。

## 源码阅读路线

读：

- [src/tau_coding/session_export.py](../../src/tau_coding/session_export.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)
- [src/tau_coding/cli.py](../../src/tau_coding/cli.py)

## 关键理解

Export 是读取 session entry 的投影，不应该改 session。HTML 是展示格式，JSONL 是可搬运格式。

## 测试入口

```bash
uv run pytest tests/test_session_export.py \
              tests/test_cli.py::test_export_session_command_writes_html_for_jsonl_path -q
```

## 自检问题

- 导出和 resume 的区别是什么?
- HTML export 为什么要保留 branch tree?
- 导出应该读取 active leaf 还是整个 session tree?
- Export 失败时应该影响原始 session 吗?
