# Demonstrate factoring from nontrivial square roots mod n.

import subprocess
import math
import random

SQ_PATH = "/project/web-classes/Fall-2025/csci5471/hw4/sq"

def der_to_int(der):
    # DER INTEGER: 0x02 | length | value
    if der[0] != 0x02:
        raise ValueError("Not a DER INTEGER")
    length = der[1]
    val = der[2:2+length]
    return int.from_bytes(val, "big")

def read_modulus():
    out = subprocess.check_output([SQ_PATH, "modulus"])
    return der_to_int(out)

def der_encode(x):
    b = x.to_bytes((x.bit_length() + 7) // 8, "big")
    if b[0] >= 0x80:
        b = b"\x00" + b
    return b"\x02" + len(b).to_bytes(1, "big") + b

def run_sqrt(a_bytes):
    out = subprocess.check_output([SQ_PATH, "sqrt"], input=a_bytes)
    return der_to_int(out)

def trial(n):
    x = random.randrange(2, n - 1)
    a = pow(x, 2, n)
    a_der = der_encode(a)

    try:
        y = run_sqrt(a_der)
    except:
        return None

    if y == x or y == n - x:
        return None

    g = math.gcd(x - y, n)
    if g != 1 and g != n:
        return g, n // g
    return None

def main():
    n = read_modulus()
    print("n (bits) =", n.bit_length())

    while True:
        r = trial(n)
        if r:
            p, q = r
            print("p (bits) =", p.bit_length())
            print("q (bits) =", q.bit_length())
            break

if __name__ == "__main__":
    main()