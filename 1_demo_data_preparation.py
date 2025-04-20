import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="Website Image Report", page_icon="🖼️")

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("🔍 Website Input")
    user_input = st.text_input("Enter a URL or reportanalysis@domain", "")

# -------------------------------
# Convert input to valid URL
# -------------------------------
def get_valid_url(inp):
    if inp.startswith("http"):
        return inp
    return None

# -------------------------------
# Image Analysis Function
# -------------------------------
def analyze_images(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        images = soup.find_all("img")
        data = []

        for i, img in enumerate(images):
            src = img.get("src")
            alt = img.get("alt", "")

            # Handling cases where alt is missing, empty, or just placeholder
            if alt == "" or alt == "..." or alt is None:
                alt = "No Alt Text"
            
            full_src = urljoin(url, src)
            data.append({
                "index": i + 1,
                "src": full_src,
                "has_alt": bool(alt.strip()),  # Ensure 'has_alt' column is populated
                "alt_text": alt.strip()
            })

        df = pd.DataFrame(data)

        if df.empty:
            return None, "No images found on the page."
        else:
            return df, response.status_code

    except Exception as e:
        return None, str(e)

# -------------------------------
# Main Display
# -------------------------------
if user_input:
    url = get_valid_url(user_input)
    if url:
        st.markdown(f"### 🔗 Analyzing: [{url}]({url})")

        df, status = analyze_images(url)

        if df is None:
            st.error(f"❌ Error: {status}")
        else:
            total = len(df)
            with_alt = df['has_alt'].sum()  # Calculate the number of images with alt text
            missing_alt = total - with_alt

            # --------- Top Metrics ---------
            col1, col2, col3 = st.columns(3)
            col1.metric("🖼️ Total Images", total)
            col2.metric("✅ With Alt Text", with_alt)
            col3.metric("⚠️ Missing Alt", missing_alt)

            # --------- Bar Plot ---------
            st.subheader("📊 Alt Text Distribution")
            fig, ax = plt.subplots()
            ax.bar(["With Alt", "Missing Alt"], [with_alt, missing_alt], color=["green", "red"])
            st.pyplot(fig)

            # --------- Status Code ---------
            st.subheader("✅ Status Code Summary")

            # Dictionary for status descriptions
            status_descriptions = {
                200: "OK – Website loaded successfully.",
                301: "Moved Permanently – The page was redirected.",
                302: "Found – Temporary redirection.",
                400: "Bad Request – Client error.",
                403: "Forbidden – You don’t have permission.",
                404: "Not Found – Page does not exist.",
                500: "Internal Server Error – Something broke on the server.",
                502: "Bad Gateway – Invalid response from upstream.",
                503: "Service Unavailable – Server is temporarily busy."
            }

            desc = status_descriptions.get(status, "Unknown or uncommon status code.")
            st.info(f"Website responded with **HTTP `{status}`** – {desc}")

            # --------- Detailed Table ---------
            st.subheader("📋 Image Table")
            def show_image(src):
                try:
                    response = requests.get(src, timeout=5)
                    img = Image.open(BytesIO(response.content))
                    return img
                except:
                    return "❌"

            df_display = df.copy()
            df_display["Preview"] = df_display["src"].apply(lambda x: show_image(x))
            df_display = df_display[["index", "Preview", "has_alt", "alt_text"]]

            st.dataframe(df_display, use_container_width=True)

    else:
        st.warning("❌ Invalid input. Please use full URL.")
