# Nike Product Scraper

A high-performance Nike product scraping project built using Python.

This project extracts product details from Nike category pages using both:

- Synchronous scraping (`requests`)
- Asynchronous scraping (`asyncio + httpx`)

The scraper collects complete product information, performs data analysis, and exports results into CSV files.

---

# Features

- Scrape all Nike product URLs from category pages
- Handle Nike API pagination
- Extract complete product details
- Extract ratings & reviews
- Filter products with empty tagging
- Export clean CSV files
- Top 10 expensive product analysis
- Top 20 ranking based on rating & review count
- Async version for high-speed scraping
- Production-ready architecture

---

# Tech Stack

- Python
- Requests
- HTTPX
- Asyncio
- Pandas
- LXML

---

# Project Structure

```bash
nike-product-scraper/
│
├── sync_scraper.py
├── async_scraper.py
├── requirements.txt
├── nike_products.csv
├── top_20_rating_review.csv
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/nike-product-scraper.git

cd nike-product-scraper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Requirements

Create a `requirements.txt` file:

```txt
requests
httpx
pandas
lxml
tqdm
```

---

# Usage

## Run Synchronous Scraper

```bash
python sync_scraper.py
```

---

## Run Asynchronous Scraper

```bash
python async_scraper.py
```

---

# Output Files

## 1. nike_products.csv

Contains all valid products with:

- Product URL
- Image URL
- Product Tagging
- Product Name
- Description
- Original Price
- Discount Price
- Sizes
- Vouchers
- Colors
- Style Code
- Rating
- Review Count

---

## 2. top_20_rating_review.csv

Contains top ranked products based on:

- Highest rating score
- Highest review count
- Dense ranking logic

---

# Product Filtering Rules

Products are excluded if:

- `Product_Tagging` is empty
- `Discount_Price` is empty

Console output example:

```bash
Total products with empty tagging: 42
```

---

# Ranking Logic

Eligibility:

```text
Review_Count > 150
```

Sorting Rules:

1. Higher Rating Score → Higher Rank
2. If ratings are equal → Compare Review Count
3. Same Rating + Same Review Count → Same Rank

---

# Async Scraper Performance

| Version | Approx Speed |
|---|---|
| Synchronous | 1-3 hours |
| Asynchronous | 5-15 minutes |

The asynchronous version uses:

- `asyncio`
- `httpx.AsyncClient`
- concurrency control with semaphores
- HTTP/2 support

---

# Nike API Pagination

Nike category pages use API pagination with:

```text
anchor=24
count=24
```

Example:

```text
https://api.nike.com/discover/product_wall/v1/...
```

The scraper automatically:

- extracts pagination URLs
- fetches all pages
- collects all product URLs

---

# Sample CSV Headers

```csv
Product_URL,
Product_Image_URL,
Product_Tagging,
Product_Name,
Product_Description,
Original_Price,
Discount_Price,
Sizes_Available,
Vouchers,
Available_Colors,
Color_Shown,
Style_Code,
Rating_Score,
Review_Count
```

---

# Example Analysis Output

## Top 10 Most Expensive Products

```bash
Name: Nike Air Max
Final Price: ₱6995
URL: https://www.nike.com/...
```

---

# Future Improvements

- Proxy rotation
- Retry mechanism
- Batch API requests
- MongoDB integration
- Docker support
- CLI arguments
- Scrapy implementation
- Playwright support
- Cloud deployment

---

# Disclaimer

This project is intended for educational and research purposes only.

Please review Nike's Terms of Service before scraping their platform.

---

# Author

Made with Python and web scraping ❤️
