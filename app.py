import openai
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables del archivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------- Funciones de Scraping y Extracción ----------------------

def scrape_web_content(url):
    """
    Scrapes textual content from the given URL.
    Returns a tuple containing the extracted text and the BeautifulSoup object.
    """
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
            print(f"Error: Status code {response.status_code} when accessing {url}")
            return None, None
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return None, None

def find_linkedin_url(soup):
    """
    Searches the BeautifulSoup object for a LinkedIn URL.
    Prioritizes URLs containing 'linkedin.com/company'; otherwise returns the first URL containing 'linkedin.com'.
    """
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
    """
    Cleans the output text from GPT-4 by stripping spaces and removing wrapping markdown (e.g., triple backticks).
    """
    cleaned = text.strip()
    # Si está envuelto en triple backticks, los quitamos.
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned.strip("```").strip()
    return cleaned

def extract_company_info(content, website_url, source="website"):
    """
    Uses GPT-4 to extract and summarize key company information from the provided content.
    
    The extraction includes:
      - Name: The name of the company.
      - Website: The company's website (provided URL).
      - Ownership: Must be one of the following values: "Private", "Public", "Subsidiary", "Acquired", "PE Backed", or "VC Backed".
      - Country: The country where the company's headquarters is located.
      - Brief Description: A short description of what the company does (About Us).
      - Services: The main services offered by the company.
      - Headcount: The approximate number of employees.
      - Revenue: The most recent known or approximate revenue.
      
    The output is expected in JSON format with the keys:
    "name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue".
    """
    if source.lower() == "linkedin":
        source_text = "the LinkedIn page"
    else:
        source_text = "the website content"

    prompt = (
        "Based on the following extracted content from " + source_text + ", please extract and summarize the following company information.\n"
        "Return a valid JSON string with no extra text. The JSON must have the following keys exactly: "
        "\"name\", \"website\", \"ownership\", \"country\", \"brief_description\", \"services\", \"headcount\", \"revenue\".\n\n"
        "Content:\n" + content
    )

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
        print("Error during GPT-4 extraction:", e)
        return None

def merge_info(website_info, linkedin_info):
    """
    Merges the company info from website and LinkedIn.
    For each key, if the LinkedIn value is provided and is not empty or a placeholder (e.g., 'Not specified', 'Not provided'),
    it takes precedence; otherwise, the website value is used.
    This function properly handles values that may be strings or lists.
    """
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

        if is_nonempty(linkedin_value):
            merged[key] = linkedin_value
        else:
            merged[key] = website_value
    return merged

def process_company(company_url):
    """
    Processes a single company's URL: performs scraping, extracts information from both the website and LinkedIn (if available),
    and returns a dictionary with the merged information.
    """
    print(f"\nProcessing company URL: {company_url}")
    
    website_text, website_soup = scrape_web_content(company_url)
    if website_text is None:
        print(f"Could not retrieve content from {company_url}.")
        return {}
    
    extracted_info_website = extract_company_info(website_text, company_url, source="website")
    print("Extracted information from the website:")
    print(extracted_info_website)
    
    cleaned_website_text = clean_extraction(extracted_info_website)
    try:
        website_info = json.loads(cleaned_website_text)
    except Exception as e:
        print("Error parsing website extraction JSON:", e)
        website_info = {}
    
    linkedin_info = {}
    linkedin_url = find_linkedin_url(website_soup)
    if linkedin_url:
        print("Found LinkedIn URL:", linkedin_url)
        linkedin_text, _ = scrape_web_content(linkedin_url)
        if linkedin_text:
            extracted_info_linkedin = extract_company_info(linkedin_text, company_url, source="LinkedIn")
            print("Extracted information from LinkedIn:")
            print(extracted_info_linkedin)
            cleaned_linkedin_text = clean_extraction(extracted_info_linkedin)
            try:
                linkedin_info = json.loads(cleaned_linkedin_text)
            except Exception as e:
                print("Error parsing LinkedIn extraction JSON:", e)
                linkedin_info = {}
        else:
            print("Could not retrieve content from the LinkedIn page.")
    else:
        print("No LinkedIn URL found on the website.")
    
    final_info = merge_info(website_info, linkedin_info)
    return final_info

# ---------------------- Interfaz Interactiva para 5 Empresas ----------------------

# Crear 5 cajas de texto para ingresar las URLs de las empresas.
company_box1 = widgets.Text(
    placeholder='Enter company website URL 1',
    description='Company 1:',
    layout=widgets.Layout(width='80%')
)
company_box2 = widgets.Text(
    placeholder='Enter company website URL 2',
    description='Company 2:',
    layout=widgets.Layout(width='80%')
)
company_box3 = widgets.Text(
    placeholder='Enter company website URL 3',
    description='Company 3:',
    layout=widgets.Layout(width='80%')
)
company_box4 = widgets.Text(
    placeholder='Enter company website URL 4',
    description='Company 4:',
    layout=widgets.Layout(width='80%')
)
company_box5 = widgets.Text(
    placeholder='Enter company website URL 5',
    description='Company 5:',
    layout=widgets.Layout(width='80%')
)

# Botón para iniciar el procesamiento de las 5 empresas.
process_button = widgets.Button(
    description='Process Companies',
    button_style='success'
)

def process_multiple_companies(b):
    clear_output()  # Limpia la salida de la celda para mostrar el resultado final
    # Re-mostrar los widgets
    display(company_box1, company_box2, company_box3, company_box4, company_box5, process_button)
    
    # Obtener las URLs ingresadas y filtrar las que no estén vacías.
    urls = [company_box1.value, company_box2.value, company_box3.value, company_box4.value, company_box5.value]
    urls = [url for url in urls if url.strip() != ""]
    
    results = []
    for url in urls:
        info = process_company(url)
        if info:
            results.append(info)
    
    if results:
        df_final = pd.DataFrame(results, columns=["name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue"])
        print("\nFinal Extracted Company Information Table:")
        print(df_final)
    
        # Guardar el DataFrame como CSV usando ";" como separador.
        output_csv = "companies_info.csv"
        df_final.to_csv(output_csv, index=False, sep=";")
        print(f"\nData has been saved to {output_csv}")
    else:
        print("No company information was extracted.")

process_button.on_click(process_multiple_companies)

# Mostrar los widgets interactivos
display(company_box1, company_box2, company_box3, company_box4, company_box5, process_button)
