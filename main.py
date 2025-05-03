
from flask import Flask, request, jsonify
from utils import get_service_duration, find_available_slot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Konfiguracja dostępu do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

# ID arkusza
SPREADSHEET_ID = "1ULiQA-eTZxGG4iAgT80cGALb-Z30HqcbtfBnu9L-QcQ"

@app.route("/hook", methods=["POST"])
def webhook():
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
    app.run(debug=True)
