import json
from app.core.pipeline import DocumentPipeline
from app.core.scoring import exact_match, similarity
import mlflow
from app.core.config import settings

KEYS = ["invoice_number", "invoice_date", "seller_name", "buyer_name", "total_amount", "iban"]

def score_item(pred: dict, gt: dict) -> dict:
    out = {}
    for k in KEYS:
        p = pred.get(k)
        g = gt.get(k)
        out[f"{k}_em"] = exact_match(p, g)
        out[f"{k}_sim"] = similarity(p, g)
    out["avg_em"] = sum(out[f"{k}_em"] for k in KEYS) / len(KEYS)
    out["avg_sim"] = sum(out[f"{k}_sim"] for k in KEYS) / len(KEYS)
    return out

def run_eval(gt_path: str):
    pipe = DocumentPipeline()
    total = {f"{k}_em": 0.0 for k in KEYS} | {f"{k}_sim": 0.0 for k in KEYS}
    total["avg_em"] = 0.0
    total["avg_sim"] = 0.0
    n = 0

    with open(gt_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            image = item["image"]
            gt_fields = item["fields"]
            res = pipe.run(image)
            pred_fields = res["fields"]
            s = score_item(pred_fields, gt_fields)
            for k, v in s.items():
                total[k] += float(v)
            n += 1

    if n == 0:
        return {}

    return {k: v / n for k, v in total.items()} | {"n": n}

if __name__ == "__main__":
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)

    metrics = run_eval("data/processed/gt.jsonl")
    with mlflow.start_run(run_name="evaluation"):
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(k, float(v))
    print(json.dumps(metrics, ensure_ascii=False, indent=2))