# Phase 18: Provider Configuration Foundation

Source: [dev-notes/architecture/phase-18-provider-config-foundation.md](../../dev-notes/architecture/phase-18-provider-config-foundation.md)

这一 phase 把 provider 配置从环境变量扩展成可保存、可列出、可选择的配置系统。

## 要抓住的主线

Provider config 解决这些问题：

- 默认 provider 是谁。
- 每个 provider 有哪些模型。
- API key 来自环境变量还是本地 credential store。
- base URL、headers、timeout、retry 怎么配。
- CLI/TUI 如何切换 provider/model。

## 源码阅读路线

读：

- [src/tau_coding/provider_config.py](../../src/tau_coding/provider_config.py)
- [src/tau_coding/provider_runtime.py](../../src/tau_coding/provider_runtime.py)
- [src/tau_coding/credentials.py](../../src/tau_coding/credentials.py)
- [src/tau_coding/cli.py](../../src/tau_coding/cli.py)

## 关键理解

`tau_ai` 提供 provider 实现，`tau_coding` 决定如何从配置创建 provider runtime。

配置系统属于应用层，因为它知道用户文件、credential store、CLI setup 命令、TUI picker。

## 测试入口

```bash
uv run pytest tests/test_provider_config.py tests/test_provider_runtime.py tests/test_credentials.py -q
```

## 自检问题

- provider implementation 和 provider configuration 有什么区别?
- credential 优先级如何理解?
- 为什么配置文件不能由 `tau_ai` 自己管理?
- CLI `/model` 和 provider config 之间是什么关系?
