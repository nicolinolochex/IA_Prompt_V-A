import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configurar conexión a SQLite
db_path = "search_history.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla para almacenar historial de búsquedas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        website TEXT,
        ownership TEXT,
        country TEXT,
        brief_description TEXT,
        services TEXT,
        headcount TEXT,
        revenue TEXT,
        linkedin TEXT,
        search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

def save_to_db(company_data):
    """Guarda los datos en SQLite si no existen previamente."""
    cursor.execute("SELECT * FROM company_info WHERE website = ?", (company_data['website'],))
    existing = cursor.fetchone()
    if not existing:
        cursor.execute('''
            INSERT INTO company_info (name, website, ownership, country, brief_description, services, headcount, revenue, linkedin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_data['name'], company_data['website'], company_data['ownership'],
            company_data['country'], company_data['brief_description'], company_data['services'],
            company_data['headcount'], company_data['revenue'], company_data['linkedin']
        ))
        conn.commit()

def get_from_db(website):
    """Busca una empresa en la base de datos SQLite."""
    cursor.execute("SELECT * FROM company_info WHERE website = ?", (website,))
    row = cursor.fetchone()
    if row:
        return {
            "name": row[1], "website": row[2], "ownership": row[3], "country": row[4],
            "brief_description": row[5], "services": row[6], "headcount": row[7], "revenue": row[8], "linkedin": row[9]
        }
    return None

def scrape_web_content(url):
    """Extrae el contenido textual de un sitio web."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text, soup
        else:
            st.error(f"Error al acceder a {url}. Código: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"Error en la extracción de {url}: {e}")
        return None, None

def extract_company_info(content, website_url):
    """Usa GPT-4 para extraer información clave de la empresa."""
    prompt = f"""
    A partir del siguiente contenido, extrae y resume la información:
    Devuelve un JSON con los campos: "name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue".
    Contenido:
    {content}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        info = response.choices[0].message['content']
        return json.loads(info)
    except Exception as e:
        st.error(f"Error en GPT-4: {e}")
        return None

def process_company(company_url):
    """Procesa la empresa y guarda los datos en la BD si no están."""
    cached_data = get_from_db(company_url)
    if cached_data:
        return cached_data
    
    website_text, website_soup = scrape_web_content(company_url)
    if not website_text:
        return None
    
    company_data = extract_company_info(website_text, company_url)
    if company_data:
        linkedin_url = None
        links = website_soup.find_all('a', href=True)
        for link in links:
            if "linkedin.com/company" in link['href']:
                linkedin_url = link['href']
                break
        company_data["linkedin"] = linkedin_url
        save_to_db(company_data)
    return company_data

# ---------------------- Interfaz en Streamlit ----------------------
st.title("Evaluador de Empresas")
st.write("Ingrese hasta 5 URLs de empresas para extraer información.")

url_inputs = [st.text_input(f"Empresa {i+1} URL:") for i in range(5)]
if st.button("Procesar Empresas"):
    urls = [u.strip() for u in url_inputs if u.strip()]
    if not urls:
        st.error("Ingrese al menos una URL válida.")
    else:
        results = [process_company(u) for u in urls if process_company(u)]
        if results:
            df_final = pd.DataFrame(results, columns=["name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue", "linkedin"])
            st.subheader("Información Extraída:")
            st.dataframe(df_final)
            df_final.to_csv("companies_info.csv", index=False, sep=";")
            st.download_button("Descargar CSV", df_final.to_csv(index=False, sep=";"), file_name="companies_info.csv", mime="text/csv")
        else:
            st.error("No se extrajo información.")
