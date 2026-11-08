import os
import requests

BASE = None
API_KEY = None

MODEL = "gemini-2.5-flash"


def initialize(user_data_dir):
    global BASE, API_KEY

    BASE = user_data_dir
    os.makedirs(BASE, exist_ok=True)

    key_file = os.path.join(BASE, "api_key.txt")

    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            API_KEY = f.read().strip()


def set_api_key(key):
    global API_KEY

    API_KEY = key.strip()

    if BASE:
        key_file = os.path.join(BASE, "api_key.txt")

        with open(key_file, "w") as f:
            f.write(API_KEY)


def ask_jarvis(message):

    if not API_KEY:
        return "बॉस, आधी Gemini API Key सेट करा."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL + ":generateContent"
    )

    try:
        response = requests.post(
            url,
            params={"key": API_KEY},
            json={
                "system_instruction": {
                    "parts": [{
                        "text": "तुझे नाव हॅप्पी आहे. "
                        "तू माझा वैयक्तिक सहाय्यक आहेस. "
                        "नेहमी सोप्या मराठी भाषेत उत्तर दे."
                    }]
                },
                "contents": [{
                    "parts": [{"text": message}]
                }]
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as error:
        return "बॉस, काही अडचण आली: " + str(error)
