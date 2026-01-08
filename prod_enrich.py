import pandas as pd
import time
import os
import requests


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "").strip()

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("Google API key or CSE ID is missing")

print(f"API Key loaded: {len(GOOGLE_API_KEY)} characters")
print(f"CSE ID loaded: {GOOGLE_CSE_ID}")


def google_search(query, num_results=1):
    """
    Perform a Google Custom Search query.
    Returns the top result (title, link, snippet).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY.strip(),
        "cx": GOOGLE_CSE_ID.strip(),
        "q": query,
        "num": num_results
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            return None

        item = data["items"][0]
        return {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
                }

    except requests.exceptions.HTTPError as e:
        print(f"[API ERROR] {query} | {e}")
        return None

    except Exception as e:
        print(f"[ERROR] {query} | {e}")
        return None



# Enrichment Logic
def enrich_product(product_name, brand):
    """
    Enrich a single product using Google Custom Search.
    """
    enrichment = {}

    # Official product page
    enrichment["official_product_page"] = google_search(
        f"{product_name} official"
    )

    # Brand website confirmation
    enrichment["brand_website"] = google_search(
        f"{brand} official website"
    )

    # External product description
    enrichment["external_description"] = google_search(
        f"{product_name} description"
    )

    # Barcode / SKU / Country of origin
    enrichment["identifier_info"] = google_search(
        f"{product_name} barcode SKU country of origin"
    )

    return enrichment


# Load scraped data
df = pd.read_csv("day1_dataset.csv")

# Limit to first 10 products
df = df.head(10)

# New columns
df["official_product_page"] = ""
df["brand_website"] = ""
df["external_description"] = ""
df["identifier_info"] = ""

for idx, row in df.iterrows():
    print(f"Enriching: {row['product_name']}")

    enrichment = enrich_product(
        product_name=row["product_name"],
        brand=row["brand"]
    )

    df.at[idx, "official_product_page"] = enrichment["official_product_page"]
    df.at[idx, "brand_website"] = enrichment["brand_website"]
    df.at[idx, "external_description"] = enrichment["external_description"]
    df.at[idx, "identifier_info"] = enrichment["identifier_info"]

    # Polite delay (important!)
    time.sleep(1.5)

# Save enriched file
df.to_csv("day2_enriched_dataset.csv", index=False)
