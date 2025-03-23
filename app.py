import sqlite3
import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# ---------------------- Helper Functions ----------------------
def safe_parse(raw_str):
    try:
        return json.loads(raw_str)
    except (TypeError, json.JSONDecodeError) as e:
        st.warning(f"JSON parse error: {e}")
        return {}

# ---------------------- Web Scraping Functions ----------------------
def scrape_web_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True), soup
    except Exception as e:
        st.error(f"Error accessing {url}: {e}")
        return None, None

def find_linkedin_url(soup):
    if not soup: return None
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'linkedin.com/company' in href:
            return href
    return None

# ---------------------- GPT Extraction ----------------------
def extract_company_info(content, source="website"):
    if not content or len(content) < 50:
        st.warning("Insufficient content for GPT analysis.")
        return None
    prompt = f"""
Extract and summarize the following company information from the provided {source} content.
Return ONLY a valid JSON object with keys: name, website, ownership, country, brief_description, services, headcount, revenue.
Content:
{content[:4000]}
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in company valuation and acquisitions, adept at extracting KPIs and business metrics from web content and structuring them as clean JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        result = resp['choices'][0]['message']['content'].strip()
        tokens = resp['usage']['total_tokens']
        st.write(f"Estimated GPT-4 cost: ${(tokens/1000)*COST_PER_1K_TOKENS:.4f}")
        return result
    except Exception as e:
        st.error(f"GPT extraction error: {e}")
        return None

# ---------------------- Data Processing ----------------------
def process_company(company_url):
    st.info(f"Processing: {company_url}")
    website_text, website_soup = scrape_web_content(company_url)
    if not website_text:
        return {}

    website_json = extract_company_info(website_text, source="website")
    website_info = safe_parse(website_json)

    linkedin_url = find_linkedin_url(website_soup)
    linkedin_info = {}
    if linkedin_url:
        linkedin_text, _ = scrape_web_content(linkedin_url)
        linkedin_json = extract_company_info(linkedin_text, source="LinkedIn")
        linkedin_info = safe_parse(linkedin_json)

    final = {**website_info, **linkedin_info, "linkedin_url": linkedin_url}
    save_search_to_db(company_url, linkedin_url, final)
    return final

# ---------------------- Database Save ----------------------
def save_search_to_db(company_url, linkedin_url, data):
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO searches(company_url, linkedin_url, name, website, ownership, country, brief_description, services, headcount, revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_url,
                linkedin_url,
                data.get("name", ""),
                data.get("website", ""),
                data.get("ownership", ""),
                data.get("country", ""),
                data.get("brief_description", ""),
                data.get("services", ""),
                data.get("headcount", ""),
                data.get("revenue", "")
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"DB insert error: {e}")
    finally:
        conn.close()
