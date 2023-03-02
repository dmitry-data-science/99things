import requests
import time
import base64

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
    response = requests.get(url + endpoint, params={'vendor': vendor, 'limit': 250})

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

    # print(f'inventory: {inventory_item_id} - {response.text}')
    return response.json()['inventory_levels']


def prod_params_updating(prod_id, params_dict):
    json_data = {
        'product': {
            'id': prod_id,
            **params_dict
        },
    }

    response = requests.put(f'{url}products/{prod_id}.json', json=json_data)
    print(response.status_code)

    return response


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

    source_variants = list()  # variants from partners website
    target_variants = list()  # variants from our website

    # form a source list - the data from partners website
    for item in [card['card']['item_card'] for card in partners_items_dict.values()]:
        source_variants.extend([(item['handle'],
                                 v['title'],
                                 v['id'],
                                 v['available'],
                                 v['price'],  # shopify add two extra characters for cents
                                 v['compare_at_price'] if v['compare_at_price'] is not None else None,  # shopify add two extra characters for cents
                                 ) for v in item['variants']])

    # form a target list - the data from our website
    for item in our_shop_product_list:

        target_variants.extend([(item['handle'],
                                 v['title'],
                                 v['inventory_item_id'],
                                 v['id'],
                                 float(v['price']),  # shopify thing that a price is string :-)
                                 float(v['compare_at_price']) if v['compare_at_price'] is not None else None,
                                 v['inventory_quantity'],
                                 ) for v in item['variants']])

    variants_dict = dict()

    # join both of our lists
    for (t_prod_handle,
         t_var_title,
         t_inv_id,
         t_var_id,
         t_price,
         t_compare_at_price,
         inventory_quantity) in target_variants:
        for (s_prod_handle,
             s_var_title,
             s_var_id,
             s_available,
             s_price,
             s_compare_at_price) in source_variants:
            if all((t_prod_handle == s_prod_handle, t_var_title == s_var_title)):
                variants_dict[t_inv_id] = {'s_var_id': s_var_id,  # variant_id of partners item
                                           's_available': s_available,  # is the partners item available?
                                           's_price': s_price,  # partners variant price
                                           't_price': t_price,  # our variant price
                                           's_compare_at_price': s_compare_at_price,  # partners variant price
                                           't_compare_at_price': t_compare_at_price,  # our variant price
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
    variants_dict_with_price_diff = dict()

    for k, v in variants_dict.items():
        if ((v['s_price'] != v['t_price'])  # price change
                # check to compare_at_price changing
            | (all([v['s_compare_at_price'], v['t_compare_at_price']])
               & (v['s_compare_at_price'] != v['t_compare_at_price']))  # both are not None and not equal

            | ((v['s_compare_at_price'] is None) & (v['t_compare_at_price'] is not None)
                | (v['s_compare_at_price'] is not None) & (v['t_compare_at_price'] is None)  # only one of them is equal None
                )
        ):
            variants_dict_with_price_diff[k] = v

    # variants_dict_with_price_diff = {k: v
    #                                  for k, v
    #                                  in variants_dict.items()
    #                                  if (v['s_price'] != v['t_price']) | (v['s_compare_at_price'] != v['t_compare_at_price'])}

    if not variants_dict_with_price_diff:
        print('There are not price differences')
        return None

    print(f'{len(variants_dict_with_price_diff)} price differences are found')

    for v in variants_dict_with_price_diff.values():
        print(v)
        json_data = {
            'variant': {'id': v['t_var_id'], 'price': v['s_price'], 'compare_at_price': v['s_compare_at_price']},
        }

        response = requests.put(f'{url}variants/{v["t_var_id"]}.json', json=json_data)
        print(f'{v["t_var_id"]} - {v["s_price"]} - {response.status_code}')
        print(json_data)

    print('update_variants_quantity procedure completed')


def update_prod_visibility(vendor, partners_items_dict):
    our_shop_product_list = get_prod_list(vendor)

    prod_list_for_visability = (
        {prod['id']:
            (
                 'active' if any([v['inventory_quantity'] for v in prod['variants']]) else 'archived',   # if any variants available
                 prod['status']  # if active - True, if archived - False
             )
         for prod in our_shop_product_list
         if prod['status'] != 'draft'})  # product is not draft

    # list (dict) of unavailable products
    prod_list_for_change = {prod_id: status[0]
                            for prod_id, status
                            in prod_list_for_visability.items()
                            if status[0] != status[1]}


    # list (dict) of product which is absent on the partners website
    # handles set of absent products
    handles_in_source = {item['card']['item_card']['handle'] for item in list(partners_items_dict.values())}
    # handles_in_target = {prod['handle'] for prod in our_shop_product_list if prod['status'] != 'archived'}
    handles_in_target = {prod['handle'] for prod in our_shop_product_list}  # if partners product doesn't exists and we have variants quantity, this line will update "archived" status
    absent_handles_set = handles_in_target.difference(handles_in_source)
    # absent products dictionary. Product_id: 'archived'
    absent_products_dict = {prod['id']: 'archived' for prod in our_shop_product_list if prod['handle'] in absent_handles_set}

    # updating prod_list_for_change with absent_products_dict
    prod_list_for_change = {**prod_list_for_change, **absent_products_dict}
    print(f'products for change visability: {prod_list_for_change}')


    if prod_list_for_change:
        print(f'{len(prod_list_for_change)} products for status updating')

        for prod_id, status in prod_list_for_change.items():
            # prod_params_updating(prod_id, {'status': status[0]})
            # print(f'Status of {prod_id} is changed for {status[0]}')
            prod_params_updating(prod_id, {'status': status})
            print(f'Status of {prod_id} is changed for {status}')

    print('All changes are done')


def get_new_items(partners_items_dict, our_shop_product_list):
    handles_in_source = {item['card']['item_card']['handle'] for item in list(partners_items_dict.values())}
    handles_in_target = {prod['handle'] for prod in our_shop_product_list if prod['status'] != 'archived'}

    new_items_handles = handles_in_source.difference(handles_in_target)

    new_items = {k: v for k, v in partners_items_dict.items() if v['card']['item_card']['handle'] in new_items_handles}

    return new_items


def get_image(image):
    name = image.split('?')[0].split('/')[-1]
    image_bytes = base64.b64encode(requests.get('https:' + image).content).decode()

    return image_bytes, name


def add_new_items_to_site(partners_new_items_dict, endpoint='products.json'):

    for cur_product in partners_new_items_dict.values():

        # print()
        # print('add_new_items_to_site')
        # print(cur_product)

        response_product = requests.post(url + endpoint, json={'product': cur_product['card']['item_card']})
        if response_product.ok:
            print(response_product.json()['product']['handle'], 'is created')
        else:
            print('Error with creation of ', cur_product['handle'])
            #         break
            continue

        prod_id = response_product.json()['product']['id']

        for image in cur_product['card']['item_card']['images']:
            image_bytes, name = get_image(image)

            json_data = {
                'image': {
                    'attachment': image_bytes,
                    'filename': name,
                },
            }
            print('add image', requests.post(f'{url}products/{prod_id}/images.json', json=json_data))

        break  # for testing we should add the one new product only

