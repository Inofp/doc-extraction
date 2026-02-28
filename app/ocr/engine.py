from PIL import Image
import pytesseract

class OCREngine:
    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract(self, image_path: str) -> tuple[str, float]:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, lang=self.lang, output_type=pytesseract.Output.DICT)
        words = []
        confs = []
        n = len(data.get("text", []))
        for i in range(n):
            w = (data["text"][i] or "").strip()
            c = data["conf"][i]
            try:
                cf = float(c)
            except Exception:
                cf = -1.0
            if w:
                words.append(w)
            if cf >= 0:
                confs.append(cf / 100.0)
        text = " ".join(words).strip()
        avg_conf = float(sum(confs) / max(len(confs), 1))
        return text, avg_conf