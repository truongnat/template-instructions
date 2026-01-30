import argparse
import sys
import os

# Ensure we can import from local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

try:
    from agentic_sdlc.infrastructure.bridge.communication.chat_manager import ChatManager
except ImportError:
    # Try relative import if running directly from directory
    sys.path.append(os.path.dirname(current_dir))
    from communication.chat_manager import ChatManager

def main():
    parser = argparse.ArgumentParser(description="Role Communication CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Send message
    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--channel", required=True)
    send_parser.add_argument("--thread", required=True)
    send_parser.add_argument("--role", required=True)
    send_parser.add_argument("--content", required=True)

    # List channels
    subparsers.add_parser("channels")

    # List threads
    thread_parser = subparsers.add_parser("threads")
    thread_parser.add_argument("--channel", required=True)

    # Get history
    hist_parser = subparsers.add_parser("history")
    hist_parser.add_argument("--channel", required=True)
    hist_parser.add_argument("--thread") # Optional
    hist_parser.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    cm = ChatManager()

    if args.command == "send":
        cm.send_message(args.channel, args.thread, args.role, args.content)
        print("Message sent.")
    elif args.command == "channels":
        channels = cm.list_channels()
        for c in channels:
            print(f"- {c['name']}: {c['description']}")
    elif args.command == "threads":
        threads = cm.list_threads(args.channel)
        for t in threads:
            print(f"- {t['title']}")
    elif args.command == "history":
        msgs = cm.get_history(args.channel, args.thread, args.limit)
        for m in msgs:
            print(f"[{m['timestamp']}] {m['role_id']} (in {m['thread_title']}): {m['content']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
