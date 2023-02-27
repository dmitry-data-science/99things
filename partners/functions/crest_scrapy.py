import requests
from bs4 import BeautifulSoup
import json

from selenium import webdriver
import time

dns = 'https://crestclothing.com'



def clean_text(text):
    return text.replace('\n', '').replace('[', '').replace(']', '').strip()


def get_soup(href, dns=dns):
    response = requests.get(f'{dns}{href}')
    soup = BeautifulSoup(response.text, features='html.parser')

    return soup


# for products list

def get_href_for_card(item):
    return item.find(name='a').get('href')


def get_title(item):
    return item.find(name='span', attrs={'class': 'grid-product__title'}).text


def get_price_field(item):
    return item.find(name='span', attrs={'class': 'long-dash'}).find_next()

def is_in_stock(price_field):
    return 'Sold out' not in price_field.text


def get_old_price(item, price_field):
    return clean_text(price_field.text) if price_field else 0


def get_new_price(item, price_field):
    return clean_text(
            price_field.find_next().text
            if price_field.get('class')[0] == 'grid-product__strikethrough' else
            get_old_price(item, price_field)
        ) if price_field else 0


# for product card

def get_images(soup):
    img_tags = soup.find_all(name='div', attrs={'class': 'product-single__media-flex-wrapper'})
    images_dict = dict()

    for i, img in enumerate(img_tags):
        images_dict[i] = dict()

        tag = img.find(name='img')
        images_dict[i]['href'] = tag.get('data-src')  # .replace('{width}', '1080')
        images_dict[i]['widths'] = clean_text(tag.get('data-widths')).split(', ')

    return images_dict


def get_description(item_card):
    return item_card.find(name='div', attrs={'class': 'product-single__description rte'}).renderContents().decode()


def get_params(item_card):
    params_list = item_card.find_all(name='div', attrs={'class': 'radio-wrapper'})

    return {clean_text(params.label.text): [x.text for x in params.find_all(name='option')] for params in params_list}


def get_data_from_card(soup):
    item_card = soup.find(name='div', attrs={'class', 'product-single__meta'})
    item_json = json.loads(soup.find_all('script', attrs={'id': 'ProductJson-product-template'})[0].string)

    return {'item_card': item_json,
            'images': get_images(soup),
            'name': item_card.find('h1').text,
            'description': get_description(item_card),
            'params': get_params(item_card)
            }


# prices has 2 additional zeros. We remove them
def fix_price_to_items_dict(items_dict):
    items_dict_fixed_prices = dict()

    for k, v in items_dict.items():
        v_fixed = v.copy()

        if 'variants' not in v['card']['item_card'].keys():
            print('variants is not in keys')
            items_dict_fixed_prices[k] = v_fixed
            continue

        # fix the product prices
        for prod_key in v['card']['item_card'].keys():

            if ('price' in prod_key) & (isinstance(v_fixed['card']['item_card'][prod_key], int)):
                v_fixed['card']['item_card'][prod_key] /= 100

        # fix the variants prices
        for i, variants in enumerate(v['card']['item_card']['variants']):

            for var_key in v['card']['item_card']['variants'][i].keys():

                if ('price' in var_key) & (isinstance(v_fixed['card']['item_card']['variants'][i][var_key], int)):
                    v_fixed['card']['item_card']['variants'][i][var_key] /= 100

        items_dict_fixed_prices[k] = v

    return items_dict_fixed_prices


def scrapy_main():
    items_list = (get_soup('/collections/all')
                  .find(name='div', attrs={'class': 'grid-uniform'})
                  .find_all(name='div', attrs={'class': 'grid__item'}))

    print(f'{len(items_list)} items detected')

    items_dict = dict()

    for i, item in enumerate(items_list):
        items_dict[i] = {
            'href': get_href_for_card(item),
            'title': get_title(item),
            'in_stock': is_in_stock(get_price_field(item)),
            'old_price': get_old_price(item, get_price_field(item)),
            'price': get_new_price(item, get_price_field(item)),
            'card': get_data_from_card(
                get_soup(
                    get_href_for_card(
                        item
                    )
                )
            )
        }

    items_dict = fix_price_to_items_dict(items_dict)

    return items_dict


# def get_redirect_name(source_handle):
#
#     response = requests.get(f'https://99things.eu/products/{source_handle}')
#     soup = BeautifulSoup(response.text, parser='html')
#
#     new_handle = json.loads(
#         soup.find(name='script', attrs={'type': "application/ld+json"})
#             .decode_contents()
#             .replace('\r', '')
#             .replace('\n', '')
#     )['url'].split('/')[-1]
#
#     return new_handle


# def source_target_matching_for_handler(partners_items_dict, our_shop_product_list):
#     handles_in_source = {item['card']['item_card']['handle'] for item in list(partners_items_dict.values())}
#     handles_in_target = {prod['handle'] for prod in our_shop_product_list}
#
#     handles_dict = {handle: handle for handle in handles_in_source & handles_in_target}
#     new_items_handles = list()
#
#     for handle in handles_in_source.difference(handles_in_target):
#
#         redirect_name = get_redirect_name(handle)
#
#         if redirect_name == '404':
#             new_items_handles.append(handle)
#         else:
#             handles_dict[handle] = redirect_name
#
#     handles_dict = {v: k for k, v in handles_dict.items()}



# SELENIUM

def get_options():
    options = webdriver.ChromeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.headless = True
    # options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    return options


def get_english_description(handle):
    new_description = str()

    try:
        browser = webdriver.Chrome(executable_path='C:\\Windows\\System32\\chromedriver.exe', options=get_options())

        print('Browser is opened')

        browser.get(f'{dns}/collections/all/products/{handle}')
        time.sleep(5)
        source = browser.page_source

        soup = BeautifulSoup(source, 'html.parser')
        item_card = soup.find(name='div', attrs={'class', 'product-single__meta'})
        new_description = item_card.find(name='div', attrs={'class': 'product-single__description'}).decode_contents()


    except:
        print(f'selenium error with {handle}')

    finally:
        browser.close()
        print('Browser is closed')

    return new_description


def form_options(item):
    options = [var['options'] for var in item['variants']]

    unique_values_list = [[] for _ in range(len(options[0]))]

    for lists in options:
        for i, l in enumerate(lists):
            if l not in unique_values_list[i]:
                unique_values_list[i].append(l)

    names = item['options']

    return [{'name': name, 'values': values} for name, values in zip(names, unique_values_list)]


def update_items_dict(items):  # for another languages

    new_items = dict()

    for k, v in items.items():

        item = v.copy()

        handle = item['card']['item_card']['handle']
        new_description = get_english_description(handle)
        # print(f'New description for {handle} is:')
        # print(new_description)
        item['card']['item_card']['description'] = new_description
        item['card']['item_card']['body_html'] = new_description
        item['card']['item_card']['status'] = 'draft'  # all new products should be added as DRAFT
        item['card']['item_card']['vendor'] = 'CREST'  # name of vendor

        item['card']['item_card']['options'] = form_options(item['card']['item_card'])

        new_items[k] = item

    return new_items


