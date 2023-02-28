from partners.crest import update_crest
from partners.lnestudio import update_lnestudio

result_crest = update_crest()
print(f'result for CREST: {result_crest}')

result_lnestudio = update_lnestudio()
print(f'result for lnestudio: {result_lnestudio}')
