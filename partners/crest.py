from partners.functions.crest_scrapy import scrapy_main
from partners.functions.shopify_api import *

vendor = 'CREST'

def update_crest():
    partners_items_dict = scrapy_main()
    our_shop_product_list = get_prod_list(vendor)

    variants_dict = get_variants_dict(partners_items_dict, our_shop_product_list)

    # update_variants_quantity(variants_dict)

    return variants_dict