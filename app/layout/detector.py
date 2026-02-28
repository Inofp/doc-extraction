import layoutparser as lp
import cv2

class LayoutDetector:
    def __init__(self):
        self.model = lp.Detectron2LayoutModel(
            "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5]
        )

    def detect(self, image_path: str):
        image = cv2.imread(image_path)
        layout = self.model.detect(image)
        return layout