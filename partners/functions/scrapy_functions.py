import time
from selenium import webdriver
from bs4 import BeautifulSoup



def form_options(item):
    options = [var['options'] for var in item['variants']]

    unique_values_list = [[] for _ in range(len(options[0]))]

    for lists in options:
        for i, l in enumerate(lists):
            if l not in unique_values_list[i]:
                unique_values_list[i].append(l)

    names = item['options']

    return [{'name': name, 'values': values} for name, values in zip(names, unique_values_list)]


def update_items_dict(items, vendor, dns_for_selenium=None):  # for another languages

    new_items = dict()

    for k, v in items.items():

        item = v.copy()

        if dns_for_selenium:
            handle = item['card']['item_card']['handle']
            new_description, new_title = get_english(handle, dns_for_selenium)
            # print(f'New description for {handle} is:')
            # print(new_description)
            item['card']['item_card']['title'] = new_title
            item['card']['item_card']['description'] = new_description

        item['card']['item_card']['body_html'] = item['card']['item_card']['description']
        item['card']['item_card']['status'] = 'draft'  # all new products should be added as DRAFT
        item['card']['item_card']['vendor'] = vendor  # name of vendor

        item['card']['item_card']['options'] = form_options(item['card']['item_card'])

        del item['card']['item_card']['tags']  # delete tags

        new_items[k] = item

    return new_items


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


# SELENIUM

def get_options():
    options = webdriver.ChromeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.headless = True
    # options.add_argument('--headless')
    options.add_argument("accept-language=en-US")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    return options


def get_english(handle, dns):
    new_description = str()

    try:
        browser = webdriver.Chrome(executable_path='C:\\Windows\\System32\\chromedriver.exe', options=get_options())

        print('Browser is opened')

        browser.get(f'{dns}/collections/all/products/{handle}')
        time.sleep(5)
        source = browser.page_source

        soup = BeautifulSoup(source, 'html.parser')
        # item_card = soup.find(name='div', attrs={'class', 'product-single__meta'})
        new_description = soup.find(name='div', attrs={'class': 'product__description'}).decode_contents()
        new_title = soup.find(name='h1', attrs={'class': 'product__title'}).decode_contents()

    except:
        print(f'selenium error with {handle}')

    finally:
        browser.close()
        print('Browser is closed')

    return new_description, new_title

