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
    lcm = m1 // g * m2
    k = ((a2 - a1) // g * s) % (m2 // g)
    x = (a1 + m1 * k) % lcm
    return x, lcm


def bsgs_with_order(g, h, mod, order):
    # baby-step giant-step in subgroup of size "order"
    g %= mod
    h %= mod

    if h == 1:
        return 0

    N = int(math.isqrt(order)) + 1

    # baby steps
    table = {}
    value = 1
    for j in range(N):
        if value not in table:
            table[value] = j
        value = (value * g) % mod

    # g^{-N}
    g_inv = inv_mod(g, mod)
    factor = pow(g_inv, N, mod)

    # giant steps
    value = h
    for i in range(N + 1):
        if value in table:
            x = i * N + table[value]
            return x % order
        value = (value * factor) % mod

    return None


def pohlig_hellman(base, h, mod, order, factors):
    # discrete log using Pohlig-Hellman
    x = 0
    m = 1

    for q, e in factors.items():
        n_q = q**e
        g_i = pow(base, order // n_q, mod)
        h_i = pow(h,    order // n_q, mod)

        if n_q <= 16:
            # brute force for very small factors
            cur = 1
            sol = None
            for k in range(n_q):
                if cur == h_i:
                    sol = k
                    break
                cur = (cur * g_i) % mod
            if sol is None:
                raise ValueError("no dlog for small factor")
            x_q = sol
        else:
            x_q = bsgs_with_order(g_i, h_i, mod, n_q)
            if x_q is None:
                raise ValueError("no dlog for factor {}".format(q))

        x, m = crt_pair(x, m, x_q, n_q)

    return x % order


def main():
    n = username_hash_to_n(M)
    print("start discrete_log_64.py")
    print(f"username = {USERNAME}")
    print(f"M = {M}")
    print(f"n = SHA256(username) mod M = {n}")

    x = pohlig_hellman(G, n, M, ORDER, FACTORS)

    print(f"log_{G} n mod (M-1) = {x}")


if __name__ == "__main__":
    main()