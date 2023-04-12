from partners.functions.crest_scrapy import scrapy_main

from partners.functions.scrapy_functions import update_items_dict
from partners.functions.shopify_api import *


vendor = 'CREST'

def update_crest():
    # requests for product lists: from partners website and from our
    partners_items_dict = scrapy_main()
    our_shop_product_list = get_prod_list(vendor)

    # add new product
    new_items = get_new_items(partners_items_dict, our_shop_product_list)
    # partners_new_items_dict = update_items_dict(new_items, vendor, dns_for_selenium='https://crestclothing.com')
    partners_new_items_dict = update_items_dict(new_items, vendor)
    add_new_items_to_site(partners_new_items_dict)

    # update our product list
    our_shop_product_list = get_prod_list(vendor)

    # get dictionary of variants for all our product
    variants_dict = get_variants_dict(partners_items_dict, our_shop_product_list)

    # updating of quantity, prices, visibility
    update_variants_quantity(variants_dict)
    update_prices(variants_dict)
    update_prod_visibility(vendor, partners_items_dict)

    return True