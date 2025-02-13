import subprocess

# Instalar openai si no está presente
try:
    import openai
except ModuleNotFoundError:
    subprocess.run(["pip", "install", "openai"])
    import openai  # Reintenta la importación

import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------- Funciones de Scraping y Extracción ----------------------

def scrape_web_content(url):
    """Scrapes textual content from the given URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
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

def clean_extraction(text):
    """Cleans extracted JSON response from GPT-4."""
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned.strip("```").strip()
    return cleaned

def extract_company_info(content, website_url, source="website"):
    """Extracts company information using GPT-4."""
    if source.lower() == "linkedin":
        source_text = "the LinkedIn page"
    else:
        source_text = "the website content"

    prompt = f"""
    Based on the following extracted content from {source_text}, please extract and summarize the following company information.
    Return a valid JSON string with no extra text. The JSON must have the following keys exactly:
    "name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue".

    Content:
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
        return info
    except Exception as e:
        st.error(f"Error during GPT-4 extraction: {e}")
        return None

def merge_info(website_info, linkedin_info):
    """Merges extracted company info from website and LinkedIn."""
    merged = {}
    keys = ["name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue"]

    def is_nonempty(val):
        if val is None:
            return False
        if isinstance(val, str):
            return val.strip() and val.strip().lower() not in ["not specified", "not provided", ""]
        if isinstance(val, list):
            return len(val) > 0
        return True

    for key in keys:
        website_value = website_info.get(key, None) if website_info else None
        linkedin_value = linkedin_info.get(key, None) if linkedin_info else None
        merged[key] = linkedin_value if is_nonempty(linkedin_value) else website_value
    return merged

def process_company(company_url):
    """Processes a single company URL, scraping data from the website and LinkedIn."""
    st.info(f"Processing company: {company_url}")

    website_text, website_soup = scrape_web_content(company_url)
    if website_text is None:
        st.error(f"Could not retrieve content from {company_url}.")
        return {}

    extracted_info_website = extract_company_info(website_text, company_url, source="website")
    cleaned_website_text = clean_extraction(extracted_info_website)

    try:
        website_info = json.loads(cleaned_website_text)
    except Exception as e:
        st.error(f"Error parsing website JSON: {e}")
        website_info = {}

    linkedin_info = {}
    linkedin_url = find_linkedin_url(website_soup)
    if linkedin_url:
        st.write(f"Found LinkedIn URL: {linkedin_url}")
        linkedin_text, _ = scrape_web_content(linkedin_url)
        if linkedin_text:
            extracted_info_linkedin = extract_company_info(linkedin_text, company_url, source="LinkedIn")
            cleaned_linkedin_text = clean_extraction(extracted_info_linkedin)
            try:
                linkedin_info = json.loads(cleaned_linkedin_text)
            except Exception as e:
                st.error(f"Error parsing LinkedIn JSON: {e}")
                linkedin_info = {}
        else:
            st.error("Could not retrieve content from LinkedIn.")
    else:
        st.warning("No LinkedIn URL found on the website.")

    final_info = merge_info(website_info, linkedin_info)
    return final_info

# ---------------------- Interfaz en Streamlit ----------------------

st.title("Company Research Tool")
st.write("Enter up to 5 company website URLs to extract and analyze information.")

# Entradas para URLs
url_inputs = []
for i in range(5):
    url = st.text_input(f"Company {i+1} URL:")
    url_inputs.append(url)

if st.button("Process Companies"):
    urls = [u.strip() for u in url_inputs if u.strip() != ""]
    
    if not urls:
        st.error("Please enter at least one valid company URL.")
    else:
        results = []
        for u in urls:
            info = process_company(u)
            if info:
                results.append(info)

        if results:
            df_final = pd.DataFrame(results, columns=["name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue"])
            st.subheader("Extracted Company Information:")
            st.dataframe(df_final)

            # Guardar el CSV con ";" como separador
            output_csv = "companies_info.csv"
            df_final.to_csv(output_csv, index=False, sep=";")

            st.success(f"Data has been saved to `{output_csv}`.")
            st.download_button("Download CSV", df_final.to_csv(index=False, sep=";"), file_name="companies_info.csv", mime="text/csv")
        else:
            st.error("No information was extracted.")

