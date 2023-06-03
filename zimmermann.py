import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib3
import logging
import os
import pandas as pd
import xlsxwriter
import csv
import re
import itertools
import uuid
from urllib.parse import urlparse
from proxy import proxy_url

def parser(url):

    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    # заголовки запроса
    headers = {
    'authority': 'www.zimmermann.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="112", "Not_A Brand";v="24", "Opera GX";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0',
    }

    # Затем отправьте запрос с полученными кукисами
    response = requests.get(url=url,proxies=proxies, headers=headers)

    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    title_block = soup.find('h1', {'class': 'heading heading--page'})

    title_h1 = title_block.find('span').text.strip()

    # TITLE H1 CAPS
    title_h1_caps = title_h1.upper()

    print(title_h1_caps)

    parsed_url = urlparse(url)
    path = parsed_url.path

    # Разделяем путь на отдельные сегменты
    filename = path.split("/")[-1]
    # Находим последний сегмент, содержащий нужную информацию
    # HANDLE
    handle = filename.split(".")[0]

    # VENDOR
    vendor = "ZIMMERMANN"

    # print(title_h1_caps, handle, vendor)

    product_column_one_div = soup.find('div',{'class':'product-styling-column-one'})
    product_column_two_div = soup.find('div',{'class':'product-styling-column-two'})

    size_column_one_div = soup.find("div", {"class":"product-measurements-wrapper"})
    size_details = soup.find("div", {"class":"product-view__sizecare-sizefit"})
    
    care_column_one_div = soup.find("div", {"class":"product-measurements-column-two"})

    # ITEM DETAILS H4
    try:
        item_details_h4 = product_column_one_div.find('h4')
    except: 
        item_details_h4 = "<h4>ITEM DETAILS</h4>"

    # STYLING H4
    try:
        styling_h4 = product_column_two_div.find('h4')
    except:
        styling_h4 = "<h4>STYLING</h4>"

    # MEASURES H4
    size_h4 = size_column_one_div.find("h4")

    care_h4 = care_column_one_div.find("h4")

    # Table product-view__sizecare-table
    table_sizecard = size_column_one_div.find("div", {"class":"product-view__sizecare-table"})

    item_details_div_stcode = product_column_one_div.find('div', {'class': 'product-view__styling-webnote paragraph'})

    styling_details_first = product_column_two_div.find('div', {'class': 'product-view__styling-stylenote paragraph'})

    try:
        styling_details_second = product_column_two_div.find_all('span')[1]
    except:
        styling_details_second = ""

    span_tag_item_details = item_details_div_stcode.find('span')

    care_instructions = care_column_one_div.find('div', {'class': 'product-view__sizecare-care paragraph'})
    item_details_text = span_tag_item_details.replace_with(span_tag_item_details.text)

    # ITEM DETAILS
    item_details = item_details_from(str(item_details_text))
    
    try:
        a_tags = styling_details_second.find_all('a')
        for tag in a_tags:
            tag.unwrap()
    except:
        styling_details_second = ""

    div_elements = soup.find_all('div', class_='product-gallery__slider-product')

    # ЛИСТ С ФОТКАМИ
    src_list = []

    for div in div_elements:
        try:
            src = div.find('img')['data-original'].split('?')[0]
            src_list.append(src)
        except (KeyError, TypeError):
            # Обработка ошибки, если атрибут 'data-original' не найден или значение равно None
            # print("Ошибка при получении src из элемента:")
            continue

    script_tag = soup.find('script', attrs={'data-ommit': 'true'})
    script_content = script_tag.string

    # SIZE LIST
    size_list = []

    size_list = re.findall(r'"label":"(?!Size)(\w+)"', script_content)

    # PRICE
    amount = soup.find("span", {"class": "price"}).text
    price = ''

    for char in amount:
        if char.isdigit():
            price += char

    # COLOR LIST HEADING
    try:
        color_list_heading = soup.find("h4",class_="product-view__color-variant-title").text
    except:
        color_list_heading = ""


    color_divs = soup.find_all("div", class_="product-view__color-variant-item")


    # COLOR LIST
    colors = [div.get_text(strip=True) for div in color_divs]

    print('ALL COLLECTED TRY TO ADD TO DATA LIST')

    body_html = str(item_details_h4) + str(item_details) + str(styling_h4) + str(styling_details_first) + str(styling_details_second) + str(size_h4) + str(table_sizecard) + str(size_details) + str(care_h4) + str(care_instructions)

    data = []
    empty_value = ""
    src_list_length = len(src_list)

    for i, (color, size) in enumerate(itertools.product(colors, size_list), start=1):
        src = src_list[i-1] if i <= src_list_length else empty_value
        title_h1_capsed = title_h1_caps if i == 1 else empty_value
        body_htmle = body_html if i == 1 else empty_value
        vendore = vendor if i == 1 else empty_value
        true_once = 'true' if i == 1 else empty_value
        false_once = 'false' if i == 1 else empty_value
        active_once = 'active' if i == 1 else empty_value
        size_list_heading = "Size" if i == 1 else empty_value
        image_pos = i if i < src_list_length+1 else empty_value
        sku = generate_sku()
        row = {
            'Handle': handle,
            'Title': title_h1_capsed,
            'Body (HTML)': body_htmle,
            'Vendor': vendore,
            'Product Category': '',
            'Type': '',
            'Tags': '',
            'Published': true_once,
            'Option1 Name': size_list_heading,
            'Option1 Value': size,
            'Option2 Name': color_list_heading,
            'Option2 Value': color,
            'Option3 Name': '',
            'Option3 Value': '',
            'Variant SKU': sku,
            'Variant Grams': '0',
            'Variant Inventory Tracker': '',
            'Variant Inventory Policy': 'deny',
            'Variant Fulfillment Service': 'manual',
            'Variant Price': price,
            'Variant Compare At Price': '',
            'Variant Requires Shipping': 'TRUE',
            'Variant Taxable': 'FALSE', 
            'Variant Barcode': '',
            'Image Src': src, 
            'Image Position': image_pos,
            'Image Alt Text': '',
            'Gift Card': false_once,
            'SEO Title': '',
            'SEO Description': '',
            'Google Shopping / Google Product Category': '',
            'Google Shopping / Gender': '',
            'Google Shopping / Age Group': '',
            'Google Shopping / MPN': '',
            'Google Shopping / AdWords Grouping': '',
            'Google Shopping / AdWords Labels': '',
            'Google Shopping / Condition': '',
            'Google Shopping / Custom Product': '',
            'Google Shopping / Custom Label 0': '',
            'Google Shopping / Custom Label 1': '',
            'Google Shopping / Custom Label 2': '',
            'Google Shopping / Custom Label 3': '',
            'Google Shopping / Custom Label 4': '',
            'Variant Image': '',
            'Variant Weight Unit': 'kg',
            'Variant Tax Code': '',
            'Cost per item': price,
            'Included / Ukraine': true_once,
            'Included / International': true_once,
            'Price / International': '',
            'Compare At Price / International': '',
            'Included / Mexico': true_once,
            'Price / Mexico': '',
            'Compare At Price / Mexico': '',
            'Status': active_once
        }
        data.append(row) 
    df = pd.DataFrame(data)
    return df

