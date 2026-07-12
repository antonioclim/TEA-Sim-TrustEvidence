from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'figures' / 'outputs'
paths = [OUTPUT / f'Figure_{i}.png' for i in range(1, 6)]
for p in paths:
    if not p.exists():
        raise FileNotFoundError(p)

thumb_w = 1050
margin = 40
label_h = 52
thumbs = []
for p in paths:
    im = Image.open(p).convert('RGB')
    ratio = thumb_w / im.width
    im = im.resize((thumb_w, int(im.height * ratio)), Image.Resampling.LANCZOS)
    thumbs.append((p.stem, im))
max_h = max(im.height for _, im in thumbs)
canvas_w = thumb_w * 2 + margin * 3
rows = 3
canvas_h = rows * (max_h + label_h) + margin * 4
canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default(size=28)
for idx, (label, im) in enumerate(thumbs):
    row, col = divmod(idx, 2)
    x = margin + col * (thumb_w + margin)
    y = margin + row * (max_h + label_h + margin)
    canvas.paste(im, (x, y + label_h))
    draw.text((x, y + 8), label.replace('_', ' '), font=font, fill='black')
canvas.save(OUTPUT / 'GENERATED_FIGURES_CONTACT_SHEET.png', dpi=(200, 200), optimize=False)
