import requests
import os
import time

BASE_URL = "https://www.strokeorder.com/assets/bishun/animation/"
OUT_DIR = "strokeorder_gifs"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# CJK Unified Ideographs range
START = 0x4E00
END = 0x9FFF

os.makedirs(OUT_DIR, exist_ok=True)

def download_gif(codepoint):
    url = f"{BASE_URL}{codepoint}.gif"
    save_path = os.path.join(OUT_DIR, f"{codepoint}.gif")

    # Skip if already exists
    if os.path.exists(save_path):
        return

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code == 200 and r.content.startswith(b"GIF"):
            with open(save_path, "wb") as f:
                f.write(r.content)

            char = chr(codepoint)
            print(f"✅ {char} | U+{codepoint:X} downloaded")

        else:
            print(f"❌ Missing: U+{codepoint:X}")

    except Exception as e:
        print(f"⚠️ Error U+{codepoint:X}:", e)

def main():
    total = END - START + 1
    count = 0

    for codepoint in range(START, END + 1):
        download_gif(codepoint)
        count += 1

        # polite rate-limit
        time.sleep(0.3)

        if count % 200 == 0:
            print(f"--- Progress: {count}/{total} ---")

if __name__ == "__main__":
    main()
