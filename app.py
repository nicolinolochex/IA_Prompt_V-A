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

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Estimated cost per 1K tokens in GPT-4
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
    
    prompt = f"""
    Extract and summarize the following company information from the provided {source} content.
    Return a valid JSON with these keys: "name", "website", "ownership", "country", "brief_description", "services", "headcount", "revenue".
    Content:
    {content[:4000]}  # Limit content size
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
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


def process_company(company_url):
    """Processes a single company URL, extracting website and LinkedIn data."""
    st.info(f"Processing company: {company_url}")
    website_text, website_soup = scrape_web_content(company_url)
    if not website_text:
        return {}
    
    website_info = extract_company_info(website_text, company_url, source="website")
    website_info = json.loads(website_info) if website_info else {}
    
    linkedin_url = find_linkedin_url(website_soup)
    linkedin_info = {}
    if linkedin_url:
        linkedin_text, _ = scrape_web_content(linkedin_url)
        if linkedin_text:
            linkedin_info = extract_company_info(linkedin_text, company_url, source="LinkedIn")
            linkedin_info = json.loads(linkedin_info) if linkedin_info else {}
    
    final_info = {**website_info, **linkedin_info, "linkedin_url": linkedin_url}
    save_search_to_db(company_url, linkedin_url, final_info)
    return final_info


def save_search_to_db(company_url, linkedin_url, data):
    """Saves the search result to the database."""
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO searches (company_url, linkedin_url, name, website, ownership, country, brief_description, services, headcount, revenue)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_url, linkedin_url,
        data.get("name"), data.get("website"), data.get("ownership"),
        data.get("country"), data.get("brief_description"),
        data.get("services"), data.get("headcount"), data.get("revenue")
    ))
    conn.commit()
    conn.close()

# ---------------------- Streamlit Interface ----------------------
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
            df.to_csv("companies_info.csv", index=False, sep=";")
            st.download_button("Download CSV", df.to_csv(index=False, sep=";"), file_name="companies_info.csv", mime="text/csv")

elif page == "Search History":
    st.title("Search History")
    conn = sqlite3.connect("history.db")
    df = pd.read_sql_query("SELECT * FROM searches ORDER BY date DESC", conn)
    conn.close()
    search_filter = st.text_input("Filter by company name:")
    if search_filter:
        df = df[df["name"].str.contains(search_filter, case=False, na=False)]
    st.dataframe(df)
    st.button("Back to Search", on_click=lambda: st.sidebar.radio("Go to:", ["Company Search"]))
