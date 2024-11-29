from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import os

import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
# Uložení souboru
SAVE_DIR = "results"
os.makedirs(SAVE_DIR, exist_ok=True)


# Hlavni stranka
@app.route('/')
def home():
    return render_template('index.html')


# Sprácovani požadavku
@app.route('/search', methods=['POST'])
def search_google_and_save():
    try:
        query = request.form.get('query')
        if not query:
            return "Parametr 'query' je povinný!", 400

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        search_url = f"https://www.google.com/search?q={query}&hl=en"
        logging.debug(f"URL: {search_url}")  # Logovani URL
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            return "Chyba při provádění požadavku!", 500

        soup = BeautifulSoup(response.text, 'html.parser')
        first_result = soup.select_one('.tF2Cxc')
        if not first_result:
            return "Výsledky se nepodařilo najít!", 404

        title = first_result.select_one('.DKV0Md').text
        link = first_result.select_one('.yuRUbf a')['href']
        snippet = first_result.select_one('.VwiC3b').text if first_result.select_one(
            '.VwiC3b') else "Bez popisu."

        # Uloženi dat do souboru
        filename = f"{SAVE_DIR}/{query.replace(' ', '_')}_result.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Záhlaví: {title}\n")
            file.write(f"Odkaz: {link}\n")
            file.write(f"Popis: {snippet}\n")

        # Odeslání souboru uživateli ke stažení
        return send_file(filename, as_attachment=True)

    except Exception as e:
        logging.error(f"Chyba při zpracování požadavku: {e}")
        return "Interní chyba serveru.", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
