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

import hashlib

@app.route('/run-intention', methods=['POST'])
def run_intention():
    data = request.json
    intention = data.get("intention", "").strip()
    duration = int(data.get("duration", 60))  # in seconds
    frequency = float(data.get("frequency", 0))  # Hz
    boost = bool(data.get("boost", False))
    multiplier = int(data.get("multiplier", 1))

    if not intention:
        return jsonify({"success": False, "message": "No intention provided."}), 400

    def sha512(message):
        return hashlib.sha512(message.encode('utf-8')).hexdigest().upper()

    def repeat_intention():
        start_time = time.time()
        total_iterations = 0

        interval = (1 / frequency) if frequency > 0 else 0.001  # default to as fast as possible

        while time.time() - start_time < duration:
            text_to_hash = intention
            if boost:
                text_to_hash = sha512(text_to_hash + ': ' + intention)
            hash_result = sha512(text_to_hash)

            total_iterations += multiplier
            print(f"🔁 [{total_iterations}] {hash_result[:16]}...")

            time.sleep(interval)

        print(f"✅ Finished repeating: {intention} — Total Iterations: {total_iterations}")

    threading.Thread(target=repeat_intention).start()

    return jsonify({
        "success": True,
        "message": f"Intention is now running for {duration} seconds.",
        "intention": intention,
        "frequency": frequency,
        "boost": boost,
        "multiplier": multiplier
    })
📦 Update requirements.txt
Make sure these lines are included:

nginx
Copy
Edit
flask
pandas
rapidfuzz
You do not need to install hashlib — it's built-in.

🧪 Example PowerShell Call (Using All Options)
powershell
Copy
Edit
Invoke-RestMethod -Uri "https://healing-codes-production.up.railway.app/run-intention" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body '{
      "intention": "I am divinely protected",
      "duration": 10,
      "frequency": 2.0,
      "boost": true,
      "multiplier": 3
    }'
