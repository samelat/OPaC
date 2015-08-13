
from opac_regex import OPaCRegex

kwords = [
    'algo_phishing_unlp_20095645',
    'algo_phishing_unlp_20090608',
    'algo_joomla_20090701'
]

oregex = OPaCRegex(kwords)
oregex.digest()