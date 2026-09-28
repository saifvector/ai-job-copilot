# AI Model Router & LLM Selection Guide (Phase 15)

## 1. Overview

The **AI Model Router** ([`AIModelRouter`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/orchestration/model_router.py)) dynamically selects the optimal large language model for each agent task based on four constraints:
1. **Task Complexity** (`LOW`, `MEDIUM`, `HIGH`)
2. **Speed / Latency Preference** (`FASTEST`, `BALANCED`, `QUALITY`)
3. **Cost Preference** (`LOWEST_COST`, `STANDARD`, `MAX_ACCURACY`)
4. **Data Privacy Policy** (`CLOUD`, `LOCAL_ONLY`)

---

## 2. Supported Model Catalog

| Model ID | Provider | Latency Tier | Cost Tier | Context Window | Primary Domain Strengths |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`gemini-2.5-pro`** | Google | Moderate (2-3s) | Medium | 1,000,000 | Multi-step reasoning, career auditing, complex tailoring |
| **`gemini-2.5-flash`** | Google | Ultra-Low (<1s) | Low | 1,000,000 | High-throughput parsing, ATS scoring, classification |
| **`gpt-4o`** | OpenAI | Low (1-2s) | High | 128,000 | Conversational interview simulation, code critique |
| **`gpt-4o-mini`** | OpenAI | Ultra-Low (<1s) | Low | 128,000 | High-speed JSON extraction, contact parsing |
| **`claude-3-5-sonnet`**| Anthropic| Low (1-2s) | High | 200,000 | Executive prose, cover letters, recruiter messaging |
| **`nemotron-70b`** | NVIDIA | Moderate (2-4s) | Medium | 128,000 | Structured benchmarks, enterprise candidate reasoning |
| **`ollama-llama3.3`** | Ollama | Low (local) | Free | 32,768 | Air-gapped on-premise parsing, zero data egress |

---

## 3. Dynamic Routing Rules

```
                      [Incoming Agent Task]
                               │
               Is privacy_level == LOCAL_ONLY?
                               ├──► YES ──► Route to on-premise Ollama (Llama 3.3)
                               │
                               ▼ NO
               Is model_override requested?
                               ├──► YES ──► Route to requested explicit model
                               │
                               ▼ NO
               Is complexity == HIGH or cost == MAX_ACCURACY?
                               ├──► YES ──► Route to Gemini 2.5 Pro / Claude 3.5 Sonnet / GPT-4o
                               │
                               ▼ NO
               Is speed_preference == FASTEST or cost == LOWEST_COST?
                               ├──► YES ──► Route to Gemini 2.5 Flash / GPT-4o Mini
                               │
                               ▼ NO
               Standard Balanced Routing ──► Gemini 2.5 Flash (<1s latency, high quality)
```

---

## 4. Fallback Matrix & Availability Guarantees

When third-party API credentials (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `NVIDIA_API_KEY`) are unconfigured in an environment, `AIModelRouter` gracefully routes to the platform's native Google Gemini engine:
* High complexity fallback: `gemini-2.5-pro`
* Standard / high-throughput fallback: `gemini-2.5-flash`
* Air-gapped local fallback: `ollama-llama3.3` / `llama3.1:8b`
