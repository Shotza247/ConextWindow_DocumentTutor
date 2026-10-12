"""Terminal chat. Run:  python main.py --source file.pdf https://example.com"""
from __future__ import annotations

import argparse

from qa_tutor.config import DEFAULT_MODEL, Settings
from qa_tutor.tutor import Tutor

HELP = "Commands: /start (guided walkthrough), /next, /outline, /exit. Anything else is a question."


def print_overview(analysis: dict) -> None:
    print(f"\n{analysis['title']} ({analysis['difficulty']})")
    print(analysis["summary"])
    print("\nLesson outline:")
    for number, step in enumerate(analysis["lesson_outline"], start=1):
        print(f"  {number}. {step['title']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with your documents.")
    parser.add_argument("--source", "-s", nargs="+", required=True, help="PDF/TXT/MD paths or web links.")
    parser.add_argument("--question", "-q", help="Ask one question and exit.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--refresh-cache", action="store_true", help="Redo everything from scratch.")
    args = parser.parse_args()

    tutor = Tutor(Settings(model=args.model, refresh_cache=args.refresh_cache))
    print("Reading and studying your material...")
    analysis = tutor.load(args.source)

    if args.question:
        print(tutor.ask(args.question))
        return

    print_overview(analysis)
    print(f"\n{HELP}")
    while True:
        text = input("\n> ").strip()
        if text.lower() in {"/exit", "exit", "quit", "q"}:
            break
        if text == "/outline":
            print_overview(analysis)
        elif text == "/start":
            print(f"\n{tutor.start_walkthrough()}")
        elif text == "/next":
            print(f"\n{tutor.next_step()}")
        elif text:
            print(f"\n{tutor.ask(text)}")
