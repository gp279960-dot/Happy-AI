
import subprocess
from assistant import ask_jarvis

def speak(text):
    if not text:
        return

    try:
        subprocess.run(
            [
                "termux-tts-speak",
                "-l", "mr",
                "-n", "IN",
                "-r", "0.85",
                text
            ],
            check=True,
            timeout=120
        )
    except Exception as e:
        print("आवाजाची अडचण:", e)


def listen():
    print("\n🎤 हॅप्पी ऐकत आहे...")

    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.stdout.strip()

    except Exception as e:
        print("मायक्रोफोनची अडचण:", e)
        return ""


def main():

    print("""
================================
          HAPPY AI
================================
AI       : GOOGLE GEMINI
LANGUAGE : MARATHI
VOICE    : ENABLED
STATUS   : READY
================================
""")

    speak("नमस्कार बॉस! मी हॅप्पी आहे. तुमच्या सेवेसाठी तयार आहे.")

    while True:
        try:
            message = listen()

            if not message:
                continue

            print("\nबॉस:", message)

            if message.lower() in [
                "exit", "quit", "stop", "बंद कर"
            ]:
                speak("ठीक आहे बॉस. पुन्हा भेटू.")
                break

            print("\nहॅप्पी विचार करत आहे...")

            answer = ask_jarvis(message)

            if answer:
                speak(answer)

        except KeyboardInterrupt:
            speak("पुन्हा भेटू बॉस.")
            break


if __name__ == "__main__":
    main()
