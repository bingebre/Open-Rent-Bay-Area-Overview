#!/usr/bin/env python3
"""Replace data: URIs in legacy/index.html with files under static/embedded/ and write index.cleaned.html."""
import base64
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "legacy" / "index.html"
OUT = ROOT / "legacy" / "index.cleaned.html"
EMBED = ROOT / "static" / "embedded"
EMBED.mkdir(parents=True, exist_ok=True)

# data:image/jpeg;base64,... or data:image/png;base64,...
PAT = re.compile(
    r"data:image/(jpeg|jpg|png|gif|webp);base64,([A-Za-z0-9+/=\s]+)",
    re.DOTALL,
)


def main():
    text = SRC.read_text(encoding="utf-8")
    counter = [0]

    def repl(m: re.Match) -> str:
        ext = m.group(1)
        if ext == "jpg":
            ext = "jpeg"
        b64 = re.sub(r"\s+", "", m.group(2))
        raw = base64.b64decode(b64)
        counter[0] += 1
        name = f"img-{counter[0]:03d}.{ext if ext != 'jpeg' else 'jpg'}"
        path = EMBED / name
        path.write_bytes(raw)
        return f"/embedded/{name}"

    new_text, n = PAT.subn(repl, text)
    OUT.write_text(new_text, encoding="utf-8")
    print(f"Extracted {n} images to {EMBED}, wrote {OUT}")


if __name__ == "__main__":
    main()
