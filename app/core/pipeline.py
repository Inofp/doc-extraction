from app.core.config import settings
from app.ocr.engine import OCREngine
from app.ocr.paddle_engine import PaddleOCREngine
from app.extraction.fields import FieldExtractor
from app.repair.llm_repair import LLMRepair
from app.core.scoring import overall_confidence
import mlflow

class DocumentPipeline:
    def __init__(self):
        self.tess = OCREngine(lang=settings.tesseract_lang)
        self.paddle = PaddleOCREngine(lang=settings.paddle_lang)
        self.extractor = FieldExtractor()
        self.repair = LLMRepair(settings.openai_api_key) if settings.openai_api_key else None

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment)

    def _ocr(self, image_path: str) -> tuple[str, float, str]:
        if settings.prefer_paddleocr:
            text, conf = self.paddle.extract(image_path)
            if text.strip():
                return text, conf, "paddleocr"
        text, conf = self.tess.extract(image_path)
        if text.strip():
            return text, conf, "tesseract"
        text, conf = self.paddle.extract(image_path)
        return text, conf, "paddleocr"

    def run(self, image_path: str) -> dict:
        with mlflow.start_run():
            text, ocr_conf, ocr_engine = self._ocr(image_path)
            base = self.extractor.extract(text).model_dump()
            conf = overall_confidence(ocr_conf, base)

            mlflow.log_param("ocr_engine", ocr_engine)
            mlflow.log_metric("ocr_conf", float(ocr_conf))
            mlflow.log_metric("base_conf", float(conf))

            out = {"fields": base, "ocr_engine": ocr_engine, "ocr_conf": ocr_conf, "confidence": conf, "repaired": False}

            if settings.use_llm_repair and self.repair and conf < settings.min_confidence_for_llm:
                repaired = self.repair.repair(text, base)
                out["fields"] = repaired
                out["repaired"] = True

            return out