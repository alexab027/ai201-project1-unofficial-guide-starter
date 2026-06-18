import json

# Preview chunks and make sure they look reasonable
with open("documents/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

step = max(1, len(chunks) // 5)

for i, c in enumerate(chunks[::step][:5], start=1):
    print("=" * 80)
    print(f"CHUNK {i}")
    print(f"[{c['type']} | {c['title']} | {c['section']}]")
    print(f"Word count: {c['word_count']}")
    print()
    print(c["text"])   # print the FULL chunk, not just first 300 chars
    print()