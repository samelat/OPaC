
from opac_regex import OPaCRegex

kwords = [
    'dolares-reservas-cepo-herencia_0_1412858778.html',
    'Volvio-luego-tormentas-preven-tiempo_0_1412858913.html',
    'Salto-evacuados-podria-regresar-manana_0_1412858945.html',
    'Inundaciones-evacuados-Lujan-Areco-lluvias_0_1412858806.html',
    'scioli-inundaciones-macri_0_1412858912.html',
    'Paz-social-Acuerdo-oficial-inflacion_0_1412858813.html'
#    'desbordo-Quilmes-sudestada-espera-crecida_0_1411658971.html'
]

oregex = OPaCRegex(kwords)
regex = oregex.digest()

print(regex)


