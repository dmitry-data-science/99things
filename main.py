from partners.crest import update_crest
from credentials import *

items_dict = update_crest()
print(items_dict)

api_key, shared, secret, shop = get_credentials()
print(api_key, shared, secret, shop)