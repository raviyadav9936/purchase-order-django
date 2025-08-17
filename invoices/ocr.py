import fitz 
import io
from PIL import Image
import pytesseract

def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    doc = fitz.open(path)
    for page in doc:
        t = page.get_text("text")
        if t:
            text_parts.append(t)

        for img in page.get_images(full=True):
            xref = img[0]
            base = doc.extract_image(xref)
            image_bytes = base["image"]
            img_pil = Image.open(io.BytesIO(image_bytes))
            ocr_txt = pytesseract.image_to_string(img_pil)
            if ocr_txt.strip():
                text_parts.append(ocr_txt)
    doc.close()
    return "\n".join(text_parts)
