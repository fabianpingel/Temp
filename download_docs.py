import os
import json
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import re

INPUT_JSON = "imu-faktendatenbank.json"
DOWNLOAD_DIR = Path("data")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def sanitize_filename(name: str) -> str:
    """
    Entfernt Sonderzeichen und Umlaute aus Dateinamen
    """
    # Umlaute ersetzen
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    # alles, was kein Buchstabe, Zahl, Unterstrich oder Punkt ist, ersetzen
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    return name

def extract_filename_from_url(url: str) -> str:
    """
    Extrahiert einen sinnvollen Dateinamen aus der URL
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # bevorzugt ?doc=XYZ.pdf
    if "doc" in qs and qs["doc"]:
        return qs["doc"][0]

    # Fallback: letzter Pfadteil
    return os.path.basename(parsed.path) or "download.pdf"

def download_documents():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        projekte = json.load(f)

    for projekt in projekte:
        titel = projekt.get("Titel", "Unbenanntes_Projekt")
        projekt_ordner = DOWNLOAD_DIR / sanitize_filename(titel)
        projekt_ordner.mkdir(exist_ok=True)

        # Alle Dokumenten-URLs einsammeln
        document_urls = set()
        for key, value in projekt.items():
            if key.startswith("documents_") and isinstance(value, list):
                document_urls.update(value)
        
        if not document_urls:
            print(f"ℹ Keine Dokumente für Projekt: {titel}")
            continue

        # Ordner erstellen
        raw_filename = f"{projekt['Titel']}"
        filename = sanitize_filename(raw_filename)
        docs_path = DOWNLOAD_DIR / filename
        docs_path.mkdir(exist_ok=True)
        
        for url in document_urls:
            try:
                full_url = urljoin("https://www.massivumformung.de", url)
                raw_name = extract_filename_from_url(url)
                filename = sanitize_filename(raw_name)
                filepath = projekt_ordner / filename

                if filepath.exists():
                    print(f"↺ Bereits vorhanden: {filename}")
                    continue

                response = requests.get(full_url, timeout=20)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"✓ Heruntergeladen: {filename}")

            except requests.exceptions.RequestException as e:
                print(f"✗ HTTP-Fehler bei {url}: {e}")
            except OSError as e:
                print(f"✗ Dateifehler bei {filename}: {e}")
            except Exception as e:
                print(f"✗ Unerwarteter Fehler bei {url}: {e}")

if __name__ == "__main__":
    download_documents()
