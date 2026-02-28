from app.ocr.engine import OCREngine
from app.extraction.fields import FieldExtractor
from app.repair.llm_repair import LLMRepair

class DocumentPipeline:
    def __init__(self, api_key: str):
        self.ocr = OCREngine()
        self.extractor = FieldExtractor()
        self.repair = LLMRepair(api_key)

    def run(self, image_path: str):
        text = self.ocr.extract_text(image_path)
        fields = self.extractor.extract(text)
        repaired = self.repair.repair(text, fields.dict())
        return repaired