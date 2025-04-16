
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.astagiudiziaria.com"
START_URL = f"{BASE_URL}/inserzioni"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_price(price_str):
    price_str = price_str.replace('.', '').replace(',', '.').replace('€', '').strip()
    try:
        return float(price_str)
    except:
        return None

def calculate_reduction(original, current):
    if original and current and original != 0:
        return ((original - current) / original) * 100
    return 0

def get_listing_urls(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    links = soup.select('a[href^="/inserzioni/"]')
    urls = set(BASE_URL + a['href'] for a in links if 'href' in a.attrs)
    return list(urls)

def analyze_listing(url, threshold):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        storico = soup.find("section", id="storico-aste") or soup.find("div", class_="storico-aste")
        if not storico:
            return []

        results = []
        rows = storico.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 3:
                data = cells[0].get_text(strip=True)
                prezzo_originale = parse_price(cells[1].get_text())
                prezzo_corrente = parse_price(cells[2].get_text())
                riduzione = calculate_reduction(prezzo_originale, prezzo_corrente)
                if riduzione >= threshold:
                    results.append({
                        "URL": url,
                        "Data": data,
                        "Prezzo Originale": prezzo_originale,
                        "Prezzo Corrente": prezzo_corrente,
                        "Riduzione (%)": round(riduzione, 2)
                    })
        return results
    except:
        return []

def get_total_pages():
    res = requests.get(START_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    last_page_link = soup.select_one('ul.pagination li:last-child a')
    if last_page_link:
        try:
            return int(last_page_link.text.strip())
        except:
            pass
    return 1

def scan_all_pages(threshold):
    total_pages = get_total_pages()
    all_results = []
    for page in range(1, total_pages + 1):
        page_url = f"{START_URL}?page={page}"
        try:
            res = requests.get(page_url, headers=HEADERS)
            listing_urls = get_listing_urls(res.text)
            for url in listing_urls:
                results = analyze_listing(url, threshold)
                all_results.extend(results)
                time.sleep(0.5)
        except:
            continue
    return all_results

st.title("📉 Analizzatore Aste Giudiziarie")

threshold = st.number_input("Inserisci la soglia minima di riduzione (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5)

if st.button("Avvia analisi"):
    st.info("Analisi in corso... potrebbe richiedere alcuni minuti.")
    data = scan_all_pages(threshold)
    if data:
        df = pd.DataFrame(data)
        st.success(f"Trovate {len(df)} aste con riduzione ≥ {threshold:.1f}%")
        st.download_button("📥 Scarica CSV", data=df.to_csv(index=False), file_name="risultati_aste.csv", mime="text/csv")
        st.dataframe(df)
    else:
        st.warning("Nessuna asta trovata con la riduzione specificata.")
