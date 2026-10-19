import json
import pandas as pd

# Path to the SQuAD v2 training JSON file
input_file = "../data/train-v2.0.json"

# Output pickle file
output_file = "../data/squad_train.pkl"

# Load the JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
context_id = 0

# Iterate through articles
for article in data["data"]:
    # Iterate through paragraphs (contexts)
    for paragraph in article["paragraphs"]:
        context = paragraph["context"]

        # Keep only answerable questions
        answerable_questions = [
            qa for qa in paragraph["qas"]
            if not qa["is_impossible"]
        ]

        # Skip contexts without answerable questions
        if not answerable_questions:
            continue

        # Assign one ID to each context
        for qa in answerable_questions:
            # SQuAD v2 can contain multiple annotated answers.
            # Use the first answer for this question.
            if not qa["answers"]:
                continue

            answer = qa["answers"][0]["text"]

            rows.append({
                "context_id": context_id,
                "context": context,
                "question": qa["question"],
                "answer": answer
            })

        context_id += 1

# Create DataFrame with the required column order
df = pd.DataFrame(
    rows,
    columns=["context_id", "context", "question", "answer"]
)

# Save DataFrame to pickle
df.to_pickle(output_file)

print(f"Saved {len(df)} question-answer pairs to {output_file}")
print(f"Number of unique contexts: {df['context_id'].nunique()}")
print(df.head())
