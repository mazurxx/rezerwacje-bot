from flask import Flask, request, jsonify
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

app = Flask(__name__)

# === CHATGPT CONFIGURATION ===
openai.api_key = "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"

@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"message": "Brak wiadomości do przetworzenia."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Jesteś serdeczną asystentką w salonie kosmetycznym. Rozmawiasz naturalnie i pomagasz klientkom umawiać się na zabiegi (np. brwi, makijaż ślubny, paznokcie)."
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.85
        )
        reply = response.choices[0].message["content"]
        return jsonify({"message": reply})
    except Exception as e:
        return jsonify({"message": f"Błąd AI: {str(e)}"}), 500

# === GOOGLE SHEETS CONFIGURATION ===

SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID = "1ULiQA-eTZxGG4iAgT80cGALb-Z30HqcbtfBnu9L-QcQ"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(credentials)

# Lista usług i czas trwania w minutach
SERVICE_DURATIONS = {
    "makijaż ślubny": 120,
    "paznokcie hybrydowe": 90,
    "brwi": 30,
    "manicure klasyczny": 60,
    "fryzjer – strzyżenie": 60
}

def get_service_duration(service_name):
    return SERVICE_DURATIONS.get(service_name.lower())

def find_available_slot(slots, duration):
    slot_length = 30
    required_slots = duration // slot_length

    for i in range(len(slots) - required_slots + 1):
        group = slots[i:i+required_slots]
        if all(s['status'].lower() == 'wolny' for s in group):
            same_day = all(s['data'] == group[0]['data'] for s in group)
            consecutive = True
            for j in range(len(group) - 1):
                t1 = datetime.strptime(group[j]['godzina'], '%H:%M')
                t2 = datetime.strptime(group[j+1]['godzina'], '%H:%M')
                if (t2 - t1) != timedelta(minutes=30):
                    consecutive = False
                    break
            if same_day and consecutive:
                return group[0]
    return None

@app.route("/hook", methods=["POST"])
def hook():
    data = request.get_json()
    service_name = data.get("usluga")

    duration = get_service_duration(service_name)
    if not duration:
        return jsonify({"message": f"Nie znam takiej usługi: {service_name}"}), 400

    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
    slots = sheet.get_all_records()

    found_slot = find_available_slot(slots, duration)
    if found_slot:
        return jsonify({
            "message": f"Najbliższy termin na '{service_name}' to {found_slot['data']} o {found_slot['godzina']}."
        })
    else:
        return jsonify({"message": "Brak dostępnych terminów w najbliższym czasie."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
