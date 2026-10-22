# AGROVISION AI - API Registry

| API Name | Official Website | Purpose | Authentication | API Key Required? | Free-Tier Limitation | Endpoint | Data Fields Used | Cache Duration | Fallback Behavior | Terms/Attribution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo API** | https://open-meteo.com/ | Weather and forecasting data | None | No | 10,000 requests/day | `https://api.open-meteo.com/v1/forecast` | Temperature, rainfall, humidity | 1 Hour | Display "Weather info unavailable" | CC-BY 4.0; must attribute |
| **AGMARKNET / data.gov.in** | https://data.gov.in/ | Published Indian mandi commodity prices | Server-side `DATA_GOV_IN_API_KEY` | Yes | Dependent on portal limits | `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070` | State, District, Market, Commodity, Variety, Arrival Date, Min/Max/Modal Price (source unit) | No application cache; display the source arrival date | Attribute AGMARKNET/data.gov.in and follow the portal's current API and OGD terms |

The market integration is opt-in and returns published observations, not real-time prices. Register for an API key on data.gov.in, then set `DATA_GOV_IN_API_KEY` in the backend/Render environment; never add it to Vite variables or source control. The official API endpoint could not be verified from this network during implementation (HTTP 403), so configure and verify the provider key before representing the integration as live.
| **Supabase** | https://supabase.com/ | Database, Auth, Realtime | API Key | Yes | 500MB DB, 1GB Storage, 50K MAU | `<supabase-url>/rest/v1/...` | Tables, Users | N/A | Offline local cache (IndexedDB) | Standard Supabase ToS |
| **Groq (Optional LLM)** | https://console.groq.com/ | AI Assistant / RAG | API Key | Yes | Generous free tier for developers | `https://api.groq.com/openai/v1/chat/completions` | Prompt, Completion | N/A | Fallback to local KB | Standard Groq ToS |

*Note: No secret keys are stored in source code. See `.env.example` for required environment variables.*
