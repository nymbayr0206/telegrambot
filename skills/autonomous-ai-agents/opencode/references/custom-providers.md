# Custom API Providers for Coding Agents

Common OpenAI-compatible providers and configuration notes for use with OpenCode or Codex CLI.

## Provider Quick Reference

### KIE (kie.ai) — Cheapest GPT-5.5 Reseller
- **Base URL:** `https://api.kie.ai/codex/v1`
- **Models:** `gpt-5-5` (standard), `gpt-5-5-thinking`, `gpt-5-5-pro`, `gpt-5-codex`
- **Pricing:** ~$1.425/M input (71.5% off official $5/M), 1 credit ≈ $0.005
- **Signup:** Google/Microsoft account, credit-based (pay-as-you-go)
- **Notes:** Also offers Codex model via kie.ai/codex page. OpenAI Responses API compatible. Credit-based system: $1 = 200 credits.

### OpenRouter
- **Base URL:** `https://openrouter.ai/api/v1`
- **Models:** 300+ models (all providers)
- **Pricing:** List price + ~10-20% markup depending on model
- **Notes:** Supports many providers in one API key. Good for multi-model access.

### Ollama (Local)
- **Base URL:** `http://localhost:11434/v1`
- **Models:** Local open-weight models (Llama, Qwen, DeepSeek, etc.)
- **Pricing:** Free (runs on your hardware)
- **Notes:** No internet needed. Quality depends on hardware. Good for prototyping.

### LiteLLM Proxy
- **Base URL:** Your proxy URL (e.g., `https://litellm.yourcompany.com/v1`)
- **Models:** Any configured backend
- **Pricing:** Whatever you configure
- **Notes:** Best for teams/complex routing. Supports load balancing and spend limits.

## Cost Comparison: Subscription vs Pay-as-you-go

| Usage Level | Codex Plus ($20/mo) | Codex Pro 5x ($100/mo) | KIE GPT-5.5 (PAYG) |
|---|---|---|---|
| Light (~50 sessions/mo) | ✅ Best value | ❌ Overkill | ~$14-28/mo |
| Medium (~150 sessions/mo) | ❌ Hits limits | ✅ Solid | ~$42-84/mo |
| Heavy (~300+ sessions/mo) | ❌ Blocked | ❌ May hit limits | ~$84-168/mo |

**Key tradeoff:** Codex Plus/Pro subscriptions unlock Codex-optimized models (GPT-5-Codex-Mini) that are ONLY available through OpenAI's Codex backend. Custom providers give you general models at potentially lower per-token cost but without those optimizations.

For Hermes Agent (this system), you can configure custom API providers in `~/.hermes/config.yaml` under the `providers` section and use them as `custom:name` in model configs.
