
import fitz
import pandas as pd
from pathlib import Path

# Locate the main project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Location of original PDF documents
RAW_DIR = PROJECT_DIR / "data" / "raw"

# Location to save extracted text
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Countries and their document folders
countries = ["india", "eu", "uk", "oecd"]

all_documents = []

for country in countries:

    country_folder = RAW_DIR / country

    for pdf_file in country_folder.glob("*.pdf"):

        print(f"Reading: {pdf_file.name}")

        document = fitz.open(pdf_file)

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text")

            if text.strip():

                all_documents.append({
                    "country": country,
                    "document": pdf_file.name,
                    "page": page_number,
                    "text": text
                })

        document.close()

# Convert extracted information into a DataFrame
df = pd.DataFrame(all_documents)

# Save the extracted text
output_file = OUTPUT_DIR / "extracted_documents.csv"

df.to_csv(output_file, index=False)

print("\nExtraction completed!")
print("Total pages extracted:", len(df))
print("Saved to:", output_file)
