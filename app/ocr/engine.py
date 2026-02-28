import pytesseract
from PIL import Image

class OCREngine:
    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract_text(self, image_path: str) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=self.lang)