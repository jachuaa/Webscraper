import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import time

# 🔹 Define the website and the type of content to scrape
BASE_URL = "https://www.jasperskytram.com/"
SCRAPE_TYPE = "text"  # Change to "text", "image", or "link"
KEYWORD = "special rates"  # Only needed if SCRAPE_TYPE = "text"

# 🔹 Storage for results
scraped_data = []
visited_urls = set()
urls_to_scrape = {BASE_URL}

# 🔹 Function to extract internal links for crawling
def extract_links(soup, current_url):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        link = urljoin(current_url, a_tag["href"])
        parsed_link = urlparse(link)

        # Only keep links within the same website
        if parsed_link.netloc == urlparse(BASE_URL).netloc and link not in visited_urls:
            links.add(link)
    return links

# 🔹 Function to scrape based on SCRAPE_TYPE
def scrape_page(url):
    global scraped_data

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        print(f"✅ Scraping: {url}")

        data = []  # Store extracted data

        if SCRAPE_TYPE == "text":
            text_elements = soup.find_all(["p", "h1", "h2", "h3", "span"])
            matched_text = []

            for elem in text_elements:
                text = elem.get_text(strip=True)
                if KEYWORD.lower() in text.lower():  # Case-insensitive keyword search
                    matched_text.append(text)

            if matched_text:
                data.append({"Page URL": url, "Matched Text": "\n".join(matched_text)})

        elif SCRAPE_TYPE == "image":
            images = soup.find_all("img", src=True)
            data = [{"Page URL": url, "Image URL": urljoin(url, img["src"])} for img in images]

        elif SCRAPE_TYPE == "link":
            links = soup.find_all("a", href=True)
            data = [{"Page URL": url, "Link": urljoin(url, a["href"])} for a in links]

        else:
            print("⚠️ Invalid SCRAPE_TYPE. Choose from 'text', 'image', or 'link'.")
            return

        # Add data to results if any were found
        if data:
            scraped_data.extend(data)

        # Extract new links for further crawling
        new_links = extract_links(soup, url)
        urls_to_scrape.update(new_links)

    except requests.RequestException as e:
        print(f"❌ Error scraping {url}: {e}")

# 🔹 Start scraping process
while urls_to_scrape:
    current_url = urls_to_scrape.pop()
    if current_url not in visited_urls:
        visited_urls.add(current_url)
        scrape_page(current_url)
        time.sleep(1)  # Prevent server overload

# 🔹 Save results to Excel
if scraped_data:
    df = pd.DataFrame(scraped_data)
    output_file = f"jasper_skytram_{SCRAPE_TYPE}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"✅ {SCRAPE_TYPE.capitalize()} data saved to {output_file}")
else:
    print(f"⚠️ No data found for the selected SCRAPE_TYPE: {SCRAPE_TYPE}")
