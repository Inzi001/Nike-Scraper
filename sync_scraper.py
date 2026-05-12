import requests
import logging
import json
from lxml import html
import csv
import pandas as pd

logging.basicConfig(level=logging.INFO)


class Nike:
    def __init__(self):
        self.products_urls = []
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-full-version-list': '"Chromium";v="148.0.0.0", "Brave";v="148.0.0.0", "Not/A)Brand";v="99.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"19.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
            
        }

    def crawl(self):
        try:
            
            response = requests.get('https://www.nike.com/ph/w',  headers=self.headers)
            logging.info("Response received: %d", response.status_code)
            next_url = ''
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                data_script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
                if data_script:
                    data_json = json.loads(data_script[0])
                    products = data_json['props']['pageProps']['initialState']['Wall']['productGroupings']
                    for product in products:
                        product_list = product['products'][0]['pdpUrl']['url']
                        self.products_urls.append(product_list)

                    next_url = data_json['props']['pageProps']['initialState']['Wall']['pageData']['next']

                    logging.info("Data extracted successfully")
                    return next_url
                else:
                    logging.warning("No data script found in the HTML")
        except requests.RequestException as e:
            logging.error("Error occurred while fetching data: %s", str(e))

    def extract_urls(self, next_url):
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.6',
                'anonymousid': '2F135F9D1D4031729E1AA556A44FBD7A',
                'cache-control': 'no-cache',
                'nike-api-caller-id': 'nike:dotcom:browse:wall.client:2.0',
                'origin': 'https://www.nike.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.nike.com/',
                'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',

            }

            response = requests.get(
                f'https://api.nike.com{next_url}',
                headers=headers,
            )
            logging.info("Response received: %d", response.status_code)
            if response.status_code == 200:
                data_json = response.json()
                return data_json
            else:
                logging.warning("Failed to fetch data from API: %d", response.status_code)
                return None
        except KeyError as e:
            logging.error("Key error while parsing data: %s", str(e))
            return []
        
    def parse_data(self, data_json):
        try:
            next_url = ''
            product_groupings = data_json['productGroupings']
            if not product_groupings:
                logging.warning("No product groupings found in the data")
                return next_url
            for product in product_groupings:
                product_list = product['products'][0]['pdpUrl']['url']
                self.products_urls.append(product_list)
            next_url = data_json['pages']['next']
            logging.info("Parsed %d products", len(self.products_urls))
        except KeyError as e:
            logging.error("Key error while parsing data: %s", str(e))
        return next_url
        
    def product_search(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            logging.info("Response received for product search: %d", response.status_code)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                data_script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
                if data_script:
                    data_json = json.loads(data_script[0])
                    return data_json
                else:
                    logging.warning("No data script found in the product page HTML")
                    return None 
            else:
                logging.warning("Failed to fetch product details: %d", response.status_code)
        except requests.RequestException as e:
            logging.error("Error occurred while fetching product details: %s", str(e))

    def extract_rating(self, url_code):
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.6',
                'cache-control': 'no-cache',
                'nike-api-caller-id': 'com.nike.commerce.nikedotcom.web',
                'origin': 'https://www.nike.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.nike.com/',
                'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
            }

            params = {
                'count': '3',
            }
            response = requests.get(f'https://api.nike.com/products/experience/v1/d9a5bc42-4b9c-4976-858a-f159cf99c647/PH/en-GB/styleCode/{url_code}', headers=headers, params=params)
            logging.info("Response received for rating extraction: %d", response.status_code)
            if response.status_code == 200:
                data_json = response.json()
                ratings = data_json['ratingsAndReviews']['averageOverallRating']
                reviews = data_json['ratingsAndReviews']['totalReviews']
                return ratings, reviews
            else:
                logging.warning("Failed to fetch product details for rating extraction: %d", response.status_code)
                return None, None
        except requests.RequestException as e:
            logging.error("Error occurred while fetching product details for rating extraction: %s", str(e))

    def extract_product_details(self, data_json):
        try:
            ratings, reviews = self.extract_rating(data_json['props']['pageProps']['selectedProduct']['styleCode'])
            data = data_json['props']['pageProps']['selectedProduct']
            product_details = {
                'Product_URL': data['pdpUrl']['url'],
                'Product_Image_URL': data['contentImages'][0]['properties']['squarish']['url'],
                'Product_Tagging': data['productInfo']['badge'],
                'Product_Name': data['productInfo']['title'],
                'Product_Description': data['productInfo']['productDescription'],   
                'Original_Price': data['prices']['initialPrice'],
                'Discount_Price': data['prices']['currentPrice'],
                'Sizes_Available': ", ".join([size['localizedLabel'] for size in data['sizes']]),
                "Vouchers": data['prices']['discountPercentage'],
                "Available_Colors": ", ".join([color['colorDescription'] for color in data_json['props']['pageProps']['colorwayImages']]),
                "Color_Shown": data['colorDescription'],
                'Style_Code': data['styleColor'],
                'Rating_Score': ratings,
                'Review_Count': reviews

            }
            return product_details
        except KeyError as e:
            logging.error("Key error while extracting product details: %s", str(e))
            return None

