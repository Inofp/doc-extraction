from paddleocr import PaddleOCR

class PaddleOCREngine:
    def __init__(self, lang: str = "en"):
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)

    def extract(self, image_path: str) -> tuple[str, float]:
        result = self.ocr.ocr(image_path, cls=True)
        lines = []
        confs = []
        for page in result:
            for item in page:
                text = item[1][0]
                conf = float(item[1][1])
                lines.append(text)
                confs.append(conf)
        text = "\n".join(lines).strip()
        avg_conf = float(sum(confs) / max(len(confs), 1))
        return text, avg_conf