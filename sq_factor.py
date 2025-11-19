#!/usr/bin/env python3

import os
import math
import secrets
import subprocess

SQ_BIN = "/project/web-classes/Fall-2025/csci5471/hw4/sq"

MOD_FILE = "sq_modulus.der"
A_FILE = "sq_a.der"
Y_FILE = "sq_y.der"


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


def int_to_der_bytes(x):
    # encode integer as ASN.1 DER INTEGER
    if x < 0:
        raise ValueError("only nonnegative supported")
    length = (x.bit_length() + 7) // 8 or 1
    b = x.to_bytes(length, byteorder="big")
    if b[0] & 0x80:
        b = b"\x00" + b
    L = len(b)
    if L < 128:
        len_bytes = bytes([L])
    elif L < 256:
        len_bytes = bytes([0x81, L])
    else:
        len_bytes = bytes([0x82, (L >> 8) & 0xFF, L & 0xFF])
    return b"\x02" + len_bytes + b


def write_der_integer(path, x):
    # write ASN.1 DER INTEGER to file
    data = int_to_der_bytes(x)
    with open(path, "wb") as f:
        f.write(data)


def get_modulus():
    # obtain modulus n from sq
    if not os.path.exists(MOD_FILE):
        with open(MOD_FILE, "wb") as f:
            subprocess.run([SQ_BIN, "modulus"], check=True, stdout=f)
    return read_der_integer(MOD_FILE)


def get_sqrt_mod_n(a, n):
    # ask sq for y such that y^2 ≡ a (mod n)
    write_der_integer(A_FILE, a)
    with open(Y_FILE, "wb") as f:
        subprocess.run([SQ_BIN, "sqrt", A_FILE], check=True, stdout=f)
    return read_der_integer(Y_FILE)


def find_factor():
    n = get_modulus()
    print(f"n (bits) = {n.bit_length()}")

    while True:
        x = secrets.randbelow(n - 2) + 1
        if math.gcd(x, n) != 1:
            continue
        a = pow(x, 2, n)
        y = get_sqrt_mod_n(a, n)

        # check x ≠ ±y (mod n)
        if y == x or y == (n - x) % n:
            continue

        g = math.gcd(x - y, n)
        if 1 < g < n:
            p = g
            q = n // g
            if p > q:
                p, q = q, p
            print("nontrivial factorization found:")
            print(f"p (bits) = {p.bit_length()}")
            print(f"q (bits) = {q.bit_length()}")
            print(f"p = {p}")
            print(f"q = {q}")
            return


def main():
    find_factor()


if __name__ == "__main__":
    main()