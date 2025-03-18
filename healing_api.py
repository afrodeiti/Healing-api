from flask import Flask, request, jsonify
import pandas as pd
import re
from rapidfuzz import process, fuzz

app = Flask(__name__)

# Load divine healing codes from Excel
def load_healing_codes_from_excel():
    try:
        df = pd.read_excel("healing_codes.xlsx")
        codes = []
        for _, row in df.iterrows():
            if "Code" in row and "Meaning" in row:
                codes.append({
                    "code": str(row["Code"]).strip(),
                    "meaning": str(row["Meaning"]).strip(),
                    "keywords": re.findall(r'\b\w+\b', str(row["Meaning"]).lower())  # Extract words for search
                })
        return codes
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return []

# Load divine healing codes from a text file
def load_healing_codes_from_txt():
    try:
        codes = []
        with open("healing_codes.txt", "r", encoding="utf-8") as file:
            current_category = None
            for line in file:
                line = line.strip()
                if line.isupper():  
                    current_category = line  # Capture category headers
                elif re.match(r'^\d+.*-.*$', line):  # Matches "CODE - MEANING" format
                    parts = line.split("-", 1)  
                    if len(parts) == 2:
                        code = parts[0].strip()
                        meaning = parts[1].strip()
                        keywords = re.findall(r'\b\w+\b', meaning.lower())  
                        if current_category:
                            keywords.append(current_category.lower())  
                        codes.append({"code": code, "meaning": meaning, "keywords": keywords})
        return codes
    except Exception as e:
        print(f"❌ Error loading TXT: {e}")
        return []

# Combine healing codes from both sources
healing_codes = load_healing_codes_from_excel() + load_healing_codes_from_txt()

# Create a list of all unique keywords
all_keywords = list(set(keyword for entry in healing_codes for keyword in entry["keywords"]))

@app.route('/get-healing-code', methods=['POST'])
def get_healing_code():
    """Retrieve divine healing codes based on a requested issue (including similar meanings)."""
    data = request.json
    issue = data.get("issue", "").lower()
    limit = data.get("limit", None)  # Allow users to set a custom limit

    print(f"\n🔍 Searching for issue: {issue}")

    # Use a dictionary to track unique codes
    unique_codes = {}

    # Try exact matches first
    for entry in healing_codes:
        if any(keyword == issue for keyword in entry["keywords"]):  # Must be an exact match
            unique_codes[entry["code"]] = entry

    # If no exact matches, find the closest keyword
    if not unique_codes:
        print("\n❌ No exact match found. Checking similar words...")
        best_match, score = process.extractOne(issue, all_keywords, scorer=fuzz.partial_ratio)
        print(f"🔍 Best fuzzy match: {best_match} (Score: {score})")
        if score > 85:  # Higher threshold to improve accuracy
            for entry in healing_codes:
                if best_match in entry["keywords"]:
                    unique_codes[entry["code"]] = entry

    # Convert dictionary values back to a list and apply limit
    matched_codes = list(unique_codes.values())

    print("\n✅ Matched Codes (Unique Only):")
    for match in matched_codes:
        print(f" - Code: {match['code']}, Meaning: {match['meaning']}")

    if matched_codes:
        if limit and isinstance(limit, int):
            matched_codes = matched_codes[:limit]

        return jsonify([
            {"code": entry["code"], "meaning": entry["meaning"]}
            for entry in matched_codes
        ])

    print("\n❌ No healing code found for this issue.")
    return jsonify({"message": "No healing code found for this issue."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
