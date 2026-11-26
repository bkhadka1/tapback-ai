import argparse
import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_PATH = BASE_DIR / "prompts.yaml"


def load_prompts() -> dict:
    with PROMPTS_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY is not set. Copy .env.example to .env and add your key.")
    base_url = os.getenv("LLM_BASE_URL") or None
    return OpenAI(api_key=api_key, base_url=base_url)


def generate_replies(text: str, style: Optional[str] = None, count: int = 3) -> list[str]:
    prompts = load_prompts()
    styles = prompts.get("styles", {})
    chosen_style = style or prompts.get("default_style", "playful")
    if chosen_style not in styles:
        raise ValueError(f"Unknown style '{chosen_style}'. Available: {', '.join(styles.keys())}")

    system_prompt = styles[chosen_style]["system"].format(count=count)
    model = os.getenv("LLM_MODEL", "gemini-3.8-flash")

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Profile or chat text:\n{text.strip()}"},
        ],
        temperature=0.8,
    )

    raw = response.choices[0].message.content or ""
    lines = [line.strip().strip('"').strip("'") for line in raw.splitlines() if line.strip()]
    return lines[:count]


app = FastAPI(title="Model-Agnostic Reply Agent", version="0.1.0")


class ReplyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="OCR text from a profile or chat screenshot")
    style: Optional[str] = Field(default=None, description="Prompt style key from prompts.yaml")
    count: int = Field(default=3, ge=1, le=5)


class ReplyResponse(BaseModel):
    model: str
    style: str
    replies: list[str]
    text_block: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "gemini-3.8-flash")}


@app.post("/reply", response_model=ReplyResponse)
def reply_endpoint(payload: ReplyRequest) -> ReplyResponse:
    prompts = load_prompts()
    chosen_style = payload.style or prompts.get("default_style", "playful")
    try:
        replies = generate_replies(payload.text, style=chosen_style, count=payload.count)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ReplyResponse(
        model=os.getenv("LLM_MODEL", "gemini-3.8-flash"),
        style=chosen_style,
        replies=replies,
        text_block="\n".join(replies),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate natural dating-app replies using any OpenAI-compatible LLM.")
    parser.add_argument("--text", required=True, help="Profile prompt or chat text")
    parser.add_argument("--style", default=None, help="Style preset from prompts.yaml")
    parser.add_argument("--count", type=int, default=3, help="Number of replies to generate")
    args = parser.parse_args()

    for item in generate_replies(args.text, style=args.style, count=args.count):
        print(item)
