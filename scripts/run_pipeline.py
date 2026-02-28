import os
from app.core.pipeline import DocumentPipeline

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    pipeline = DocumentPipeline(api_key=api_key)

    result = pipeline.run("data/samples/sample_invoice.jpg")
    print(result)