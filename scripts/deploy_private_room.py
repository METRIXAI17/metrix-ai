"""
Mint + deploy a private client room into pilot_private/deployed_rooms/{slug}/.

Usage:
  py -3 scripts/deploy_private_room.py --name "Client Co" --industry ai-agencies --lang ru
  py -3 scripts/deploy_private_room.py --name "Acme" --base-url http://127.0.0.1:8790

Prints unique link + password. Folder is gitignored via pilot_private/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pilot_private.private_rooms import DEPLOY_MIRROR, PrivateRoomRegistry


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy private Metrix room")
    ap.add_argument("--name", default="Client")
    ap.add_argument("--industry", default="ai-agencies")
    ap.add_argument("--contact", default="")
    ap.add_argument("--lang", default="ru")
    ap.add_argument("--base-url", default="http://127.0.0.1:8790")
    ap.add_argument("--preview", default="")
    args = ap.parse_args()

    reg = PrivateRoomRegistry()
    room = reg.mint(
        client_name=args.name,
        industry=args.industry,
        contact=args.contact,
        lang=args.lang,
        business_preview=args.preview,
        base_url=args.base_url,
    )
    slug = room["slug"]
    folder = DEPLOY_MIRROR / slug
    print("=== PRIVATE ROOM DEPLOYED ===")
    print(f"Folder: {folder}")
    print(f"Unique link: {room['unique_url']}")
    print(f"Password:    {room['password']}")
    print(f"Return path: {room['return_url']}")
    print()
    print("--- Message for client (RU) ---")
    print(room["message_for_client_ru"])
    print()
    # also write OPERATOR.txt
    op = folder / "OPERATOR.txt"
    op.write_text(
        f"UNIQUE LINK: {room['unique_url']}\n"
        f"PASSWORD: {room['password']}\n"
        f"RETURN: {args.base_url.rstrip('/')}{room['return_url']}\n"
        f"SLUG: {slug}\n",
        encoding="utf-8",
    )
    print(f"Credentials file: {folder / 'CREDENTIALS.json'}")
    print(f"Operator file:    {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
