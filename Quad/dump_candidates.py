from collections import Counter

PATH = "lidar_5s.bin"

CANDIDATES = [
    bytes.fromhex("00770077"),
    bytes.fromhex("008a00"),
    bytes.fromhex("8a00"),
    bytes.fromhex("064406"),
    bytes.fromhex("4406"),
]

DUMP_BYTES_BEFORE = 16
DUMP_BYTES_AFTER  = 64
MAX_DUMPS_PER_PATTERN = 8

def hexline(b: bytes) -> str:
    return " ".join(f"{x:02x}" for x in b)

def find_positions(data: bytes, pat: bytes):
    pos = []
    start = 0
    while True:
        i = data.find(pat, start)
        if i == -1:
            break
        pos.append(i)
        start = i + 1
    return pos

def main():
    data = open(PATH, "rb").read()
    print("bytes:", len(data))

    for pat in CANDIDATES:
        pos = find_positions(data, pat)
        print("\n=== pattern", pat.hex(), "occurrences", len(pos), "===")
        if len(pos) < 3:
            continue

        deltas = [pos[i+1]-pos[i] for i in range(len(pos)-1)]
        top = Counter(deltas).most_common(12)
        print("top deltas:", top)

        # dump a few occurrences
        for k, p in enumerate(pos[:MAX_DUMPS_PER_PATTERN]):
            a = max(0, p - DUMP_BYTES_BEFORE)
            b = min(len(data), p + len(pat) + DUMP_BYTES_AFTER)
            chunk = data[a:b]
            print(f"\n#{k} offset={p} (showing {a}..{b})")
            print(hexline(chunk))

if __name__ == "__main__":
    main()
