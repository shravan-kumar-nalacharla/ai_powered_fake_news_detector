import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "shravan1nala/tejas-fake-news-model-v3.1"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

model.to(device)
model.eval()


def predict(text: str):
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    label_id = int(probs.argmax())
    confidence = float(probs[label_id])

    label_map = {
        0: "REAL",
        1: "FAKE"
    }

    return {
        "label": label_map[label_id],
        "confidence": round(confidence, 4),
        "probabilities": {
            "REAL": round(float(probs[0]), 4),
            "FAKE": round(float(probs[1]), 4)
        }
    }
