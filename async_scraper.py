import aiohttp
import asyncio
import logging
import json
from lxml import html
import csv
import time

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

    async def crawl(self):
        try:
            
            response = await aiohttp.ClientSession().get('https://www.nike.com/ph/w',  headers=self.headers)
            logging.info("Response received: %d", response.status)
            if response.status == 200:
                tree = html.fromstring(await response.content.read())
                data_script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
                if data_script:
                    data_json = json.loads(data_script[0])
                    total_pages = data_json['props']['pageProps']['initialState']['Wall']['pageData']['totalPages']
                    return total_pages
                else:
                    logging.warning("No data script found in the HTML")
        except aiohttp.ClientError as e:
            logging.error("Error occurred while fetching data: %s", str(e))

    async def extract_urls(self, page_number):
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

            response = await aiohttp.ClientSession().get(
                f'https://api.nike.com/discover/product_wall/v1/marketplace/PH/language/en-GB/consumerChannelId/d9a5bc42-4b9c-4976-858a-f159cf99c647?path=/ph/w&queryType=PRODUCTS&anchor={page_number}&count=24',
                headers=headers,
            )
            logging.info("Response received: %d", response.status)
            if response.status == 200:
                data_json = await response.json()
                return data_json
            else:
                logging.warning("Failed to fetch data from API: %d", response.status)
                return None
        except KeyError as e:
            logging.error("Key error while parsing data: %s", str(e))
            return []
        
    def parse_data(self, data_json):
        try:
            product_groupings = data_json['productGroupings']
            if not product_groupings:
                logging.warning("No product groupings found in the data")
                return None
            for product in product_groupings:
                product_list = product['products'][0]['pdpUrl']['url']
                self.products_urls.append(product_list)
            logging.info("Parsed %d products", len(self.products_urls))
        except KeyError as e:
            logging.error("Key error while parsing data: %s", str(e))
        return None
    

    async def product_search(self, url, session):
        try:
            async with session.get(url, headers=self.headers) as response:
                logging.info("Response received for product search: %d", response.status)
                if response.status == 200:
                    content = await response.text()
                    tree = html.fromstring(content)
                    data_script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
                    if data_script:
                        data_json = json.loads(data_script[0])
                        return data_json    
                    else:
                        logging.warning("No data script found in the product page HTML")
                        return None 
                else:
                    logging.warning("Failed to fetch product details: %d", response.status)
        except aiohttp.ClientError as e:
            logging.error("Error occurred while fetching product details: %s", str(e))
            return None 

    async def extract_rating(self, url_code, session):
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
            async with session.get(f'https://api.nike.com/products/experience/v1/d9a5bc42-4b9c-4976-858a-f159cf99c647/PH/en-GB/styleCode/{url_code}', params=params, headers=headers) as response:
                logging.info("Response received for rating extraction: %d", response.status)
                if response.status == 200:
                    data_json = await response.json()
                    ratings = data_json['ratingsAndReviews']['averageOverallRating']
                    reviews = data_json['ratingsAndReviews']['totalReviews']
                    return ratings, reviews
                else:
                    logging.warning("Failed to fetch product details for rating extraction: %d", response.status)
                    return None, None
        except aiohttp.ClientError as e:
            logging.error("Error occurred while fetching product details for rating extraction: %s", str(e))
            return None, None
        except KeyError as e:
            logging.error("Key error while parsing rating data: %s", str(e))
            return None, None
        
    async def process_product(self, url, session, semaphore):
        async with semaphore:
            try:
                data_json = await self.product_search(url, session)
                if data_json:
                    data = data_json['props']['pageProps']['selectedProduct']
                    style_code = data['styleCode']
                    ratings, reviews = (await self.extract_rating(style_code,session))
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
                return None
            except Exception as e:
                logging.error(f"Processing failed: {e}")
                return None
    
async def main():
    init  = time.time()
    nike = Nike()
    total_pages = await nike.crawl()
    logging.info("Total pages to crawl: %d", total_pages)
    
    tasks = asyncio.gather(*(nike.extract_urls(page) for page in range(1, total_pages + 1)))

    results = await tasks
    for data_json in results:
        if data_json:
            nike.parse_data(data_json)

    logging.info("Total product URLs extracted: %d", len(nike.products_urls))

    dl_seamphore = asyncio.Semaphore(10)  # Limit concurrent requests to 5

    async with aiohttp.ClientSession() as session:
        tasks = [nike.process_product(url, session, dl_seamphore) for url in nike.products_urls]
        results = await asyncio.gather(*tasks)

    product_details_list = []
    for result in results:
        if result:
            product_details_list.append(result)

    
    with open('nike_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product_URL', 'Product_Image_URL', 'Product_Tagging', 'Product_Name', 'Product_Description', 'Original_Price', 'Discount_Price', 'Sizes_Available', 'Vouchers', 'Available_Colors', 'Color_Shown', 'Style_Code', 'Rating_Score', 'Review_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in product_details_list:
            writer.writerow(product)
    end = time.time()
    logging.info("Crawling completed in %.2f seconds", end - init)

if __name__ == "__main__":
    asyncio.run(main())
