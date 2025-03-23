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


# Load environment variables
load_dotenv()
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Estimated token cost for GPT-4
COST_PER_1K_TOKENS = 0.03

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
    """Scrapes textual content from the given URL."""
    headers = {"User-Agent": "Mozilla/5.0"}
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
    
if ticker:
    hist = yf.Ticker(ticker).history(period="1y")
    hist["MA50"] = hist["Close"].rolling(50).mean()
    hist["MA200"] = hist["Close"].rolling(200).mean()

    st.subheader("Evolución Precio (último año) y Medias Móviles")
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
        file_name=f"{ticker}_1y_history.csv",
        mime="text/csv"
    )


def process_company(company_url):
    """Processes a single company URL, extracting website and LinkedIn data."""
    st.info(f"Processing company: {company_url}")
    website_text, website_soup = scrape_web_content(company_url)
    if not website_text:
        return {}

    # Extracción y parseo seguro de la info desde el sitio web
    website_raw = extract_company_info(website_text, company_url, source="website")
    website_info = safe_parse(website_raw)

    linkedin_url = find_linkedin_url(website_soup)
    linkedin_info = {}
    if linkedin_url:
        linkedin_text, _ = scrape_web_content(linkedin_url)
        if linkedin_text:
            linkedin_raw = extract_company_info(linkedin_text, company_url, source="LinkedIn")
            linkedin_info = safe_parse(linkedin_raw)

    final_info = {**website_info, **linkedin_info, "linkedin_url": linkedin_url}
    ticker = final_info.get("ticker")
    if ticker:
        final_info.update(fetch_financials(ticker))

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

lang = st.sidebar.selectbox("Idioma de salida", ["Original", "Español"])

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Company Search", "Search History"])

if page == "Company Search":
    st.title("Company Research Tool")
    st.write("Enter company URLs to analyze and extract information.")

    urls = [st.text_input(f"Company {i+1} URL:") for i in range(5)]

    if st.button("Process Companies"):
        valid_urls = [u.strip() for u in urls if u.strip()]
    if not valid_urls:
        st.error("Please enter at least one valid company URL.")
    else:
        results = [process_company(url) for url in valid_urls]
        df = pd.DataFrame(results)
        st.dataframe(df)

        # Asegura que existan las columnas de fundamentals
        for col in ["market_cap", "current_price", "year_change_pct"]:
            if col not in df.columns:
                df[col] = None

        st.subheader("Fundamentals Económicos")
        st.dataframe(df[["name", "market_cap", "current_price", "year_change_pct"]])
        # —————— Gráfico de precio + medias móviles ——————
        if "ticker" in df.columns and not df["ticker"].dropna().empty:
            selected_ticker = st.selectbox(
                "Selecciona ticker para gráfico",
                df["ticker"].dropna().unique()
            )
            hist = yf.Ticker(selected_ticker).history(period="1y")
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
                file_name=f"{selected_ticker}_1y_history.csv",
                mime="text/csv"
            )

        df.to_csv("companies_info.csv", index=False, sep=";")
        st.download_button(
            "Download CSV",
            df.to_csv(index=False, sep=";"),
            file_name="companies_info.csv",
            mime="text/csv"
        )



elif page == "Search History":
    st.title("Search History")

    conn = sqlite3.connect("history.db")
    df_history = pd.read_sql("SELECT * FROM searches ORDER BY date DESC", conn)
    conn.close()

    search_filter = st.text_input("Filter by company name:")
    if search_filter:
        df_history = df_history[df_history["name"].str.contains(search_filter, case=False, na=False)]

    st.dataframe(df_history)

    if st.button("Back to Search"):
        st.experimental_set_query_params(page="Company Search") 

