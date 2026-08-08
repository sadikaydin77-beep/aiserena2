import os
import requests

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

PROMPT = """You are a jewelry market analyst for AiSerena, a luxury jewelry brand.

Research today's current US jewelry market trends and any active marketing
campaigns from major/notable jewelry brands (e.g. seasonal pushes, viral
styles, notable discounts or launches). Use this to propose ONE realistic,
sellable jewelry piece AiSerena could produce and post about today.

Reply in English. Keep it short and scannable, structured exactly like this:

📈 TREND SUMMARY
(2-3 sentences - today's standout trend(s) and any active campaign examples, naming source brands)

💎 PRODUCT SUGGESTION
(One concrete product suggestion: type, stone/material, style - 2-3 sentences, explain why it fits today)

🎨 GEMINI IMAGE PROMPT
(A single ready-to-use image generation prompt, 40-80 words, that I can paste directly into Gemini to generate a photorealistic product photo of this exact piece. Include: the specific jewelry item, materials/stones/colors, camera/lens style, lighting, background/surface, and explicitly state ONE single jewelry piece only, no people, no hands, no multiple items, photorealistic, ultra-detailed, 8K product photography. Write it as one continuous paragraph, no line breaks.)

Do not include hashtags or social media captions - only these three sections."""


def get_report():
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-5",
            "max_tokens": 800,
            "messages": [{"role": "user", "content": PROMPT}],
            "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        },
        timeout=120,
    )
    data = r.json()
    if "content" not in data:
        raise Exception(f"Claude error: {data}")
    # Concatenate all text blocks (web search produces multiple content blocks)
    text_parts = [block["text"] for block in data["content"] if block.get("type") == "text"]
    return "\n".join(text_parts).strip()


def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🗓️ Daily AiSerena Trend Report\n\n{text}"},
    )
    print(f"Telegram response: {r.status_code} - {r.text}")


if __name__ == "__main__":
    report = get_report()
    send_telegram(report)
