# autoanki
Runs locally to automatically fill empty Anki cards with definitions, examples, etymology, synonyms, and antonyms using an LLM, so you just add the word and let it do the rest.

<table border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td align="center" valign="middle" width="48%">
      <img src="https://github.com/user-attachments/assets/e0adce45-03a8-44a1-9053-f6f1f874ab2b" width="100%">
    </td>
    <td align="center" valign="middle">
      →
    </td>
    <td align="center" valign="middle" width="48%">
      <img src="https://github.com/user-attachments/assets/706c7d49-db21-4927-8d15-0b4df5878ca5" width="100%">
    </td>
  </tr>
</table>


---


## Prerequisites
- Anki (running) — apps.ankiweb.net
- AnkiConnect add-on (must be installed & enabled)
  - **Method A (recommended): Anki → Tools → Add-ons → Get Add-ons… → paste code: 2055492159 → OK → restart Anki**
  - Method B (manual zip): Download the release zip → Anki → Tools → Add-ons → View Files → copy the unzipped folder into this directory → restart Anki
  - **Verify**: open http://127.0.0.1:8765 in a browser; a small JSON like {"error":"missing action","result":null} means it’s working.
- **Python 3.8+**
- OpenAI-compatible LLM access (OpenAI API or a local compatible server)

---

## Quick Start (macOS)
### Clone the repo
```bash
git clone https://github.com/well-balanced/autoanki.git
cd autoanki
open .
```
### (Recommended) `start.command`
Open Finder and Double-click `start.command`
1. First run will ask for your OPENAI_API_KEY (entered in the terminal).
2. It will also check AnkiConnect availability.
3. Then it starts AutoAnki.

### or Clone the repo and install deps:
```bash
pip install -r requirements.txt
python3 main.py
```

and you need to create a `.env` file and fill like below
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```


---


## What It Does (each cycle)
	1.	Fetches all decks from AnkiConnect.
	2.	Finds notes where **BACK_FIELD is empty.**
	3.	Sends the front (word) to the LLM with your prompt.
	4.	Sleeps for LOOP_DELAY_SECONDS and repeats.


---


## Prompt Customization
The script imports FILL_CARD_BACK_PROMPT from prompts.py.
Provide a concise system prompt that instructs the model to return exactly what your card needs. Example:
```python
# prompts.py
FILL_CARD_BACK_PROMPT = """
You are an English lexicographer. For the user's word, produce a short, study-friendly back text that includes:
- concise definition
- one natural example sentence using the word
- short etymology (or 'unknown')
- up to 6 synonyms and up to 6 antonyms
Return clean plaintext (no markdown). Keep it brief and exam-oriented.
"""
```

---


## How It Works
```
Anki (running) ↔ AnkiConnect (localhost:8765) ←→ AutoAnki (this script) ←→ LLM (OpenAI or local)
```
- AnkiConnect exposes a local HTTP API.
- AutoAnki queries notes with empty BACK_FIELD, calls your LLM, then updates notes via updateNoteFields.


## License
MIT — do whatever you want, attribution appreciated.
