
import subprocess
import re
from assistant import ask_jarvis


def speak(text):
    if not text:
        return

    has_marathi = bool(
        re.search(r'[\u0900-\u097F]', text)
    )

    language = "mr" if has_marathi else "en"
    country = "IN" if has_marathi else "US"

    try:
        subprocess.run(
            [
                "termux-tts-speak",
                "-l", language,
                "-n", country,
                text
            ],
            check=True,
            timeout=120
        )
    except Exception as error:
        print("TTS Error:", error)


def listen():
    print("\n🎤 JARVIS: Listening...")

    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print("Speech Error:", result.stderr)
            return ""

        return result.stdout.strip()

    except Exception as error:
        print("Microphone Error:", error)
        return ""


def main():

    print("""
==================================
       JARVIS VOICE ASSISTANT
==================================
AI       : GEMINI
INPUT    : MICROPHONE
OUTPUT   : ANDROID TTS
LANGUAGE : MARATHI + ENGLISH
==================================
""")

    speak("नमस्कार बॉस! मी हॅप्पी आहे. तुमच्या मदतीसाठी तयार आहे.")

    while True:
        try:
            message = listen()

            if not message:
                continue

            print("\nBOSS:", message)

            if message.lower() in [
                "exit", "quit", "stop", "बंद कर"
            ]:
                speak("ठीक आहे बॉस, पुन्हा भेटू.")
                break

            print("\nJARVIS: विचार करत आहे...")

            answer = ask_jarvis(message)

            if answer:
                speak(answer)

        except KeyboardInterrupt:
            print("\nJARVIS बंद झाला.")
            break


if __name__ == "__main__":
    main()

