import hashlib
from django.conf import settings


def generate_ticket_number(ticket_id, created_at):
    raw = f"{ticket_id}-{created_at.timestamp()}-{settings.SECRET_KEY}"

    digest = hashlib.sha256(raw.encode()).hexdigest()

    number = int(digest, 16) % 1_000_000

    return f"{number:06d}"