#pip install pyvisa-py

import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np
import sys


#Initialisation du programme
rm = pyvisa.ResourceManager()
oscillo = rm.open_resource('ASRL3::INSTR')  #port serie 3
oscillo.write(":Autos") #Autoset
oscillo.write(':ACQ:RECO 1e+5') #Change le nombre de valeurs a 10000

#On récupere la data sur les 2 channels
vert_scale1,time_scale1,waveform1,high1 = lecture(1)
vert_scale2,time_scale2,waveform2,high2 = lecture(2)

#On les met en valeurs d'intensite
waveform1 = norm1(waveform1,high1)
waveform2 = norm2(waveform2,high2)

    
#On affiche le graph
x = np.linspace(-5*time_scale1,5*time_scale1,len(val))
plt.plot(x, waveform1, label="CH1")
plt.plot(x,waveform2, label="CH2")
plt.grid()
plt.xlabel("Time (s)")
plt.ylabel("Signal (V)")
plt.legend()
plt.show()

#Création des différentes fonctions utiles
def lecture(CH,N=5):
    oscillo.write(':MEAS:SOUR'+CH+' CH'+CH) #Vraiment pas sur de cette ligne
    oscillo.write(':Header on')
    time.sleep(0.5)
    oscillo.write(':ACQ'+CH+":MEM?")
    _header = oscillo.read()
    _vert_scale=float(header.split(";")[12].split(',')[1])
    _time_scale=float(header.split(";")[15].split(',')[1])
    _waveform = oscillo.read_binary_values(datatype='h') #Essayer is_big_endian=True
    _high=float(oscillo.query(":Meas:HIGH?"))
    return _vert_scale,_time_scale,_waveform,_high

def norm1(_waveform,_high) : #Ce qu'on utilise atm pour avoir les vraies valeurs de la waveform
    wave = _waveform
    for i in range(0,len(wave)) :
        wave[i] = wave[i]/max(wave)*_high
    return wave

def norm2(_waveform,_vert_scale,AD=25) : #Ce qui est sensé marcher selon la docu
    wave = _waveform
    for i in range(0,len(wave)) :
        wave[i] = wave[i]/AD * _vert_scale
    return wave


def vidage() :
    for i in range(0,1000) :
        oscillo.read_raw()


