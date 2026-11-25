
import re
import pandas as pd
from pathlib import Path

# Locate project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "processed" / "extracted_documents.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Local English stopwords (no internet download required)
stop_words = {
    "a", "an", "the", "and", "or", "but", "if",
    "of", "at", "by", "for", "with", "about",
    "against", "between", "into", "through",
    "during", "before", "after", "above", "below",
    "to", "from", "in", "on", "out", "over",
    "under", "again", "further", "then", "once",
    "is", "am", "are", "was", "were", "be",
    "been", "being", "have", "has", "had",
    "do", "does", "did", "doing", "this", "that",
    "these", "those", "it", "its", "as", "such",
    "than", "too", "very", "can", "could",
    "would", "there", "their", "they", "them",
    "we", "our", "you", "your", "he", "she",
    "his", "her", "who", "which", "what",
    "when", "where", "how", "why"
}

# Keep legally meaningful words such as:
# must, shall, should, may, will, not, no, cannot

# Load extracted document text
df = pd.read_csv(INPUT_FILE)

def clean_text(text):

    # Convert to lowercase
    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Split into words
    words = text.split()

    # Remove common words
    words = [
        word for word in words
        if word not in stop_words
    ]

    return " ".join(words)


# Generate cleaned text
df["cleaned_text"] = df["text"].apply(clean_text)

# Save results
output_file = OUTPUT_DIR / "cleaned_documents.csv"

df.to_csv(output_file, index=False)

print("Text preprocessing completed!")
print("Total pages processed:", len(df))
print("Output saved to:", output_file)

# Display an example
if not df.empty:
    print("\nORIGINAL TEXT:")
    print(df.iloc[0]["text"][:500])

    print("\nCLEANED TEXT:")
    print(df.iloc[0]["cleaned_text"][:500])
