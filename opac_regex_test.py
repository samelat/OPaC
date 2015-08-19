#!/usr/bin/python3

from opac.opac_regex import OPaCRegex

kwords = [
    'algo__dolares-reservas-cepo-herencia_0_1412858778.html',
    'algo_Volvio-luego-tormentas-preven-tiempo_0_1412858913.html',
    'algo__Salto-evacuados-podria-regresar-manana_0_1412858945.html',
    'algo_Inundaciones-evacuados-Lujan-Areco-lluvias_0_1412858806.html',
    'algo__scioli-inundaciones-macri_0_1412858912.html',
    'algo_Paz-social-Acuerdo-oficial-inflacion_0_1412858813.html'
]

oregex = OPaCRegex()
regex = oregex.digest(kwords)

for keyword in kwords:
    print(keyword)
print()

print(regex)


