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
    user_input = st.text_input("Enter a URL", "")

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
            fig, ax = plt.subplots(figsize=(4, 3))  # Smaller figure for compact look

            bars = ax.bar(["With Alt", "Missing Alt"], [with_alt, missing_alt], width=0.3, color=["green", "red"])

            # Optional: Add text labels above the bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=10)

            ax.set_ylabel("Count", fontsize=10)
            ax.set_ylim(0, max(with_alt, missing_alt) + 5)  # Adjust y-limit for space
            ax.tick_params(axis='x', labelsize=10)
            ax.tick_params(axis='y', labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            st.pyplot(fig)


            # --------- Detailed Table ---------
            st.subheader("📋 Image Table")
            # Function to generate HTML <img> tag for previews
            def generate_img_tag(src):
                try:
                    return f"<img src='{src}' width='100' height='100'>"
                except:
                    return "❌"

            # Copy and transform dataframe
            df_display = df.copy()
            df_display["Preview"] = df_display["src"].apply(generate_img_tag)
            df_display["Has Alt"] = df_display["has_alt"].apply(lambda x: "✅" if x else "❌")
            df_display["Alt Text"] = df_display["alt_text"].fillna("None")

            # Only display selected columns
            df_display = df_display[["index", "Preview", "Has Alt", "Alt Text"]]

            # Convert to HTML table
            table_html = df_display.to_html(escape=False, index=False)
            st.markdown(table_html, unsafe_allow_html=True)

    else:
        st.warning("❌ Invalid input. Please use full URL.")
