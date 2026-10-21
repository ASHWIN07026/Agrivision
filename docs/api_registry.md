# AGROVISION AI - API Registry

| API Name | Official Website | Purpose | Authentication | API Key Required? | Free-Tier Limitation | Endpoint | Data Fields Used | Cache Duration | Fallback Behavior | Terms/Attribution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo API** | https://open-meteo.com/ | Weather and forecasting data | None | No | 10,000 requests/day | `https://api.open-meteo.com/v1/forecast` | Temperature, rainfall, humidity | 1 Hour | Display "Weather info unavailable" | CC-BY 4.0; must attribute |
| **AGMARKNET / data.gov.in** | https://data.gov.in/ | Market Intelligence & Crop Prices | API Key (data.gov.in) | Yes (for data.gov.in) | Dependent on portal limits | `https://api.data.gov.in/resource/...` | State, District, Market, Commodity, Min Price, Max Price, Modal Price | 24 Hours | Show cached market data | Acknowledge OGD Platform India |
| **Supabase** | https://supabase.com/ | Database, Auth, Realtime | API Key | Yes | 500MB DB, 1GB Storage, 50K MAU | `<supabase-url>/rest/v1/...` | Tables, Users | N/A | Offline local cache (IndexedDB) | Standard Supabase ToS |
| **Groq (Optional LLM)** | https://console.groq.com/ | AI Assistant / RAG | API Key | Yes | Generous free tier for developers | `https://api.groq.com/openai/v1/chat/completions` | Prompt, Completion | N/A | Fallback to local KB | Standard Groq ToS |

*Note: No secret keys are stored in source code. See `.env.example` for required environment variables.*
