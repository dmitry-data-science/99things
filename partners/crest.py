from partners.functions.crest_scrapy import scrapy_main


def update_crest():
    items_dict = scrapy_main()

    return items_dict