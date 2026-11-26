# Screen Reply Agent

A lightweight, fork-and-run Python API and CLI that turns screenshot text from **any** messaging or dating app (Hinge, Tinder, iMessage, WhatsApp) into 3 short, natural replies using **any** OpenAI-compatible LLM—including [Google Gemini's free tier](https://klymentiev.com/blog/gemini-api-free-tier), [xAI Grok](https://x.ai/api), OpenAI, or local Ollama.

Because it only reads text you pass to it and never touches app UIs, it stays compliant with [Hinge's automated-tools policy](https://help.hinge.co/hc/en-us/articles/49657802257683-Note-on-Third-Party-Automated-Tools) and works safely alongside an iPhone Shortcut.

## Fork & Run in 60 Seconds

1. **Fork and clone** this repo, then install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Pick your model** by copying `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your API key (for a $0 setup with no credit card, grab a free Gemini key at [Google AI Studio](https://aistudio.google.com/docs/models)).

3. **Run the CLI or API server:**
   ```bash
   # Quick CLI test
   python main.py --text "Two truths and a lie: I've been to 14 countries, I hate coffee, I can juggle." --style playful

   # Start the API server
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   Or run with Docker:
   ```bash
   docker build -t screen-reply-agent .
   docker run --env-file .env -p 8000:8000 screen-reply-agent
   ```

## Pair with an iPhone Shortcut (1-Tap Back Tap)

1. In Apple **Shortcuts**, add **Take Screenshot** -> **Extract Text from Image**.
2. Add **Get Contents of URL** pointing to `http://<your-server-url>/reply` (method: **POST**, JSON body: `text` = *Text from Image*, `style` = `playful`).
3. Add **Get Dictionary Value** for `text_block` -> **Split Text** (New Lines) -> **Choose from List** -> **Copy to Clipboard**.
4. Bind the shortcut to **Settings > Accessibility > Touch > [Back Tap](https://support.apple.com/guide/iphone/back-tap-iphaa57e7885/ios) > Double Tap**.

## Pair with Android (MacroDroid or Tasker)

You can trigger the same `/reply` endpoint on Android with a floating button using **MacroDroid** (free on Google Play) or **Tasker**:

1. **Trigger:** Add a **Floating Button** (or Quick Settings tile) so you can trigger it over any app.
2. **Read screen:** Add **UI Interaction → Read Screen Contents** and save it to a text variable (for example, `screen_text`).
3. **Call the API:** Add **HTTP Request** set to **POST** `http://<your-server-url>/reply` with header `Content-Type: application/json` and body:
   ```json
   {"text": "{lv=screen_text}", "style": "playful"}

## Customize Tone & Prompts

Edit `prompts.yaml` to tweak the built-in styles (`playful`, `curious`, `direct`) or add your own—no Python edits needed.

## License

MIT — see [LICENSE](LICENSE).
