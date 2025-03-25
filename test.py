# Le but de ce pprogramme est de tester si on peut conttroller l'oscillo en manipulant des string

import pyvisa

rm = pyvisa.ResourceManager()
oscillo = rm.open_resource('ASRL3::INSTR')

string = "Autoset"
oscillo.write(string)
string = "Meas:"+"High?"
print(oscillo.query(string))