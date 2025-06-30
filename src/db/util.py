import string
from random import choice

alpha_num = string.ascii_letters + string.digits

def gen_random_string(length: int) -> str:
    
    if length < 0:
        raise ValueError("length cannot be negative")

    res: str = ""

    for _ in range(length):
        res += choice(alpha_num)

    return res