from partners.functions.scrapy_functions import form_options, fix_price_to_items_dict

import requests
from bs4 import BeautifulSoup
import json


dns = 'https://lnestudio.com'


def clean_text(text):
    return text.replace('\n', '').replace('[', '').replace(']', '').strip()


def get_soup(href, dns=dns):
    response = requests.get(f'{dns}{href}')
    soup = BeautifulSoup(response.text, features='html.parser')

    return soup


# get product list
def get_items_list(dns=dns, page='/collections/all'):
    items_list = list()
    i = 1

    while True:

        soup = get_soup(f'{page}?page={str(i)}')
        items_list.extend(soup
                          .find(name='ul', attrs={'id': 'product-grid'})
                          .find_all(name='li', attrs={'class': 'grid__item'}))

        prod_count = int(soup.find(name='span', attrs={'id': 'ProductCount'}).text.split()[0])

        if len(items_list) < prod_count:
            i += 1
        else:
            break

    return items_list


# for products list

def get_href_for_card(item):
    return item.find(name='a').get('href')


def get_title(item):
    return item.find(name='a', attrs={'class': 'full-unstyled-link'}).text.strip()


def get_price_field(item):
    return item.find(name='span', attrs={'class': 'long-dash'}).find_next()

def is_in_stock(item):
    return 'Sold out' not in item.find(name='div', attrs={'class': 'card-wrapper'}).text


def get_old_price(item):
    sale_block = item.find(name='div', attrs={'class': 'price__sale'}).find(name='span', attrs={'class': 'price-item--regular'})
    if sale_block:
        old_price = sale_block.text.strip().split()[-1]
    else:
        old_price = get_new_price(item)
    return old_price


def get_new_price(item):
    return item.find(name='span', attrs={'class': 'price-item--regular'}).text.strip().split()[-1]


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
    return item_card.find(name='div', attrs={'class': 'product__info-container'}).renderContents().decode()


def get_params(item_card):
    params_list = item_card.find_all(name='div', attrs={'class': 'radio-wrapper'})

    return {clean_text(params.label.text): [x.text for x in params.find_all(name='option')] for params in params_list}


def get_data_from_card(soup):
    # item_card = soup.find(name='div', attrs={'class', 'product-single__meta'})

    js_text = [js for js in soup.find_all('script') if (js.string and 'Globo.Options.product' in js.string)][0].string
    item_json = json.loads(js_text.split('Globo.Options.product')[1].replace('\n  ', '').replace(' = ', ''))

    return {'item_card': item_json,
            #             'images': get_images(soup),
            #             'name': item_card.find('h1').text,
            #             'description': get_description(item_card),
            #             'params': get_params(item_card)
            }


def scrapy_main():
    items_list = get_items_list()

    print(f'{len(items_list)} items detected')

    items_dict = dict()

    for i, item in enumerate(items_list):
        items_dict[i] = {
            'href': get_href_for_card(item),
            'title': get_title(item),
            'in_stock': is_in_stock(item),
            'old_price': get_old_price(item),
            'price': get_new_price(item),
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



