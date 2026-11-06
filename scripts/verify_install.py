"""Installation verification."""

import sys


def main():
    try:
        import emotions_ai
        from emotions_ai import EmotionAI
        ai = EmotionAI()
        r = ai.chat_sync(user_id="verify", message="hello")
        assert r.text
        print(f"OK: emotions_ai {emotions_ai.__version__}")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())