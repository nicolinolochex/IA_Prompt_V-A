import subprocess
import sqlite3
import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
from dotenv import load_dotenv
import yfinance as yf
import urllib.parse
import tldextract





# Load environment variables
load_dotenv()
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Estimated token cost for GPT-4
COST_PER_1K_TOKENS = 0.03

FALLBACK_TICKERS = {
    # Formato:
    # "dominio_principal_de_la_empresa": "TICKER_BURSÁTIL"

    # -----------------------------------------------------
    # ------------------- Ejemplos de Empresas ------------
    # -----------------------------------------------------

    # Tecnología
    "apple.com": "AAPL",
    "microsoft.com": "MSFT",
    "google.com": "GOOGL",   # google.com => GOOGL
    "alphabet.com": "GOOG",  # a veces la web es alphabet.com
    "amazon.com": "AMZN",
    "tesla.com": "TSLA",
    "meta.com": "META",
    "ibm.com": "IBM",
    "intel.com": "INTC",
    "amd.com": "AMD",
    "nvidia.com": "NVDA",
    "salesforce.com": "CRM",
    "adobe.com": "ADBE",
    "oracle.com": "ORCL",
    "paypal.com": "PYPL",
    "zoom.us": "ZM",
    "netflix.com": "NFLX",
    "hp.com": "HPQ",
    "cisco.com": "CSCO",

    # Finanzas/Bancos
    "jpmorganchase.com": "JPM",
    "chase.com": "JPM",
    "goldmansachs.com": "GS",
    "bankofamerica.com": "BAC",
    "bofa.com": "BAC",
    "citigroup.com": "C",
    "wellsfargo.com": "WFC",
    "hsbc.com": "HSBC",
    "barclays.co.uk": "BCS",

    # Consumo/Alimentación
    "coca-colacompany.com": "KO",
    "pepsico.com": "PEP",
    "nestle.com": "NSRGY",  # ADR
    "unilever.com": "UL",
    "kraftheinzcompany.com": "KHC",
    "mondelezinternational.com": "MDLZ",
    "danone.com": "DANOY",   # ADR
    "tyson.com": "TSN",

    # Automotriz
    "toyota.com": "TM",
    "ford.com": "F",
    "gm.com": "GM",
    "volkswagen.com": "VWAGY", # ADR
    "honda.com": "HMC",
    "bmw.com": "BMWYY",
    "mercedes-benz.com": "MBGYY",

    # Energía/Petróleo
    "exxonmobil.com": "XOM",
    "chevron.com": "CVX",
    "shell.com": "SHEL",
    "bp.com": "BP",
    "totalenergies.com": "TTE",

    # Retail
    "walmart.com": "WMT",
    "costco.com": "COST",
    "homedepot.com": "HD",
    "lowes.com": "LOW",
    "target.com": "TGT",
    "bestbuy.com": "BBY",
    "nike.com": "NKE",
    "adidas.com": "ADDYY",  # ADR
    "zalando.com": "ZLNDY", # ADR

    # Farmacéuticas/Salud
    "pfizer.com": "PFE",
    "johnsonandjohnson.com": "JNJ",
    "moderna.com": "MRNA",
    "astrazeneca.com": "AZN",
    "novartis.com": "NVS",
    "merck.com": "MRK",
    "bayer.com": "BAYRY",
    "sanofi.com": "SNY",

    # Aeroespacial/Defensa
    "boeing.com": "BA",
    "lockheedmartin.com": "LMT",
    "raytheon.com": "RTX",
    "airbus.com": "EADSY",
    "northropgrumman.com": "NOC",

    # Telecomunicaciones
    "verizon.com": "VZ",
    "att.com": "T",
    "vodafone.com": "VOD",
    "telefonica.com": "TEF",

    # Transporte/Logística
    "ups.com": "UPS",
    "fedex.com": "FDX",
    "dhl.com": "DPSTF",
    "maersk.com": "AMKBY",

    # Bienes Raíces/Constructora
    "cbreglobal.com": "CBRE",
    "realogy.com": "HOUS",
    "lennar.com": "LEN",
    "drhorton.com": "DHI",
    "pultegroup.com": "PHM",

    # Diversas/OTRAS
    "berkshirehathaway.com": "BRK-B",
    "didi.com": "DIDIY",
    "alibaba.com": "BABA",
    "jd.com": "JD",
    "baidu.com": "BIDU",
    "united.com": "UAL",   # United Airlines
    "southwest.com": "LUV",
    "marriott.com": "MAR",
    "booking.com": "BKNG",
    "accenture.com": "ACN",
    "3m.com": "MMM",
    "ecopetrol.com.co": "EC"
}

