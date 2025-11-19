#!/usr/bin/env python3

import hashlib
import math

USERNAME = "ye000242"

P_PATH = "/project/web-classes/Fall-2025/csci5471/hw4/p"
Q_PATH = "/project/web-classes/Fall-2025/csci5471/hw4/q"


def read_der_integer(path):
    # read ASN.1 DER INTEGER from file
    with open(path, "rb") as f:
        data = f.read()
    if not data or data[0] != 0x02:
        raise ValueError("not an INTEGER DER")
    length_byte = data[1]
    if length_byte & 0x80 == 0:
        length = length_byte
        offset = 2
    elif length_byte == 0x81:
        length = data[2]
        offset = 3
    elif length_byte == 0x82:
        length = (data[2] << 8) | data[3]
        offset = 4
    else:
        raise ValueError("unsupported length")
    int_bytes = data[offset:offset + length]
    return int.from_bytes(int_bytes, byteorder="big")


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


def sha256_to_e(username):
    # SHA256(username) -> odd integer e
    digest = hashlib.sha256(username.encode("utf-8")).digest()
    e = int.from_bytes(digest, byteorder="big")
    if e % 2 == 0:
        e += 1
    return e


def main():
    p = read_der_integer(P_PATH)
    q = read_der_integer(Q_PATH)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = sha256_to_e(USERNAME)

    # make sure gcd(e, phi) = 1
    while math.gcd(e, phi) != 1:
        e += 2

    d = inv_mod(e, phi)

    print(f"username = {USERNAME}")
    print(f"p (bits) = {p.bit_length()}")
    print(f"q (bits) = {q.bit_length()}")
    print(f"n (bits) = {n.bit_length()}")

    print(f"e (hex) = {e:x}")
    print(f"d (hex) = {d:x}")


if __name__ == "__main__":
    main()