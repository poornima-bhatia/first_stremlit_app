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
            st.subheader("📋 Image Table with Previews")

            table_html = """
            <table style='width:100%; border-collapse: collapse;' border='1'>
            <tr>
                <th>Index</th>
                <th>Preview</th>
                <th>Has Alt</th>
                <th>Alt Text</th>
            </tr>
            """

            for _, row in df.iterrows():
                img_tag = f"<img src='{row['src']}' width='100' height='100'>" if row['src'] else "❌"
                has_alt = "✅" if row["has_alt"] else "❌"
                alt_text = row["alt_text"] if row["alt_text"] else "N/A"

                table_html += f"""
                <tr>
                    <td>{row['index']}</td>
                    <td>{img_tag}</td>
                    <td>{has_alt}</td>
                    <td>{alt_text}</td>
                </tr>
                """

            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)
            
    else:
        st.warning("❌ Invalid input. Please use full URL.")
