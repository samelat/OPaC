
from graph import OPaCRegex

kwords = [
    'algo_phishing_unlp_20095645',
    'algo_phishing_unlp_20090608',
    'algo_joomla_20090701',
    'desbordo-Quilmes-sudestada-espera-crecida_0_1411658971.html'
]

oregex = OPaCRegex(kwords)
oregex.digest()


