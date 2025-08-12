#!/usr/bin/env python3
import os, sys, time, datetime

from typing import Dict, Any, List

import requests
from dotenv import load_dotenv
from openai import OpenAI
from prompts import FILL_CARD_BACK_PROMPT
from cachetools import TTLCache

load_dotenv()

ANKI_BASE_URL = "http://127.0.0.1:8765"
LLM_CACHE_TTL = 600
LLM_CACHE = TTLCache(maxsize=4096, ttl=LLM_CACHE_TTL)


def anki(action, **params):
    r = requests.post(
        ANKI_BASE_URL, json={"action": action, "version": 6, "params": params}
    )
    r.raise_for_status()
    j = r.json()
    if j.get("error"):
        raise RuntimeError(j["error"])
    return j["result"]


def chunked(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Put it in your .env")
    base = os.getenv("OPENAI_API_BASE")
    if base:
        return OpenAI(api_key=api_key, base_url=base)
    return OpenAI(api_key=api_key)


def generate_fields_via_llm(client: OpenAI, word: str, model: str) -> str:
    if word in LLM_CACHE:
        print(f"[CACHE] hit: {word}")
        return LLM_CACHE[word]

    system = FILL_CARD_BACK_PROMPT
    user = f"{word}".strip()

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", model),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    txt = resp.choices[0].message.content
    if txt:
        LLM_CACHE[word] = txt
    return txt or ""


def main():
    TARGET_DECKS = ["Wynn's TOEIC Vocab"]
    BATCH_SIZE = 1000
    FRONT_FIELD = os.getenv("FRONT_FIELD", "Front")
    BACK_FIELD = os.getenv("BACK_FIELD", "Back")

    client = get_llm_client()
    model_hint = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    note_ids = []
    for deck in TARGET_DECKS:
        note_ids.extend(anki("findNotes", query=f'deck:"{deck}"'))

    targets: List[Dict[str, Any]] = []
    for batch in chunked(note_ids, BATCH_SIZE):
        notes = anki("notesInfo", notes=batch)
        for n in notes:
            fields = n.get("fields", {})
            front_val = (fields.get(FRONT_FIELD, {}).get("value") or "").strip()
            target_val = (fields.get(BACK_FIELD, {}).get("value") or "").strip()
            if not front_val:
                continue
            if target_val:
                continue
            targets.append({"id": n["noteId"], "front": front_val, "fields": fields})

    print(f"Found {len(targets)} notes in decks '{', '.join(TARGET_DECKS)}'.")

    updated = 0
    for t in targets:
        word = t["front"]
        print("[LLM] Generating for ", word)
        ret_txt = generate_fields_via_llm(client, word, model_hint)
        print("[LLM] Generated: ", ret_txt)

        update_fields = {
            BACK_FIELD: ret_txt.replace("\n", "<br>"),
        }

        if not update_fields:
            continue

        anki("updateNoteFields", note={"id": t["id"], "fields": update_fields})
        updated += 1

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Updated {updated} notes.")
    return 0


if __name__ == "__main__":
    MINIMUM_DELAY = 5
    try:
        while True:
            main()
            time.sleep(MINIMUM_DELAY)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
