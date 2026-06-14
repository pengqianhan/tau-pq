# Tau

Tau is a Python implementation of Pi's minimalist coding-agent harness architecture.

The project is intentionally built in small, documented phases. Each phase adds one layer to the system while keeping the core agent harness independent from the coding-agent app and from any terminal UI framework.

## Architecture at a glance

```text
tau_ai       provider/model streaming layer
tau_agent    portable agent harness, loop, tools, events, sessions
tau_coding   CLI app, resources, skills, extensions, commands, UI integration
```

The key design boundary is:

```text
AgentHarness = reusable brain
AgentSession = coding-agent environment
TUI = one possible frontend
```

## Current status

Tau currently has:

- project/package foundation
- development tooling
- a basic `tau --version` CLI
- provider-neutral message, tool, result, and event models
- beginner-friendly design documentation

## Where to start

- New to the project? Read [Getting Started](getting-started.md).
- Want the full plan? Read the [Roadmap](00-roadmap.md).
- Want the big-picture boundaries? Read [Architecture](01-architecture.md).
- Want the current core model? Read [Core Types and Events](05-core-types-and-events.md).
