
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE = os.path.expanduser("~/jarvis")
DB = os.path.join(BASE, "memory", "jarvis.db")

load_dotenv(os.path.join(BASE, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

if not API_KEY or not MODEL:
    raise SystemExit("API Key or Model missing in .env")

client = genai.Client(api_key=API_KEY)

os.makedirs(os.path.dirname(DB), exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    assistant TEXT,
    created_at TEXT
)
""")
conn.commit()


SYSTEM_PROMPT = """
तुझे नाव हॅप्पी आहे.
तू माझा वैयक्तिक कृत्रिम बुद्धिमत्ता सहाय्यक आहेस.

भाषेसंबंधी अत्यंत महत्त्वाचे नियम:

1. प्रत्येक उत्तर फक्त मराठी भाषेत दे.
2. देवनागरी लिपीमध्येच लिही.
3. इंग्रजी भाषेत उत्तर देऊ नकोस.
4. शक्यतो इंग्रजी शब्द वापरू नकोस.
5. तांत्रिक शब्दांसाठी सोपे मराठी पर्याय वापर.
6. कोड आवश्यक असेल तेव्हाच इंग्रजीमध्ये दे.
7. उत्तर नैसर्गिक, स्पष्ट आणि बोलण्यास योग्य ठेव.
8. मला नेहमी बॉस म्हणून संबोध.

तुझी कामे:
- प्रश्नांची उत्तरे देणे.
- तांत्रिक समस्या सोडवणे.
- प्रोग्रामिंगमध्ये मदत करणे.
- नवीन कल्पना सुचवणे.
- मोबाईल वापरण्यास मदत करणे.

तू नेहमी मराठीतच संवाद साध.
"""


def get_history(limit=10):
    cur.execute("""
        SELECT user, assistant
        FROM conversations
        ORDER BY id DESC LIMIT ?
    """, (limit,))

    rows = cur.fetchall()[::-1]
    history = []

    for user, assistant in rows:
        history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user)]
            )
        )
        history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=assistant)]
            )
        )

    return history


def save_chat(user, answer):
    cur.execute("""
        INSERT INTO conversations
        (user, assistant, created_at)
        VALUES (?, ?, ?)
    """, (user, answer, datetime.now().isoformat()))

    conn.commit()

def ask_jarvis(message):
    history = get_history()

    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
    )

    print("\nJARVIS: ", end="", flush=True)

    answer = ""

    try:
        response = client.models.generate_content_stream(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1200,
                temperature=0.7
            )
        )

        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                answer += chunk.text

        print()

        if answer.strip():
            save_chat(message, answer)

        return answer

    except Exception as error:
        print("\nJARVIS ERROR:", str(error))
        return "Sorry Boss, connection problem."


def main():
    print("""
====================================
          JARVIS AI
====================================
ENGINE  : GOOGLE GEMINI
MODE    : ONLINE
MEMORY  : ENABLED
STATUS  : READY

Type exit to quit.
====================================
""")

    while True:
        try:
            message = input("\nBoss: ").strip()

            if not message:
                continue

            if message.lower() in ["exit", "quit", "bye"]:
                print("JARVIS: Goodbye Boss!")
                break

            ask_jarvis(message)

        except KeyboardInterrupt:
            print("\nJARVIS stopped.")
            break

    conn.close()


if __name__ == "__main__":
    main()
