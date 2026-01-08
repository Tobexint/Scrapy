import requests
import re
from lxml import html
from bs4 import BeautifulSoup
import pandas as pd
import time


headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_product_urls_from_category(category_url, limit=20):
    """
    Extract individual product URLs from a category page using XPath.
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(category_url, headers=headers, timeout=20)
    response.raise_for_status()

    tree = html.fromstring(response.content)

    # XPath: anchor tags linking to product pages
    product_links = tree.xpath("//a[contains(@href, '/product/')]/@href")

    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in product_links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    return unique_links[:limit]

CATEGORY_URL = "https://qudobeauty.com/"

# ---------- Individual product URLs ----------
PRODUCT_URLS = get_product_urls_from_category(CATEGORY_URL, limit=20)

products = []

def extract_category_from_json(soup):
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "category" in data:
                return data["category"]
        except:
            continue

    return None

def infer_category_from_name(product_name):
    if not product_name:
        return None

    name = product_name.lower()

    if "cleanser" in name or "wash" in name:
        return "Cleanser"
    if "serum" in name:
        return "Serum"
    if "moisturizer" in name or "cream" in name:
        return "Moisturizer"
    if "toner" in name:
        return "Toner"
    if "lotion" in name:
        return "Lotion"
    if "shower gel" in name:
        return "Shower Gel"
    if "deodorant" in name:
        return "Deodorant"

    return "Skincare"

def get_product_category(soup, product_name):
    return (
        extract_category_from_json(soup)
        or infer_category_from_name(product_name)
    )

def extract_size(product_name):
    """
    Extracts size (e.g. 450ml, 50 g, 8oz) from the end of a product name.
    Returns None if not found.
    """
    if not product_name:
        return None

    pattern = r"(\d+\s?(?:ml|g|kg|oz|l|count|Pcs))$"
    match = re.search(pattern, product_name.strip(), re.IGNORECASE)

    if match:
        return match.group(1).replace(" ", "")

    return None

def extract_ingredients(soup):
    """
    Extract ingredients listed after 'Product contains:'.
    Returns None if not found.
    """
    text = soup.get_text(" ", strip=True)

    pattern = r"Product contains:\s*(.*?)(?=Product effects|$)"

    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        ingredients = match.group(1).strip()
        ingredients = re.sub(r"\s+", " ", ingredients)
        return ingredients

    return None

# ---------- Scrape each product ----------
for url in PRODUCT_URLS:
    print(f"Fetching: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed: {e}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    try:
        product_name = soup.find("h1").get_text(strip=True)
    except:
        product_name = None

    try:
        image = soup.find("img")["src"]
        if image.startswith("//"):
            image = "https:" + image
    except:
        image = None

    #description = soup.get_text(" ", strip=True)

    products.append({
        "product_name": product_name,
        "brand": product_name.split(" ")[0] if product_name else None,
        "category": get_product_category(soup, product_name),
        "ingredients": extract_ingredients(soup),
        "size": extract_size(product_name),
        "image_url": image,
        "product_url": url
    })

    time.sleep(1)

# ---------- Save to CSV ----------
df = pd.DataFrame(products)
df.to_csv("day1_dataset.csv", index=False)

print("Scraping completed successfully")