def main():

    # параметры для использования прокси сервера
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    # заголовки запроса
    headers = {
    'authority': 'www.zimmermann.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="112", "Not_A Brand";v="24", "Opera GX";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0',
    }

    with open("FILE_NAME.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    # soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all('a', {'class': 'catalog-grid-item__link'})

    # print(links, 'COLLECTED')

    dataframes = []

    previous_link = None
    for link in links:
        product_url = link.get('href')
        response_test = requests.get(url=product_url,proxies=proxies, headers=headers)
        response_test_status_code = response_test.status_code
        if product_url == previous_link or response_test_status_code == 404:
            continue  # Пропустить повторяющуюся ссылку
        print(product_url)

        product_data = parser(product_url)
        dataframes.append(product_data)
        previous_link = product_url
    
    # Объедините все полученные dataframe
    final_df = pd.concat(dataframes)

    # Сохраните итоговый dataframe в один Excel файл
    final_df.to_csv('FILE_NAME.csv', index=False)
    final_df.to_excel('FILE_NAME.xlsx', index=False)

sku_set = set()

def generate_sku():
    while True:
        sku = str(uuid.uuid4().int)[:10]  # Генерация случайного SKU из UUID
        if sku not in sku_set:  # Проверка уникальности SKU
            sku_set.add(sku)
            return sku


def item_details_from(text):
    # Найдем все текстовые узлы внутри тега span и произведем замену
    pars = BeautifulSoup(text, 'html.parser')

    for node in pars.find_all(string=True):
        if "from our" in node:
            node.replace_with(node.replace("from our", "from the"))

    # Получим измененный текст
    new_text = str(pars)
    return new_text
 
if __name__ == "__main__":
    main()