#!/usr/bin/env python3
import sys

SCRAMBLED = (
    "p8rwo02U1EsihgCZnJ9NYj73qm" # A-Z
    "L5kAXftbWQ64SMdVFlIRaOxGDT" # a-z
    "eBvPuKyzHc"                 # 0-9
)
ORIGINAL = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
)

TABLE = str.maketrans(SCRAMBLED, ORIGINAL)

def decode(text: str) -> str:
    return text.translate(TABLE)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(decode(" ".join(sys.argv[1:])))
    else:
        for line in sys.stdin:
            print(decode(line), end="")
