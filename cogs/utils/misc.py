from random import sample
from string import ascii_letters, digits

def generate_code(length: int) -> str:
    """Generate a random code with the given length."""
    return "".join(sample(ascii_letters + digits, length))