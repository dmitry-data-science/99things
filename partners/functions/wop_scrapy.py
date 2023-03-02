from partners.functions.scrapy_functions import form_options, fix_price_to_items_dict

import requests
from bs4 import BeautifulSoup
import re
import json


dns = 'https://world-of-pop.com'


def clean_text(text):
    return text.replace('\n', '').replace('[', '').replace(']', '').strip()


def get_soup(href, dns=dns):
    cookies = {
        'secure_customer_sig': '',
        'localization': 'EN',
        '_tracking_consent': '%7B%22reg%22%3A%22%22%2C%22con%22%3A%7B%22GDPR%22%3A%22%22%7D%2C%22lim%22%3A%5B%22GDPR%22%5D%2C%22v%22%3A%222.0%22%7D',
        '_y': 'fffe05e6-555b-44d5-9bf5-3fc75f209eab',
        '_shopify_y': 'fffe05e6-555b-44d5-9bf5-3fc75f209eab',
        '_shopify_m': 'persistent',
        '_ga': 'GA1.2.482776510.1671625839',
        '_pin_unauth': 'dWlkPU1EWTNaamcyT0RRdE56ZGxOQzAwWlRVMExXRXlOemN0WldKaVkyTTBNRGRpTVRNeA',
        'poptin_user_id': '0.fgbafdmosot',
        'poptin_user_ip': '37.233.40.147',
        'poptin_user_country_code': 'MD',
        'poptin_session_account_ad9482606fe05': 'true',
        'poptin_c_visitor': 'true',
        '_orig_referrer': 'https%3A%2F%2Fworld-of-pop.com%2Fcollections%2Fall%3Fpage%3D2',
        '_landing_page': '%2Fproducts%2Ft-shirt-a-manches-courtes-en-coton-bio',
        '_shopify_tw': '',
        'cart': 'a1286ec144ac434fc6182a680ec84995',
        'cart_sig': '477049d9e1169d7be7da269c6cf9161a',
        '_s': '600684ce-830d-4583-a975-af577487c95d',
        '_shopify_s': '600684ce-830d-4583-a975-af577487c95d',
        '_shopify_tm': '',
        '_shopify_sa_p': '',
        '_gid': 'GA1.2.1138163412.1673901302',
        '_gat': '1',
        '_derived_epik': 'dj0yJnU9bHFvUEhkQ25LQjRUSU1SNlM5WGlzR3Etek5WNEJZNE8mbj1XeEVybWZ3Q19iWlNoeERHTHZZdmlBJm09ZiZ0PUFBQUFBR1BGdFBVJnJtPWYmcnQ9QUFBQUFHUEZ0UFUmc3A9Mg',
        'poptin_old_user': 'true',
        'poptin_o_v_c8f6d029b6a45': '4486bc58d2f3c',
        'poptin_session': 'true',
        'poptin_o_a_d_c8f6d029b6a45': '4486bc58d2f3c',
        'poptin_c_p_o_x_c_c8f6d029b6a45': 'c8f6d029b6a45',
        'poptin_session_account_time_ad9482606fe05': '{"set_at":1673901305939,"expiry_at":1673901385944}',
        'keep_alive': 'ceba56ff-5dab-4fd5-8949-93b83bb58b76',
        '_shopify_sa_t': '2023-01-16T20%3A35%3A28.049Z',
        '__kla_id': 'eyIkcmVmZXJyZXIiOnsidHMiOjE2NzE2MjU4NDAsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd29ybGQtb2YtcG9wLmNvbS8ifSwiJGxhc3RfcmVmZXJyZXIiOnsidHMiOjE2NzM5MDEzMjgsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd29ybGQtb2YtcG9wLmNvbS8ifX0=',
        'cart_currency': 'EUR',
        'cart_ts': '1673901329',
        'cart_ver': 'gcp-us-east1%3A24',
        '_dd_s': 'logs=1&id=11c9d691-8422-4ad0-8c65-fb3d2a66ba6f&created=1673901300164&expire=1673902231249',
    }

    headers = {
        'authority': 'world-of-pop.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US;q=0.8,en;q=0.7',
        # 'cookie': 'secure_customer_sig=; localization=FR; _tracking_consent=%7B%22reg%22%3A%22%22%2C%22con%22%3A%7B%22GDPR%22%3A%22%22%7D%2C%22lim%22%3A%5B%22GDPR%22%5D%2C%22v%22%3A%222.0%22%7D; _y=fffe05e6-555b-44d5-9bf5-3fc75f209eab; _shopify_y=fffe05e6-555b-44d5-9bf5-3fc75f209eab; _shopify_m=persistent; _ga=GA1.2.482776510.1671625839; _pin_unauth=dWlkPU1EWTNaamcyT0RRdE56ZGxOQzAwWlRVMExXRXlOemN0WldKaVkyTTBNRGRpTVRNeA; poptin_user_id=0.fgbafdmosot; poptin_user_ip=37.233.40.147; poptin_user_country_code=MD; poptin_session_account_ad9482606fe05=true; poptin_c_visitor=true; _orig_referrer=https%3A%2F%2Fworld-of-pop.com%2Fcollections%2Fall%3Fpage%3D2; _landing_page=%2Fproducts%2Ft-shirt-a-manches-courtes-en-coton-bio; _shopify_tw=; cart=a1286ec144ac434fc6182a680ec84995; cart_sig=477049d9e1169d7be7da269c6cf9161a; _s=600684ce-830d-4583-a975-af577487c95d; _shopify_s=600684ce-830d-4583-a975-af577487c95d; _shopify_tm=; _shopify_sa_p=; _gid=GA1.2.1138163412.1673901302; _gat=1; _derived_epik=dj0yJnU9bHFvUEhkQ25LQjRUSU1SNlM5WGlzR3Etek5WNEJZNE8mbj1XeEVybWZ3Q19iWlNoeERHTHZZdmlBJm09ZiZ0PUFBQUFBR1BGdFBVJnJtPWYmcnQ9QUFBQUFHUEZ0UFUmc3A9Mg; poptin_old_user=true; poptin_o_v_c8f6d029b6a45=4486bc58d2f3c; poptin_session=true; poptin_o_a_d_c8f6d029b6a45=4486bc58d2f3c; poptin_c_p_o_x_c_c8f6d029b6a45=c8f6d029b6a45; poptin_session_account_time_ad9482606fe05={"set_at":1673901305939,"expiry_at":1673901385944}; keep_alive=ceba56ff-5dab-4fd5-8949-93b83bb58b76; _shopify_sa_t=2023-01-16T20%3A35%3A28.049Z; __kla_id=eyIkcmVmZXJyZXIiOnsidHMiOjE2NzE2MjU4NDAsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd29ybGQtb2YtcG9wLmNvbS8ifSwiJGxhc3RfcmVmZXJyZXIiOnsidHMiOjE2NzM5MDEzMjgsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd29ybGQtb2YtcG9wLmNvbS8ifX0=; cart_currency=EUR; cart_ts=1673901329; cart_ver=gcp-us-east1%3A24; _dd_s=logs=1&id=11c9d691-8422-4ad0-8c65-fb3d2a66ba6f&created=1673901300164&expire=1673902231249',
        'referer': 'https://world-of-pop.com/collections/w-o-p-adulte',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    response = requests.get(f'{dns}{href}', headers=headers)
    soup = BeautifulSoup(response.text, features='html.parser')

    return soup


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
    return item.find(name='a', attrs={'class': 'full-unstyled-link'}).get('href')


def get_title(item):
    return clean_text(item.find(name='a', attrs={'class': 'full-unstyled-link'}).text)


def get_old_price(item):
    return clean_text(item.find(name='span', attrs={'class': 'price-item--regular'}).text)


def get_new_price(item):
    return clean_text(item.find(name='span', attrs={'class': 'price-item--sale'}).text)


# for product card

def get_images(soup):
    img_tags = soup.find_all(name='li', attrs={'class': 'product__media-item'})
    images_dict = dict()

    for i, img in enumerate(img_tags):
        images_dict[i] = dict()

        tag = img.find(name='img')
        src = tag.get('src')
        images_dict[i]['href'] = src[: src.rfind('=')]  # concatenate

        widths = re.findall(' [0-9]+w', tag.get('srcset'))
        images_dict[i]['widths'] = [re.findall('[0-9]+', num)[0]
                                    for num in
                                    widths]

    return images_dict


def get_description(item_card):
    return item_card.find(name='div', attrs={'class': 'product__description'}).renderContents().decode()


def get_params(item_card):
    params_list = item_card.find_all(name='div', attrs={'class': 'vario-variant-wrapper'})

    return {clean_text(params.label.text): [x.get('data-value') for x in params.find_all(name='li')] for params in
            params_list}


def get_data_from_card(soup):
    #     item_card = soup.find(name='div', attrs={'class', 'product-single__meta'})
    item_json = json.loads(soup.find(name='script', attrs={'id': 'vario-product-json'}).string)

    return {
        'item_card': item_json,
        'images': get_images(soup),
        #             'name': soup.find('h1').text,
        #             'description': get_description(soup),
        #             'params': get_params(soup)
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