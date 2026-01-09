
## Day 1 Deliverables
• Dataset: day1_dataset.csv

• Script: scrapy.py

• Tools used: python, pandas, BeautifulSoup, lxml, requests, re

• Issues encountered:

    • Ingredients and size information were not always structured consistently across product pages.
    • Some fields required inference from product descriptions.

• Assumptions and logic applied:

    • Brand was inferred from the product title when not explicitly stated.
    • Ingredients were captured as raw text when not listed in a dedicated section.
    • Missing fields were left empty rather than guessed.

• Dataset Organisation: Each row represents one skincare product, and each column represents a specific attribute. The dataset was exported as a csv file for easy analysis and reuse.

## Day 2 Deliverables
• Dataset: day2_enriched_dataset.csv

• Script: prod_enrich.py

### How the API was used
The Google Custom Search json API was used to enrich the scraped skincare product dataset with external information.
For each selected product, at least one API call was made using the product name and brand as the search query.
The API was used to retrieve:

  • Manufacturer's official product pages.
  
  • Brand website confirmations.
  
  • Additional product descriptions from external sources.
  
  • Identifiers such as SKU, barcode, or country of origin when available.

Each API request returned structured metadata including the page title, URL, and snippet, which were stored alongside the original scraped data.
API calls were rate limited and wrapped in error handling logic to ensure the pipeline continued even if an individual enrichment failed.

### Data Validation Logic
Several checks were applied to ensure data quality:

  • Source validation: Only search results from recognizable brand websites, manufacturers, or reputable retailers were considered valid.

  • Query consistency: Search queries were standardized using the product name and brand to avoid mismatches.

  • Null handling: If no relevant results were returned by the API, the enrichment fields were left empty rather than populated with unreliable data.

  • Formatting: All text fields were cleaned and normalized to ensure compatibility with csv storage.

### How reliability was determined
The reliability of enriched data was assesed using:

  • Domain credibility: Preference was given to offical brand domains and manufacturer websites over third party blogs.

  • Cross confirmation: Enriched information was compared to the original scraped data for consistency.

  • Search relevance: The relevance of each enrichment was evaluated using the search result title and snippet to ensure alignment with the product.

This ensured that enriched data improved that dataset's value without compromising accuracy or transparency.

## My Approach Summary

The project was executed in two main phases: web data extraction and external data enrichment. Initially, product data was collected by targeting individual product URLs to ensure accurate extraction of attributes such as product name, brand, category, ingredients, size, and product page URLs. While this approach ensured correctness, it was not scalable. To improve efficiency, the extraction logic was later refactored to target product listings directly from category pages using XPath selectors to identify product card elements and anchor tags. These elements were then parsed with BeautifulSoup to dynamically retrieve the first set of product links, enabling automated and repeatable scraping without manual URL input.

For content extraction on individual product pages, BeautifulSoup was used to parse structured HTML elements such as headings, description blocks, and specification sections. Custom parsing logic was applied to handle semi-structured text patterns (e.g., extracting ingredient lists beginning after “Product contains:” and excluding sections such as “Product effects”). Additional string-processing functions were implemented to derive attributes like product size directly from product names.

Product categorization was determined using a multi signal, rule-based approach designed to maximize reliability in the presence of inconsistent site structure. Rather than relying on a single label, category inference combined breadcrumb hierarchy, URL path patterns, HTML section headers, and keyword analysis of product titles, descriptions, and ingredient lists. When explicit category metadata was unavailable or ambiguous, fallback details such as ingredient and packaging descriptors were applied to determine the most probable product type.

In the enrichment phase, the Google Custom Search JSON API was integrated to retrieve externally validated information, including official product pages, brand website confirmations, and supplementary descriptions. During integration, repeated 401 Unauthorized errors were encountered due to incorrect API key types, project configuration mismatches, and permission restrictions. These issues were resolved by generating a valid Google Cloud API key, enabling the Custom Search API in the correct project, resolving permission issues, and ensuring environment variables do not have hidden characters. Error handling was implemented to log API failures without interrupting the enrichment pipeline.

Throughout the project, validation logic was applied to improve data quality and analytical reliability. Enriched fields were populated only when results originated from credible domains such as manufacturer or brand owned websites. Queries were standardized, null handling was enforced for missing results, and scraped data was stored separately from enriched data. This ensured the final dataset was scalable, traceable, and suitable for product analytics.

## Summary Insights

• Product information consistency varied across sources: Core attributes such as product names and sizes were generally consistent across scraped and external sources, while ingredient lists and descriptions showed variability in structure and level of detail.

• Brand-owned pages provided the highest data reliability: Official brand and manufacturer websites consistently offered the most complete and accurate information compared to third-party retailers, making them the preferred enrichment sources for catalog validation.

• Semi-structured product content requires custom parsing logic: Key product attributes (e.g., ingredients and size) were embedded within free-text descriptions rather than structured fields, requiring pattern based extraction and string processing for accurate data capture.

• External enrichment improved product context, not completeness: While API-based enrichment enhanced brand confirmation and product context, some attributes (such as barcode or country of origin) were inconsistently available, reinforcing the need for null handling rather than forced inference.

• Scalable extraction significantly improves maintainability: Transitioning from manually targeted product URLs to XPath-driven product discovery reduced manual overhead and enabled a more scalable, repeatable scraping workflow suitable for ongoing product analytics and catalog monitoring.
