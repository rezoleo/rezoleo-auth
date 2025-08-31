import re

EMAIL_RE = re.compile(
    r"^(?P<first>[a-zA-Z_-]+)\.(?P<last>[a-zA-Z0-9_-]+)@(?P<school>centrale|enscl|iteem|ig2i)\.centralelille\.fr$"
)

NAME_TOKEN_RE = re.compile(r"([a-zA-ZÀ-ÖØ-öø-ÿ]+)")


def parse_school_email(email: str):
    m = EMAIL_RE.match(email.strip())
    if not m:
        raise ValueError("Email invalide. Format attendu: prenom.nom@ecole.centralelille.fr")
    first, last, school = m.group("first"), m.group("last"), m.group("school")
    return first, last, school


def titlecase_name(name: str) -> str:
    # handle hyphens, spaces, apostrophes
    parts = re.split(r"([\- '\u2019])", name.strip())

    def tc(token: str) -> str:
        return token[:1].upper() + token[1:].lower() if token else token

    return ''.join(tc(p) if NAME_TOKEN_RE.match(p) else p for p in parts)


def sanitize_username_base(first: str, last: str) -> str:
    def norm(s: str) -> str:
        s = s.strip().lower()
        s = re.sub(r'[^a-z0-9]', '', s)
        return s

    return f"{norm(first)}-{norm(last)}"[:31]


def normalize_room(room: str) -> str:
    return room.strip().upper()


def load_rooms(path: str) -> list[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            rooms = [normalize_room(line) for line in f if line.strip()]
        return rooms
    except FileNotFoundError:
        return []
