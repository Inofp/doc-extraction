import os
import json
import copy
from app.core.config import settings
from app.core.pipeline import DocumentPipeline
from app.core.scoring import exact_match, similarity
import mlflow

KEYS = ["invoice_number", "invoice_date", "seller_name", "buyer_name", "total_amount", "iban"]

def aggregate(scores: list[dict]) -> dict:
    if not scores:
        return {}
    out = {k: 0.0 for k in scores[0].keys()}
    for s in scores:
        for k, v in s.items():
            out[k] += float(v)
    n = len(scores)
    return {k: v / n for k, v in out.items()} | {"n": n}

def score(pred: dict, gt: dict) -> dict:
    out = {}
    for k in KEYS:
        out[f"{k}_em"] = exact_match(pred.get(k), gt.get(k))
        out[f"{k}_sim"] = similarity(pred.get(k), gt.get(k))
    out["avg_em"] = sum(out[f"{k}_em"] for k in KEYS) / len(KEYS)
    out["avg_sim"] = sum(out[f"{k}_sim"] for k in KEYS) / len(KEYS)
    return out

def run(gt_path: str):
    pipe = DocumentPipeline()

    base_scores = []
    repair_scores = []

    with open(gt_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            image = item["image"]
            gt_fields = item["fields"]

            prev_use = settings.use_llm_repair
            settings.use_llm_repair = False
            r_base = pipe.run(image)
            settings.use_llm_repair = prev_use

            settings.use_llm_repair = True
            r_rep = pipe.run(image)

            base_scores.append(score(r_base["fields"], gt_fields))
            repair_scores.append(score(r_rep["fields"], gt_fields))

    base = aggregate(base_scores)
    rep = aggregate(repair_scores)

    delta = {}
    for k in base.keys():
        if k in rep and isinstance(base[k], (int, float)) and isinstance(rep[k], (int, float)):
            delta[f"delta_{k}"] = float(rep[k]) - float(base[k])

    return {"baseline": base, "with_repair": rep, "delta": delta}

if __name__ == "__main__":
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)

    result = run("data/processed/gt.jsonl")

    with mlflow.start_run(run_name="benchmark"):
        mlflow.log_param("min_confidence_for_llm", float(settings.min_confidence_for_llm))
        for grp in ["baseline", "with_repair", "delta"]:
            for k, v in result[grp].items():
                if isinstance(v, (int, float)):
                    mlflow.log_metric(f"{grp}_{k}", float(v))

    print(json.dumps(result, ensure_ascii=False, indent=2))