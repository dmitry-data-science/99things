from partners.functions.crest_scrapy import scrapy_main, source_target_matching_for_handler, update_items_dict
from partners.functions.shopify_api import *

vendor = 'CREST'

def update_crest():
    partners_items_dict = scrapy_main()
    our_shop_product_list = get_prod_list(vendor)

    # partners_items_dict, our_shop_product_list_replaced, new_items_handles = \
    #     source_target_matching_for_handler(partners_items_dict, our_shop_product_list)


    # variants_dict = get_variants_dict(partners_items_dict, our_shop_product_list_replaced)
    variants_dict = get_variants_dict(partners_items_dict, our_shop_product_list)

    update_variants_quantity(variants_dict)
    update_prices(variants_dict)
    update_prod_visibility(vendor)

    # new_items = get_new_items(partners_items_dict, our_shop_product_list_replaced)
    # partners_new_items_dict = update_items_dict(new_items)
    # add_new_items_to_site(partners_new_items_dict)

    return True