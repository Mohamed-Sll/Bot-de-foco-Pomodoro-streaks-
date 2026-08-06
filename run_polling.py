"""Run the telegram bot using long polling (development only).

Usage: Activate venv and run from the `focus-bot` folder:

    python run_polling.py

This avoids webhooks and is ideal for local dev.
"""

from bot import build_application


def main() -> None:
    app = build_application()
    app.run_polling()


if __name__ == "__main__":
    main()
