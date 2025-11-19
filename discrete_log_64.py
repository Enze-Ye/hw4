#!/usr/bin/env python3

import math
import hashlib

M = 2**64 - 59         # modulus M
ORDER = M - 1          # group order
G = 7                  # base g
USERNAME = "ye000242"  # CSELabs username

# factorization of ORDER = M - 1
# 2^2 * 11 * 137 * 547 * 5594472617641
FACTORS = {
    2: 2,
    11: 1,
    137: 1,
    547: 1,
    5594472617641: 1,
}


def username_hash_to_n(mod):
    # SHA256(username) mod mod
    digest = hashlib.sha256(USERNAME.encode("utf-8")).digest()
    return int.from_bytes(digest, byteorder="big") % mod


def egcd(a, b):
    # extended gcd
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def inv_mod(a, mod):
    # modular inverse
    g, x, _ = egcd(a, mod)
    if g != 1:
        raise ValueError("no inverse")
    return x % mod


def crt_pair(a1, m1, a2, m2):
    # combine x ≡ a1 (mod m1), x ≡ a2 (mod m2)
    g, s, t = egcd(m1, m2)
    if (a2 - a1) % g != 0:
        raise ValueError("no CRT solution")
    lcm = m1