# ---------------------- Initialize Database ----------------------
def init_db():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS searches (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      company_url TEXT,
                      linkedin_url TEXT,
                      name TEXT,
                      website TEXT,
                      ownership TEXT,
                      country TEXT,
                      brief_description TEXT,
                      services TEXT,
                      headcount TEXT,
                      revenue TEXT,
                      date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()
    conn.close()

init_db()

# ---------------------- Web Scraping Functions ----------------------
def scrape_web_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text, soup
        else:
            st.error(f"Error: Status code {response.status_code} when accessing {url}")
            return None, None
    except Exception as e:
        st.error(f"Error accessing {url}: {e}")
        return None, None

def find_linkedin_url(soup):
    """Finds the LinkedIn URL from the scraped website."""
    if soup is None:
        return None
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if "linkedin.com/company" in href:
            return href
    for link in links:
        href = link['href']
        if "linkedin.com" in href:
            return href
    return None

def extract_company_info(content, website_url, source="website"):
    if not content or len(content) < 50:
        st.warning("Insufficient content extracted for GPT analysis.")
        return None

    # Construir prompt según idioma
    if lang == "Español":
        system_msg = "Eres un asistente experto en valoración y adquisición de empresas. Genera resultados en Español."
        prompt = f"""
        Extrae y resume la siguiente información de la empresa del contenido proporcionado ({source}).
        Devuelve SOLO un JSON válido con las claves: name, website, ownership, country, brief_description, services, headcount, revenue, ticker.
        Contenido:
        {content[:4000]}
        """
    else:
        system_msg = "You are an expert in company valuation and acquisitions. Return output in English."
        prompt = f"""
        Extract and summarize the following company information from the provided {source} content.
        Return ONLY a valid JSON with keys: name, website, ownership, country, brief_description, services, headcount, revenue, ticker.
        Content:
        {content[:4000]}
        """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"Error during GPT-4 extraction: {e}")
        return None


def safe_parse(raw):
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}

def fetch_financials(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice"),
            "year_change_pct": info.get("52WeekChange"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume")
        }
    except Exception:
        return {}
    

def lookup_ticker_by_name(name: str) -> str | None:
    query = urllib.parse.quote(name)
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        quotes = resp.json().get("quotes", [])
        return quotes[0].get("symbol") if quotes else None
    except Exception:
        return None


def lookup_ticker_by_name(name: str) -> str | None:
    query = urllib.parse.quote(name)
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        quotes = resp.json().get("quotes", [])
        return quotes[0].get("symbol") if quotes else None
    except Exception:
        return None


def process_company(company_url):
    st.info(f"Processing company: {company_url}")
    website_text, website_soup = scrape_web_content(company_url)
    if not website_text:
        return {}

    # Extraer info GPT
    website_raw = extract_company_info(website_text, company_url, source="website")
    website_info = safe_parse(website_raw)

    # LinkedIn
    linkedin_url = find_linkedin_url(website_soup)
    linkedin_info = {}
    if linkedin_url:
        linkedin_text, _ = scrape_web_content(linkedin_url)
        if linkedin_text:
            linkedin_raw = extract_company_info(linkedin_text, company_url, source="LinkedIn")
            linkedin_info = safe_parse(linkedin_raw)

    final_info = {**website_info, **linkedin_info, "linkedin_url": linkedin_url}

    # 1) Tomar ticker desde GPT
    ticker = final_info.get("ticker")

    # 1.b) Si GPT devolvió algo como "Data not provided", limpiarlo a None
    invalid_tickers = ["Data not provided", "Not provided", "N/A", "", None]
    if ticker and ticker.lower() in ["data not provided", "not provided", "n/a", ""]:
        ticker = None

    # 2) Si GPT no lo dio, buscar en Yahoo Finance con el nombre
    if not ticker:
        name_for_lookup = final_info.get("name", "")
        ticker_from_yahoo = lookup_ticker_by_name(name_for_lookup)
        if ticker_from_yahoo:
            ticker = ticker_from_yahoo
            final_info["ticker"] = ticker

    # 3) Si ni GPT ni lookup lo dieron, fallback manual por dominio
# 3) Si ni GPT ni lookup lo dieron, fallback manual por dominio
    if not ticker:
        domain_parts = tldextract.extract(company_url)
        domain = f"{domain_parts.domain}.{domain_parts.suffix}"
        fallback = FALLBACK_TICKERS.get(domain)
        if fallback:
            ticker = fallback
            final_info["ticker"] = ticker


    # 4) Si al final tenemos ticker, trae datos financieros
    if ticker:
        st.write(f"Ticker final => {ticker}")
        final_info.update(fetch_financials(ticker))

    # Guardar en DB
    save_search_to_db(company_url, linkedin_url, final_info)
    return final_info


def save_search_to_db(company_url, linkedin_url, data):
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    try:
        params = (
            company_url,
            linkedin_url,
            str(data.get("name", "")),
            str(data.get("website", "")),
            str(data.get("ownership", "")),
            str(data.get("country", "")),
            str(data.get("brief_description", "")),
            str(data.get("services", "")),
            str(data.get("headcount", "")),
            str(data.get("revenue", ""))
        )
        cursor.execute(
            """
            INSERT INTO searches (
                company_url, linkedin_url, name, website, ownership,
                country, brief_description, services, headcount, revenue
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            params
        )
        conn.commit()
    except sqlite3.ProgrammingError as e:
        st.error(f"Database insert error: {e}")
        import logging; logging.exception("DB insert failed")
    finally:
        conn.close()


# ---------------------- Streamlit UI ----------------------
# URL de la foto de perfil de LinkedIn
linkedin_image_url = "https://media.licdn.com/dms/image/v2/D4E03AQHFFEQls8Yz-w/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1702933383349?e=1746662400&v=beta&t=tYwSt2scB5uEJfWvlLdg19ycRkfvAFGRNj1X3JcNGOc"

# CSS para centrar la imagen
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; margin-bottom: 10px;">
        <img src="{linkedin_image_url}" width="120" style="border-radius: 50%;">
    </div>
    """, 
    unsafe_allow_html=True
)

# Muestra tu nombre centrado
st.sidebar.markdown("<h4 style='text-align: center;'>Catriel Nicolas Arandiga</h4>", unsafe_allow_html=True)

# URL del icono de LinkedIn
linkedin_icon_url = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

# Agrega el enlace a LinkedIn con icono
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <a href="https://www.linkedin.com/in/catriel-nicolas-arandiga" target="_blank" style="font-size: 16px; text-decoration: none; display: flex; align-items: center;">
            <img src="{linkedin_icon_url}" width="20" style="margin-right: 5px;"/> LinkedIn Profile
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)
lang = st.sidebar.selectbox("Idioma de salida", ["Original", "Español"])

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Company Search"])

