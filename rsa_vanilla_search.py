#!/usr/bin/env python3

import subprocess
import sys
import os

VANILLA_DIR = "/project/web-classes/Fall-2025/csci5471/hw4/vanilla"
DB_DIR = "/project/web-classes/Fall-2025/csci5471/hw1/db"


def read_int_from_file(path):
    # read file as big-endian integer
    with open(path, "rb") as f:
        data = f.read()
    return int.from_bytes(data, byteorder="big")


def parse_pk_with_openssl(pk_path):
    # use openssl to extract modulus n and exponent e
    proc = subprocess.run(
        ["openssl", "rsa", "-pubin", "-text", "-noout", "-in", pk_path],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = proc.stdout.splitlines()

    # parse modulus
    n_hex_chunks = []
    in_mod = False
    for line in lines:
        line = line.strip()
        if line.startswith("Modulus:"):
            in_mod = True
            continue
        if in_mod:
            if line.startswith("Exponent:"):
                break
            # hex bytes like "00:b1:23:..."
            parts = line.split(":")
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                if all(c in "0123456789abcdefABCDEF" for c in p):
                    n_hex_chunks.append(p)
    n_hex = "".join(n_hex_chunks)
    n = int(n_hex, 16)

    # parse exponent, e.g. "Exponent: 65537 (0x10001)"
    e = None
    for line in lines:
        line = line.strip()
        if line.startswith("Exponent:"):
            # second token is decimal exponent
            parts = line.split()
            for token in parts:
                if token.isdigit():
                    e = int(token)
                    break
            break
    if e is None:
        raise ValueError("exponent not found")

    return n, e


def search_plaintext_for_cipher(pk_path, ct_path):
    # get n, e from public key
    n, e = parse_pk_with_openssl(pk_path)

    # ciphertext as integer
    c = read_int_from_file(ct_path)

    # scan LAPDOG database
    for root, _, files in os.walk(DB_DIR):
        for name in sorted(files):
            fp = os.path.join(root, name)
            with open(fp, "rb") as f:
                data = f.read()
            if len(data) < 256:
                continue
            # check all 256-byte blocks
            for offset in range(0, len(data) - 256 + 1):
                block = data[offset:offset + 256]
                m = int.from_bytes(block, byteorder="big")
                if pow(m, e, n) == c:
                    return fp, offset, block

    return None, None, None


def main():
    if len(sys.argv) != 2:
        print("usage: python3 rsa_vanilla_search.py N")
        print("where N is the last digit of your student ID (0-9).")
        sys.exit(1)

    N = sys.argv[1]
    if not N.isdigit() or not (0 <= int(N) <= 9):
        print("N must be a digit 0-9")
        sys.exit(1)

    pk_path = os.path.join(VANILLA_DIR, f"pk{N}")
    ct_path = os.path.join(VANILLA_DIR, f"ct{N}")

    print(f"using pk file: {pk_path}")
    print(f"using ct file: {ct_path}")

    fp, offset, block = search_plaintext_for_cipher(pk_path, ct_path)

    if fp is None:
        print("no matching plaintext found")
    else:
        print("plaintext found:")
        print(f"  file   : {fp}")
        print(f"  offset : {offset}")
        print("  bytes  :")
        # print hex and ASCII
        hex_str = block.hex()
        print(f"    hex : {hex_str}")
        try:
            ascii_str = block.decode("utf-8", errors="replace")
        except Exception:
            ascii_str = ""
        print(f"    text: {ascii_str}")


if __name__ == "__main__":
    main()