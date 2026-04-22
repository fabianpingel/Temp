import requests
import re
import json

URL = r"https://www.massivumformung.de/llm/"
OUTPUT_JSON = "imu-faktendatenbank.json"

def finde_json_string(text):
    # Sucht nach JSON-ähnlichem Inhalt in eckigen Klammern [ ... ]
    match = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def parse_webseite(url):
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    json_roh = finde_json_string(html)
    if not json_roh:
        print("❌ Kein JSON-Block im Quelltext gefunden.")
        return

    try:
        daten = json.loads(json_roh)
    except json.JSONDecodeError as e:
        print(f"❌ JSON konnte nicht geladen werden: {e}")
        return

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON gespeichert in '{OUTPUT_JSON}'")


if __name__ == "__main__":   
    parse_webseite(URL)
