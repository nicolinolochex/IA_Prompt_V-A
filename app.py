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
    """Extracts company information using GPT-4."""
    if not content or len(content) < 50:
        st.warning("Insufficient content extracted for GPT analysis.")
        return None
    
    language_clause = "" if lang == "Original" else " Return all output in Spanish."

    prompt = f"""
    Extract and summarize the following company information from the provided {source} content.
    Return a valid JSON with these keys: "name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue", "ticker".
    Content:
    {content[:4000]}  # Limit content size
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Eres un asistente experto en valoración y adquisición de empresas. Dominas métricas financieras y de negocio (KPIs) como revenue, headcount, crecimiento, rentabilidad, sostenibilidad y posición de mercado. Identificas automáticamente la información más relevante de sitios web y perfiles corporativos, la estructuras en formato JSON limpio y generas insights claros que faciliten decisiones estratégicas de M&A."},
            {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
)

        info = response["choices"][0]["message"]["content"].strip()
        token_usage = response["usage"]["total_tokens"]
        cost_estimate = (token_usage / 1000) * COST_PER_1K_TOKENS
        st.write(f"Estimated GPT-4 cost: ${cost_estimate:.4f}")
        return info
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
            "year_change_pct": info.get("52WeekChange")
        }
    except Exception:
        return {}

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

