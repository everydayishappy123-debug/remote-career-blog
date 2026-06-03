#!/usr/bin/env python3
"""
generate_post.py
Anthropic Batch API で記事を生成して Hugo の Markdown ファイルとして保存する。
GitHub Actions から毎日呼び出される。
"""

import anthropic
import json
import time
import re
import random
from datetime import datetime
from pathlib import Path

# ── 設定 ──────────────────────────────────────────────
CONTENT_DIR = Path("content/posts")
MODEL = "claude-sonnet-4-20250514"

TOPICS = [
    ("Remote Job Trends",        ["remote work", "job search", "career", "2025"]),
    ("Salary Negotiation",       ["salary", "negotiation", "remote", "career growth"]),
    ("Japan Digital Nomad Visa", ["japan", "visa", "digital nomad", "overseas job"]),
    ("Resume for Global Jobs",   ["resume", "cv", "global company", "job application"]),
    ("Remote Interview Tips",    ["interview", "remote work", "job search", "career"]),
    ("Work From Abroad Guide",   ["work abroad", "remote job", "expat", "career"]),
    ("Top Remote Job Boards",    ["job board", "remote work", "job search", "hiring"]),
]

SYSTEM_PROMPT = """You are a professional blog writer for RemoteCareer AI,
a blog helping English speakers find remote work and overseas jobs.
Write engaging, informative, SEO-optimized articles.
Always respond in valid JSON only — no markdown fences, no preamble."""

def build_user_prompt(topic: str, keywords: list[str]) -> str:
    kw = ", ".join(keywords)
    return f"""Write a blog article about: "{topic}"

Return ONLY this JSON structure:
{{
  "title": "compelling SEO title (max 60 chars)",
  "description": "meta description (max 155 chars)",
  "body": "full article in markdown (400-500 words, use ## subheadings and bullet points)",
  "tags": ["tag1", "tag2", "tag3"]
}}

Target keywords: {kw}
"""

def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60]

def save_post(data: dict, date_str: str) -> Path:
    slug = slugify(data["title"])
    filename = CONTENT_DIR / f"{date_str}-{slug}.md"
    tags_yaml = "\n".join(f'  - "{t}"' for t in data.get("tags", []))
    content = f"""---
title: "{data['title']}"
date: {date_str}
description: "{data['description']}"
tags:
{tags_yaml}
draft: false
---

{data['body']}
"""
    filename.write_text(content, encoding="utf-8")
    print(f"  saved → {filename.name}")
    return filename

def run():
    client = anthropic.Anthropic()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # 今日のトピックをランダムに選ぶ（重複を避けるなら DB 管理も可）
    topic, keywords = random.choice(TOPICS)
    print(f"Topic: {topic}")

    # ── Batch API でリクエストを送信 ──────────────────
    batch = client.messages.batches.create(
        requests=[
            {
                "custom_id": "post-001",
                "params": {
                    "model": MODEL,
                    "max_tokens": 1500,
                    "system": SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": build_user_prompt(topic, keywords)}
                    ],
                },
            }
        ]
    )
    print(f"Batch created: {batch.id}")

    # ── 完了待ち（最大 30 分ポーリング）─────────────────
    for attempt in range(60):
        time.sleep(30)
        batch = client.messages.batches.retrieve(batch.id)
        print(f"  [{attempt+1}] status: {batch.processing_status}")
        if batch.processing_status == "ended":
            break
    else:
        raise TimeoutError("Batch did not complete within 30 minutes.")

    # ── 結果を取得して保存 ────────────────────────────
    for result in client.messages.batches.results(batch.id):
        if result.result.type != "succeeded":
            print(f"  FAILED: {result.result}")
            continue
        raw = result.result.message.content[0].text
        # JSON フェンスが混入した場合の保険
        raw = re.sub(r"^```json\s*", "", raw.strip())
        raw = re.sub(r"```$", "", raw.strip())
        data = json.loads(raw)
        save_post(data, today)

    print("Done.")

if __name__ == "__main__":
    run()
