from playwright.sync_api import sync_playwright
import random as r
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time
import os

main_frame = []

# Header for frame only once
header_csv = True


def extract_json(url_dot_json):
    global header_csv
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=r.randint(50, 101))
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/69.0.3497.100 Safari/537.36"
        )
        page = browser.new_page(user_agent=ua)
        product_url = f"{url_dot_json}.json"
        page.goto(
            product_url, wait_until="load")
        pageText = page.inner_text('html')
        json_response = json.loads(pageText)
        title = json_response['product']['title']
        sku = json_response['product']['variants'][0]['sku']
        # Filtered Prices (Each item in a list)
        filtered_prices = []
        for item in json_response['product']['variants']:
            filtered_prices.append([float(s)
                                    for s in re.findall(r'\d+\.*\d*', item['title'])])
        final_prices = []
        for i in range(len(json_response['product']['variants'])-1):
            final_prices.append(filtered_prices[i])
        final_prices.append(
            filtered_prices[len(json_response['product']['variants'])-1])
        final_price_for_product = []
        sizes = []
        shipping_array = []
        express_price_for_product = []
        flag = False
        print(final_prices)
        for count, i in enumerate(final_prices):
            if (final_prices[count][-1] < 45):
                continue
            if (flag):
                flag = False
                continue
            if (len(final_prices[count]) >= 5):
                if (len(final_prices[count]) == 5):
                    Shipping = "Normal"
                else:
                    Shipping = "Express"
                try:
                    if (Shipping == "Normal" and final_prices[count][0] == final_prices[count+1][0] and (len(final_prices[count])+1 == len(final_prices[count+1]))):
                        express_price_for_product.append(
                            final_prices[count+1][-2])
                        if (final_prices[count][-1] < final_prices[count+1][-2]):
                            final_price_for_product.append(
                                final_prices[count][-1])
                        else:
                            final_price_for_product.append('_')
                        flag = True
                    else:
                        if (Shipping != "Normal"):
                            express_price_for_product.append(
                                final_prices[count][-2])
                            final_price_for_product.append("_")
                        else:
                            final_price_for_product.append(
                                final_prices[count][-1])
                            express_price_for_product.append("_")
                    sizes.append(
                        f"{int(final_prices[count][0])} {int(final_prices[count][1])}/{int(final_prices[count][2])}")
                    shipping_array.append(Shipping)
                except:
                    try:
                        if (count == len(final_prices)-1):
                            if (Shipping != "Normal"):
                                express_price_for_product.append(
                                    final_prices[count][-1])
                                final_price_for_product.append("_")
                            else:
                                final_price_for_product.append(
                                    final_prices[count][-1])
                                express_price_for_product.append("_")
                            sizes.append(
                                f"{int(final_prices[count][0])} {int(final_prices[count][1])}/{int(final_prices[count][2])}")
                            shipping_array.append(Shipping)
                    except:
                        pass
                    else:
                        pass
            else:
                if (len(final_prices[count]) == 4 and final_prices[count][-1] == 48):
                    Shipping = "Express"
                else:
                    Shipping = "Normal"
                try:
                    if (Shipping == "Normal" and final_prices[count][0] == final_prices[count+1][0] and (len(final_prices[count+1]) < 5) and final_prices[count+1][-1] > 45):
                        express_price_for_product.append(
                            final_prices[count+1][2])
                        if (final_prices[count][2] < final_prices[count+1][2]):
                            final_price_for_product.append(
                                final_prices[count][2])
                        else:
                            final_price_for_product.append('_')
                        flag = True
                    else:
                        if (Shipping != "Normal"):
                            express_price_for_product.append(
                                final_prices[count][2])
                            final_price_for_product.append("_")
                        else:
                            if (len(filtered_prices[count]) == 4):
                                final_price_for_product.append(
                                    f"{int(final_prices[count][-2]*10**3) + int(final_prices[count][-1])}")
                                express_price_for_product.append("_")
                            else:
                                if (final_prices[count][-1] == 48):
                                    continue
                                final_price_for_product.append(
                                    final_prices[count][2])
                                express_price_for_product.append("_")
                    sizes.append(final_prices[count][0])
                    shipping_array.append(Shipping)
                except:
                    try:
                        if (count == len(final_prices)-1):
                            if (Shipping != "Normal"):
                                express_price_for_product.append(
                                    final_prices[count][2])
                                final_price_for_product.append("_")
                            else:
                                final_price_for_product.append(
                                    final_prices[count][2])
                                express_price_for_product.append("_")
                            sizes.append(final_prices[count][0])
                            shipping_array.append(Shipping)
                    except:
                        pass
                    else:
                        pass
                for pr in final_price_for_product:
                    try:
                        if (float(pr).is_integer()):
                            pr = int(pr)
                    except:
                        pass
                for price in express_price_for_product:
                    try:
                        if (float(price).is_integer()):
                            price = int(price)
                    except:
                        pass
        product = {
            'Title': title,
            'sku': sku,
            'size': sizes,
            'product_url': url_dot_json,
            'price': final_price_for_product,
            'express price': express_price_for_product,
        }
        try:
            df = pd.DataFrame(product)
            main_frame.append(df)
            with open('result_one.csv', 'a', newline='')as f:
                if (header_csv == True):
                    df.to_csv(f, index=False)
                    header_csv = False
                else:
                    df.to_csv(f, index=False, header=False)
        except:
            pass
        print("Product scraped")


extract_json(
    "https://en.wethenew.com/products/air-jordan-1-low-cardinal-red")