st.sidebar.markdown("""
## Descripción de la App

Esta herramienta automatiza el **research de empresas** para adquisiciones, reduciendo horas de trabajo manual.

➡️ **Cómo funciona:**  
1. Ingresás URLs de sitios corporativos o perfiles de LinkedIn.  
2. El sistema extrae datos clave (headcount, revenue, servicios, país) mediante web scraping.  
3. GPT‑4 procesa esa información, genera un resumen estructurado y asigna un puntaje según tus criterios predefinidos.
🎯 **Objetivo:**  
Acelerar la obtención de insights confiables, mejorar la precisión de los datos y facilitar decisiones estratégicas.
""", unsafe_allow_html=True)



if page == "Company Search":
    st.title("Company Research Tool")
    urls = [st.text_input(f"Company {i+1} URL:") for i in range(5)]

    if st.button("Process Companies"):
        valid_urls = [u.strip() for u in urls if u.strip()]
        if not valid_urls:
            st.error("Please enter at least one valid company URL.")
        else:
            st.session_state.df = pd.DataFrame([process_company(url) for url in valid_urls])

    # Si ya hay resultados en session_state, los mostramos (incluso tras cambiar el selectbox)
    if "df" in st.session_state:
        df = st.session_state.df

        # Normalizar estructuras complejas
        for col in df.columns:
            df[col] = df[col].apply(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)

        st.dataframe(df)

        # Fundamentals Económicos
        for col in ["name", "market_cap", "current_price", "year_change_pct"]:
            if col not in df.columns:
                df[col] = None

        st.subheader("Fundamentals Económicos")
        st.dataframe(df[["name","market_cap","current_price","year_change_pct"]])

         # Gráfico con medias móviles (persistente)
        if "ticker" in df.columns and df["ticker"].notna().any():
            selected_ticker = st.selectbox(
                "Selecciona ticker para gráfico",
                df["ticker"].dropna().unique()
            )

            try:
                hist = yf.Ticker(selected_ticker).history(period="1y")
                if hist.empty:
                    raise ValueError("No hay datos históricos disponibles")

                hist["MA50"] = hist["Close"].rolling(50).mean()
                hist["MA200"] = hist["Close"].rolling(200).mean()

                st.subheader(f"Evolución Precio y Medias Móviles — {selected_ticker}")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.plot(hist.index, hist["Close"], label="Precio cierre")
                ax.plot(hist.index, hist["MA50"], label="MA50")
                ax.plot(hist.index, hist["MA200"], label="MA200")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Precio (USD)")
                ax.legend()
                st.pyplot(fig)

                csv_data = hist.to_csv()
                st.download_button(
                    "Descargar datos históricos (CSV)",
                    csv_data,
                    file_name=f"{selected_ticker}_history.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"No se pudieron obtener datos históricos para {selected_ticker}: {e}")

        df.to_csv("companies_info.csv", index=False, sep=";")
        st.download_button(
            "Download CSV",
            df.to_csv(index=False, sep=";"),
            file_name="companies_info.csv",
            mime="text/csv"
        )

