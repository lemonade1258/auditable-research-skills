import sys, os
import fitz

out_dir = sys.argv[1]
for path in sys.argv[2:]:
    try:
        doc = fitz.open(path)
        text = "\n".join(p.get_text() for p in doc)
        name = os.path.splitext(os.path.basename(path))[0] + ".txt"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK {name}: {len(text)} chars, {doc.page_count} pages")
    except Exception as e:
        print(f"FAIL {path}: {e}")
