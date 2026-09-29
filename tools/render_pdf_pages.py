import sys
from pathlib import Path

import pypdfium2 as pdfium


pdf_path = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
output_dir.mkdir(parents=True, exist_ok=True)

document = pdfium.PdfDocument(pdf_path)
for number, page in enumerate(document, 1):
    image = page.render(scale=2).to_pil()
    image.save(output_dir / f"page-{number}.png")

print(len(document))
