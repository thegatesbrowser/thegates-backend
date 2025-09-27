import os
import json
import hashlib
import requests
from typing import Tuple, List


webhook_url = open('keys/discord_webhook.key', 'r').read()


def _load_personas_from_json() -> Tuple[List[str], List[str], List[str]]:
    path = os.path.join(os.path.dirname(__file__), "personas.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    adjectives = list(data.get("adjectives") or [])
    animals = list(data.get("animals") or [])
    emojis = list(data.get("emojis") or [])
    return adjectives, animals, emojis


_ADJECTIVES, _ANIMALS, _AVATAR_EMOJIS = _load_personas_from_json()


def _stable_hash_int(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def generate_stable_nickname(user_id: str) -> str:
    base = str(user_id)
    h = _stable_hash_int(base)
    adj = _ADJECTIVES[h % len(_ADJECTIVES)]
    animal = _ANIMALS[(h // 7) % len(_ANIMALS)]
    return f"{adj}{animal}"


def get_avatar_emoji(user_id: str) -> str:
    h = _stable_hash_int(str(user_id))
    return _AVATAR_EMOJIS[h % len(_AVATAR_EMOJIS)]


def _format_visit_text(user_visit_count: int) -> str:
    count = user_visit_count
    if count <= 1:
        return "✨ First visit — welcome!"
    if count == 2:
        return "🔁 Back again — second visit!"
    return f"🔁 They've visited {count} times!"


def _compose_message(
    nickname: str,
    avatar: str,
    country: str,
    user_visit_count: int,
    total_visitors: int,
) -> str:
    line1 = f"{avatar} {nickname} ({country}) just stepped through TheGates"
    line2 = _format_visit_text(user_visit_count)
    line3 = f"🌍 Total visitors today: {total_visitors}"

    parts = [line1, line2, line3]
    return "\n".join(parts)


def notify_application_open(data) -> None:
    user_id = data["user_id"]
    city = data["city"]
    country = data["country"]

    nickname = generate_stable_nickname(str(user_id))
    avatar = get_avatar_emoji(str(user_id))

    content = _compose_message(
        nickname=nickname,
        avatar=avatar,
        city=city,
        country=country,
        user_visit_count=data["user_visit_count"],
        total_visitors=data["total_visitors"],
    )

    response = requests.post(webhook_url, json={"content": content}, timeout=6)
    if response.status_code in (200, 204):
        print("Discord message sent.")
    else:
        print(f"Failed to send Discord message: {response.status_code} {response.text}")
