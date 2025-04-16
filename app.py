import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("🔗 Estrazione URL Aste Giudiziarie (In scadenza)")

def estrai_url_aste():
    url = "https://www.astagiudiziaria.com/ricerca?filter%5Bstatus%5D%5B0%5D=In%20vendita&filter%5Bvisibile_su%5D%5B0%5D=1&filter%5Bposition%5D=&query=&page=1&rpp=100&sort%5Bkey%5D=data_vendita_search&sort%5Bvalue%5D=asc"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select('a[href^="/inserzioni/"]')
        base_url = "https://www.astagiudiziaria.com"
        urls = list({base_url + a['href'] for a in links if "/inserzioni/" in a['href'] and not a['href'].endswith("#")})
        return urls
    except Exception as e:
        st.error(f"Errore durante la richiesta: {e}")
        return []

if st.button("Estrai URL delle aste"):
    st.info("Analisi in corso... attendi qualche secondo.")
    urls = estrai_url_aste()
    if urls:
        st.success(f"Trovati {len(urls)} URL.")
        for url in urls:
            st.write(url)
    else:
        st.warning("Nessun URL trovato.")