if __name__ == "__main__":
    nike = Nike()
    next_url = nike.crawl()
    while next_url:
        logging.info("Fetching data from: %s", next_url)
        data_json = nike.extract_urls(next_url)
        if data_json:
            next_url = nike.parse_data(data_json)
            logging.info("Total products parsed: %d", len(nike.products_urls))
        else:
            with open('nike_data.json', 'w') as f:
                json.dump(nike.products_urls, f, indent=4)
            break

    products = []
    for url in nike.products_urls:  # Limiting to first 10 products for demonstration
        logging.info("Extracting details for product URL: %s", url)
        product_data_json = nike.product_search(url)
        if product_data_json:
            product_details = nike.extract_product_details(product_data_json)
            if product_details:
                logging.info("Product details extracted successfully for URL: %s", url)
                products.append(product_details)
            else:
                logging.warning("Failed to extract product details for URL: %s", url)
        else:
            logging.warning("Failed to fetch product data for URL: %s", url)

    df = pd.DataFrame(products)
    empty_tagging_count = (
        df["Product_Tagging"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    print(f"Total products with empty tagging: {empty_tagging_count}")

    df = df[
        (
            df["Product_Tagging"]
            .fillna("")
            .astype(str)
            .str.strip() != ""
        )
        &
        (
            df["Discount_Price"]
            .fillna("")
            .astype(str)
            .str.strip() != ""
        )
    ]
    main_columns = [
        "Product_URL",
        "Product_Image_URL",
        "Product_Tagging",
        "Product_Name",
        "Product_Description",
        "Original_Price",
        "Discount_Price",
        "Sizes_Available",
        "Vouchers",
        "Available_Colors",
        "Color_Shown",
        "Style_Code",
        "Rating_Score",
        "Review_Count"
    ]

    df[main_columns].to_csv(
        "nike_products.csv",
        index=False,
        encoding="utf-8"
    )

    top_10_expensive = (
        df.sort_values(
            by="Discount_Price",
            ascending=False
        )
        .head(10)
    )

    print("\nTop 10 Most Expensive Products:\n")

    for _, row in top_10_expensive.iterrows():

        print(f"Name: {row['Product_Name']}")
        print(f"Final Price: {row['Discount_Price']}")
        print(f"URL: {row['Product_URL']}")
        print("-" * 50)

    # =========================
    # B. TOP 20 RANKING
    # =========================

    ranking_df = df[
        df["Review_Count"] > 150
    ].copy()

    ranking_df = ranking_df.sort_values(
        by=["Rating_Score", "Review_Count"],
        ascending=[False, False]
    )

    # SAME RANK FOR SAME VALUES
    ranking_df["Rank"] = ranking_df[
        ["Rating_Score", "Review_Count"]
    ].apply(tuple, axis=1).rank(
        method="dense",
        ascending=False
    ).astype(int)

    top_20 = ranking_df.head(20)

    top_20.to_csv(
        "top_20_rating_review.csv",
        index=False,
        encoding="utf-8"
    )


