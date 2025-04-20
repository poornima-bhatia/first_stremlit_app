import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Website Report Analysis", page_icon="🔍")
st.title("🔍 Website Report Analysis")
st.write("Niche format mein website input dein:")
st.code("reportanalysis@www.example.com")
st.code("https://www.example.com")

def get_valid_url(user_input):
    if user_input.startswith("reportanalysis@"):
        domain = user_input.split("@")[1]
        return "https://" + domain
    elif user_input.startswith("http"):
        return user_input
    else:
        return None

def analyze(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "No title found"
        meta = soup.find('meta', attrs={'name': 'description'})
        description = meta['content'].strip() if meta and 'content' in meta.attrs else "No meta description"

        headers = []
        for tag in ['h1', 'h2', 'h3']:
            headers.extend([h.get_text(strip=True) for h in soup.find_all(tag)])

        return title, description, headers
    except Exception as e:
        return None, str(e), []

user_input = st.text_input("🔗 Website URL ya reportanalysis@domain likhein:")

if user_input:
    url = get_valid_url(user_input)
    if url:
        st.info(f"Fetching: {url}")
        title, description, headers = analyze(url)

        if title is None:
            st.error(f"Error fetching website: {description}")
        else:
            st.subheader("✅ Report")
            st.markdown(f"**Title:** {title}")
            st.markdown(f"**Meta Description:** {description}")
            st.markdown("**Headers (H1, H2, H3):**")
            for h in headers:
                st.markdown(f"- {h}")
    else:
        st.error("❌ Format galat hai. Use 'reportanalysis@domain' ya 'https://...'")
