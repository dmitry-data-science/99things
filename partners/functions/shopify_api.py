import requests
import time

from partners.functions.credentials import get_credentials


credentials = get_credentials()
api_key = credentials['api_key']
shared = credentials['shared']
shop = credentials['shop']

url = f'https://{api_key}:{shared}@{shop}.myshopify.com/admin/api/2022-10/'
# endpoint = 'products.json'
location_id = 70944456922

available_variant_quantity = 5


def get_prod_list(vendor, url=url, endpoint='products.json'):
    response = requests.get(url + endpoint, params={'vendor': vendor})

    return response.json()['products']


def get_inventory_level(inventory_item_id, location_id=location_id):
    params = {
        'location_ids': location_id,
        'inventory_item_ids': inventory_item_id
    }

    response = requests.get(
        f'{url}inventory_levels.json',
        params=params,
    )

    return response.json()['inventory_levels']


# form a dictionary. Key is a variant_id from our shop, value is a variant_id form partners shop
# plus availability - the data from a partners website
def get_variants_dict(partners_items_dict, our_shop_product_list):

    source_variants = list() # variants from partners website
    target_variants = list() # variants from our website

    # form a source list - the data from partners website
    for item in [card['card']['item_card'] for card in partners_items_dict.values()]:
        source_variants.extend([(item['handle'],
                                 v['title'],
                                 v['id'],
                                 v['available'],
                                 v['price'] / 100 # shopify add two extra characters for cents
                                 ) for v in item['variants']])

    # form a target list - the data from our website
    for item in our_shop_product_list:

        target_variants.extend([(item['handle'],
                                 v['title'],
                                 v['inventory_item_id'],
                                 float(v['price']) # shopify thing that a price is string :-)
                                 ) for v in item['variants']])

    variants_dict = dict()

    # join both of our lists
    for t_prod_handle, t_var_title, t_var_id, t_price in target_variants:
        for s_prod_handle, s_var_title, s_var_id, s_available, s_price in source_variants:
            if all((t_prod_handle == s_prod_handle, t_var_title == s_var_title)):
                variants_dict[t_var_id] = {'s_var_id': s_var_id, # variant_id of partners item
                                           's_available': s_available, # is the partners item available?
                                           's_price': s_price, # partners variant price
                                           't_price': t_price, # our variant price
                                           }
                break

    return variants_dict


def update_variants_quantity(variants_dict,
                             location_id=location_id,
                             available_variant_quantity=available_variant_quantity):
    for inv_id in variants_dict.keys():

        available = get_inventory_level(inv_id)[0]['available'] or 0
        desired_value = available_variant_quantity if variants_dict[inv_id]['s_available'] else 0

        params = {
            'inventory_item_id': inv_id,
            'location_id': location_id,
            'available_adjustment': desired_value - available
        }

        response = requests.post(f'{url}inventory_levels/adjust.json', json=params)

        print(f'{inv_id} : {response.text}')
        time.sleep(1)

    print('update_variants_quantity procedure completed')
