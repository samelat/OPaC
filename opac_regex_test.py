#!/usr/bin/python3

from opac.opac_regex import OPaCRegex

kwords0 = [
    'Guillermina_Valdes-separacion-Marcelo_Tinelli-fue-al-teatro_0_1321668164.html',
    'DVD-Tuya-Claudia_Pineiro-Andrea_Pietra-Jorge_Marrale-Juana_Viale-Edgardo_Gonzalez_Amer_0_1395460874.html',
    'Gianinna_Maradona-exploto-bronca-me-tienen-podrida_0_1268273408.html',
    'Lucia_Celasco-Susana_Gimenez-Punta_del_Este-sensual-transparencias-sexy-nieta-joven-atuendo_0_1277872478.html',
    'Andres_Calamaro-Micaela_Breque-Punta_del_Este-chivito-uruguayo-La_Barra-dieta-pescado-kilos_de_mas_0_1303069985.html'
]

kwords1 = [
    ''
]

oregex = OPaCRegex()
regex = oregex.digest(kwords0)

for keyword in kwords:
    print(keyword)
print()

print(regex)


