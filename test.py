# Le but de ce pprogramme est de tester si on peut conttroller l'oscillo en manipulant des string

import pyvisa

rm = pyvisa.ResourceManager()
oscillo = rm.open_resource('ASRL3::INSTR')

string = "Autoset"
oscillo.write(string)
string = "Meas:"+"High?"
print(oscillo.query(string))

def bestTimeScale (liste,t,max_index) :
    max = liste[max_index]
    res =  False
    i = max_index
    compteur == 0
    while (i < len(liste)) and (compteur != 10):
        if liste[i] < max/100 :
            compteur += 1
        else :
            compteur = 0
        i += 1
    if compteur == 10 :
        res = (t[i]-t[max_index])*1.1/10
    return res
        


