# Providers

Tau's provider layer lives in `tau_ai`.

Providers translate external model APIs into Tau's provider-neutral event stream.

## OpenAI-compatible provider

Tau currently includes an OpenAI-compatible chat completions adapter.

Set:

```bash
export OPENAI_API_KEY="..."
```

Optionally set a custom compatible endpoint:

```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

The provider uses `/chat/completions` with streaming enabled.

## Fake provider

Tau also includes `FakeProvider` for deterministic tests. It replays scripted provider events and never makes network requests.

This will be used heavily by the agent-loop tests in the next phase.
