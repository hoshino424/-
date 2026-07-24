# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Streamlit web app (Japanese UI) where three role-based GPT-4o "agents" debate and produce a travel itinerary, grounded with live data from weather, maps, and search APIs. Everything lives in a single file: `main.py`.

`main.py` runs entirely through Streamlit; there is no FastAPI backend or LangChain usage in this repo.

## Commands

Run the app locally:
```
streamlit run main.py --server.enableCORS false --server.enableXsrfProtection false
```
(This is also what the devcontainer's `postAttachCommand` runs; the app is served on port 8501.)

Install dependencies:
```
pip install -r requirements.txt
```

There are no lint, test, or build scripts in this repo.

### Required environment variables (`.env`, loaded via `python-dotenv`)
- `OPENAI_API_KEY` — GPT-4o calls
- `GOOGLE_MAPS_API_KEY` — `googlemaps` client (place details/opening hours)
- `OPENWEATHER_API_KEY` — current weather lookup
- `SERPER_API_KEY` — Google search via serper.dev (transit status, diverse links, images)

## Architecture (`main.py`)

The app runs a fixed **research → 3-agent debate → refine** pipeline on every button click, driven by `st.session_state` (`final_plan`, `last_plan_a`, `last_plan_b`, `context_info`).

1. **Data-gathering helpers** (each fails soft, returning `None`/an empty/error string on any exception rather than raising):
   - `get_weather_info` / `get_clothing_tip` — OpenWeatherMap → temp/description → clothing advice
   - `search_transit_status`, `search_diverse_links`, `search_web_assets` — Serper.dev search/images endpoints for transit info, official/blog/review links, and images
   - `generate_google_maps_route` — builds a Google Maps directions URL (no API call)
   - `get_place_details_text` — `googlemaps.places`/`place` for opening hours / open-now status

2. **Context assembly** — all of the above results plus sidebar form inputs (date, departure point/time, flight numbers, budget, preferences) are concatenated into one `context_info` string that is passed verbatim as part of the system prompt to every agent call.

3. **Three-agent relay** via `ask_agent(role_prompt, context, user_input)` (one `gpt-4o` chat completion per call, defined in `ROLES`):
   - **Agent A** ("ワクワク担当"/enthusiasm) — proposes a 1–3 hour block itinerary
   - **Agent B** ("現実担当"/reality check) — critiques A's plan against travel time, weather, opening hours
   - **Agent C** ("まとめ担当"/synthesizer) — merges A+B into the final plan, required to open with conditions and close with a link roundup

   Each agent only sees the shared `context_info` plus the previous agent's output — there's no shared conversation history/memory beyond that hand-off.

4. **Refinement loop** — once a `final_plan` exists, `st.chat_input` feedback re-runs the same A→B→C relay (seeded with the previous plan output instead of the original request) and `st.rerun()`s to redisplay.

When modifying agent behavior, prompts live entirely in the `ROLES` dict and the `*_input` f-strings right before each `ask_agent` call — there's no separate prompt-template system.
