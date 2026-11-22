import json
import struct
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Tuple

@dataclass
class ParsedDoc:
    text: str
    image_path: Optional[str] = None
    image_format: Optional[str] = None
    image_size: Optional[Tuple[int, int]] = None

def parse_png_header(path: Path):
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return {"format": "png", "width": width, "height": height}

def parse_multimodal(text: str, image_path: Optional[str] = None):
    doc = ParsedDoc(text=text)
    if image_path:
        p = Path(image_path)
        doc.image_path = str(p)
        if p.exists() and p.suffix.lower() == ".png":
            info = parse_png_header(p)
            if info:
                doc.image_format = info["format"]
                doc.image_size = (info["width"], info["height"])
    return asdict(doc)

def create_demo_png(path: Path, width: int = 64, height: int = 48):
    # Minimal PNG header for demo parsing (not a full renderable image).
    header = b"\x89PNG\r\n\x1a\n"
    header += struct.pack(">I", 13) + b"IHDR"
    header += struct.pack(">II", width, height)
    header += b"\x08\x06\x00\x00\x00"
    path.write_bytes(header + b"\x00" * 8)

def main():
    image_path = Path("demo_multimodal.png")
    if not image_path.exists():
        create_demo_png(image_path)
    result = parse_multimodal(
        text="A cat sitting on a mat.",
        image_path=str(image_path),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()