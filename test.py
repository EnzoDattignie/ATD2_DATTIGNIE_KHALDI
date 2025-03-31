# Le but de ce pprogramme est de tester si on peut conttroller l'oscillo en manipulant des string

import pyvisa


def getGBF () :
    _period = gbf.query(":SOURce:PERiod?")
    _duty = gbf.query (":SOURce:DCYCle?")
    _volt = gbf.query(":SOURce:VOLTage?")
    vidage(gbf)
    return _period, _volt, _duty


def setGBF (period, voltage, duty) :
    gbf.write(":SOURce:PERiod "+str(period))
    gbf.write(":SOURce:VOLTage "+str(voltage))
    if duty > 100 or duty < 0 :
        print ("Duty values incorrect, set to 1%")
        duty = 1
    gbf.write(":SOURce:PULSe:DCYCle "+str(duty))
    vidage(gbf)

    rm = pyvisa.ResourceManager()
oscillo = rm.open_resource('ASRL3::INSTR')  #port serie 3
gbf = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA241701521::INSTR') #Remplacer par le bon port

#On check que les deux fonctionnent
print(oscillo.query("*IDN?"))
print(gbf.query("*IDN?"))
vidage()
        

