from partners.crest import update_crest
from partners.lnestudio import update_lnestudio
from partners.wop import update_wop

result_crest = update_crest()
print(f'result for CREST: {result_crest}')

result_lnestudio = update_lnestudio()
print(f'result for lnestudio: {result_lnestudio}')

# result_wop = update_wop()
# print(f'result for wop: {result_wop}')
