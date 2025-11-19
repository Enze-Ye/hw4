#!/usr/bin/env python3

import math
import hashlib

P = 2**31 - 1          # modulus p
G = 7                  # base g
USERNAME = "ye000242"  # CSELabs username


def username_hash_to_n(username: str) -> int:
    """Compute SHA256(username) mod p."""
    digest = hashlib.sha256(username.encode("utf-8")).digest()
    n = int.from_bytes(digest, byteorder="big") % P
    return n


def bsgs(g: int, h: int, p: int) -> int | None:
    """Baby-step giant-step for g^x = h mod p."""
    g %= p
    h %= p

    if h == 1:
        return 0

    N = int(math.isqrt(p - 1)) + 1

    # baby steps
    table = {}
    value = 1
    for j in range(N):
        if value not in table:
            table[value] = j
        value = (value * g) % p

    # g^{-N}
    g_inv = pow(g, p - 2, p)
    factor = pow(g_inv, N, p)

    # giant steps
    value = h
    for i in range(N + 1):
        if value in table:
            x = i * N + table[value]
            return x % (p - 1)
        value = (value * factor) % p

    return None


def main() -> None:
    username = USERNAME
    n = username_hash_to_n(username)

    print(f"username = {username}")
    print(f"p = {P}")
    print(f\"n = SHA256(username) mod p = {n}\")

    x = bsgs(G, n, P)

    if x is None:
        print("discrete log not found")
    else:
        print(f\"log_{G} n mod (p-1) = {x}\")


if __name__ == "__main__":
    main()