import requests
from bs4 import BeautifulSoup
import json
import base64

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

    return items_dict