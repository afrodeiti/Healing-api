from flask import Flask, request, jsonify
import pandas as pd
import re
import threading
import time
from rapidfuzz import process, fuzz

app = Flask(__name__)

# ---------------------------------------------
# HEALING CODE LOGIC
# ---------------------------------------------

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
                    "keywords": re.findall(r'\b\w+\b', str(row["Meaning"]).lower())
                })
        return codes
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return []

# Load divine healing codes from text file
def load_healing_codes_from_txt():
    try:
        codes = []
        with open("healing_codes.txt", "r", encoding="utf-8") as file:
            current_category = None
            for line in file:
                line = line.strip()
                if line.isupper():
                    current_category = line
                elif re.match(r'^\d+.*-.*$', line):
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

# Combine and prepare data
healing_codes = load_healing_codes_from_excel() + load_healing_codes_from_txt()
all_keywords = list(set(keyword for entry in healing_codes for keyword in entry["keywords"]))

@app.route('/get-healing-code', methods=['POST'])
def get_healing_code():
    data = request.json
    issue = data.get("issue", "").lower()
    limit = data.get("limit", None)

    print(f"\n🔍 Searching for issue: {issue}")
    unique_codes = {}

    for entry in healing_codes:
        if any(keyword == issue for keyword in entry["keywords"]):
            unique_codes[entry["code"]] = entry

    if not unique_codes:
        print("❌ No exact match found. Using fuzzy match...")
        best_match, score = process.extractOne(issue, all_keywords, scorer=fuzz.partial_ratio)
        print(f"🔍 Best match: {best_match} (Score: {score})")
        if score > 85:
            for entry in healing_codes:
                if best_match in entry["keywords"]:
                    unique_codes[entry["code"]] = entry

    matched_codes = list(unique_codes.values())

    if matched_codes:
        if limit and isinstance(limit, int):
            matched_codes = matched_codes[:limit]

        return jsonify([
            {"code": entry["code"], "meaning": entry["meaning"]}
            for entry in matched_codes
        ])

    return jsonify({"message": "No healing code found for this issue."})

# ---------------------------------------------
# INTENTION REPEATER LOGIC
# ---------------------------------------------

active_intentions = []

def repeat_intention(intention_text, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        print(f"🔁 Repeating: {intention_text}")
        time.sleep(1)
    print(f"✅ Finished repeating: {intention_text}")

@app.route('/run-intention', methods=['POST'])
def run_intention():
    data = request.json
    intention = data.get("intention")
    duration = data.get("duration", 60)

    if not intention:
        return jsonify({"success": False, "message": "No intention provided."}), 400

    thread = threading.Thread(target=repeat_intention, args=(intention, duration))
    thread.start()

    active_intentions.append({"intention": intention, "duration": duration})

    return jsonify({
        "success": True,
        "message": f"Intention is now running for {duration} seconds.",
        "intention": intention
    })

# ---------------------------------------------
# RUN APP
# ---------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
