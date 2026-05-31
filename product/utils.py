
MULTIPLIER = 7919
OFFSET = 100000


def encode_product_id(product_id: int) -> int:
    return int(product_id) * MULTIPLIER + OFFSET

def decode_product_id(public_id: int) -> int:
    return (int(public_id) - OFFSET) // MULTIPLIER
