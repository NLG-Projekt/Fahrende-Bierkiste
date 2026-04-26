from collections import Counter

PATH = "lidar_5s.bin"

def find_repeating_headers(data, max_header_len=6, step=1):
    """
    Sucht Byte-Sequenzen, die sehr oft vorkommen und als Sync/Header taugen könnten.
    """
    results = []
    for hlen in range(2, max_header_len + 1):
        c = Counter()
        for i in range(0, len(data) - hlen, step):
            c[data[i:i+hlen]] += 1
        top = c.most_common(20)
        results.append((hlen, top))
    return results

def find_candidate_sync_positions(data, pattern: bytes):
    pos = []
    start = 0
    while True:
        i = data.find(pattern, start)
        if i == -1:
            break
        pos.append(i)
        start = i + 1
    return pos

def stats_of_deltas(pos):
    if len(pos) < 3:
        return None
    deltas = [pos[i+1] - pos[i] for i in range(len(pos)-1)]
    c = Counter(deltas)
    return c.most_common(10)

def main():
    with open(PATH, "rb") as f:
        data = f.read()

    print("file bytes:", len(data))

    # 1) Suche häufige kleine Sequenzen
    res = find_repeating_headers(data, max_header_len=6, step=4)
    for hlen, top in res:
        print(f"\nTop patterns len={hlen}:")
        for pat, cnt in top[:10]:
            # nur druckbare Darstellung
            hexpat = pat.hex()
            print(f"  {hexpat}  count={cnt}")

    # 2) Nimm ein paar Kandidaten (du kannst hier später easy wechseln)
    # Wir probieren automatisch die Top-Patterns von Länge 2 und 3.
    candidates = []
    for hlen, top in res:
        if hlen in (2, 3, 4):
            candidates.extend([pat for pat, _ in top[:5]])

    tested = set()
    print("\n\nTesting candidate syncs (positions + delta stats):")
    for pat in candidates:
        if pat in tested:
            continue
        tested.add(pat)
        pos = find_candidate_sync_positions(data, pat)
        if len(pos) < 50:
            continue
        deltas = stats_of_deltas(pos)
        if not deltas:
            continue
        print(f"\npattern={pat.hex()} occurrences={len(pos)}")
        print("top deltas:", deltas)

if __name__ == "__main__":
    main()
