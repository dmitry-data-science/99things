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

    print(f'inventory: {inventory_item_id} - {response.text}')
    return response.json()['inventory_levels']


def var_params_updating(var_id, params_dict):
    json_data = {
        'variant': {'id': var_id, **params_dict},
    }
    response = requests.put(f'{url}variants/{var_id}.json', json=json_data)
    print(response.status_code)

    return response


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
                                 v['id'],
                                 float(v['price']),  # shopify thing that a price is string :-)
                                 v['inventory_quantity'],
                                 ) for v in item['variants']])

    variants_dict = dict()

    # join both of our lists
    for t_prod_handle, t_var_title, t_inv_id, t_var_id, t_price, inventory_quantity in target_variants:
        for s_prod_handle, s_var_title, s_var_id, s_available, s_price in source_variants:
            if all((t_prod_handle == s_prod_handle, t_var_title == s_var_title)):
                variants_dict[t_inv_id] = {'s_var_id': s_var_id,  # variant_id of partners item
                                           's_available': s_available,  # is the partners item available?
                                           's_price': s_price,  # partners variant price
                                           't_price': t_price,  # our variant price
                                           't_var_id': t_var_id,
                                           'inventory_quantity': inventory_quantity,
                                           }
                break

    return variants_dict


def update_variants_quantity(variants_dict,
                             location_id=location_id,
                             available_variant_quantity=available_variant_quantity):
    for inv_id in variants_dict.keys():

        available = get_inventory_level(inv_id)[0]['available'] or 0
        time.sleep(0.5)
        desired_value = available_variant_quantity if variants_dict[inv_id]['s_available'] else 0

        quantity_diff = desired_value - available

        if not quantity_diff:
            continue

        var_params_updating(variants_dict[inv_id]['t_var_id'], {'inventory_management': 'shopify'})


        print(f'{inv_id} : {quantity_diff} - {variants_dict[inv_id]}')

        params = {
            'inventory_item_id': inv_id,
            'location_id': location_id,
            'available_adjustment': quantity_diff
        }

        response = requests.post(f'{url}inventory_levels/adjust.json', json=params)

        print(f'{inv_id} : {response.text}')
        time.sleep(1)

    print('update_variants_quantity procedure completed')


def update_prices(variants_dict):

    variants_dict_with_price_diff = {k: v for k, v in variants_dict.items() if v['s_price'] != v['t_price']}

    if not variants_dict_with_price_diff:
        print('There are not price differences')
        return None

    print(f'{len(variants_dict_with_price_diff)} price differences are found')

    for v in variants_dict_with_price_diff.values():
        print(v)
        json_data = {
            'variant': {'id': v['t_var_id'], 'price': v['s_price']},
        }

        response = requests.put(f'{url}variants/{v["t_var_id"]}.json', json=json_data)
        print(f'{v["t_var_id"]} - {v["s_price"]} - {response.status_code}')

    print('update_variants_quantity procedure completed')

