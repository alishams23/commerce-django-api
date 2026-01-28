import secrets

# For Generate Discount Code
SAFE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_discount_code(length=10):
    """
        For Generate Discount Code
    """
    if length < 6:
        raise ValueError("Length must be at least 6 characters")

    return ''.join(secrets.choice(SAFE_CHARS) for _ in range(length))