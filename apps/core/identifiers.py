from secrets import token_hex

from django.utils import timezone


def generate_business_code(prefix: str) -> str:
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    entropy = token_hex(2).upper()
    return f"{prefix}-{timestamp}-{entropy}"
