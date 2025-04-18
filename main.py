# -*- coding: utf-8 -*-
# Le but de ce pprogramme est de tester si on peut conttroller l'oscillo en manipulant des string

#pip install pyvisa-py

import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np


#On détecte les instruments de mesure par leur nom déclaré dans *IDN?
rm = pyvisa.ResourceManager()
L=rm.list_resources() 
for i in range(0, len(L)) :
    try :
        instrument=rm.open_resource(L[i-1])
        try :
            nom= instrument.query("*IDN?")
            if nom.split(",")[0].strip("'")=="GW" :
                oscillo = instrument
            elif nom.split(" ")[0].strip(",")=="Rigol" :
                gbf = instrument
        except :
            print("")
    except : 
        print("")


#Création des différentes fonctions utiles


#Fonction permettant juste de demander a l'utilisateur de modifier des valeurs du gbf
def question(_period,_volt, _duty) :
    answer = input("Que voulez vous modifier ? (volt,period,duty)")
    val = ""
    if answer == "volt" :
        while type(val) != type(0.5) :
            val = input("Donner la nouvelle valeur de potentiel : ")
            try :
                val = float(val)
                _volt = val
            except :
                print ("erreur {} pas un float".format(val))
    elif answer == "period" :
        while type(val) != type(0.5) :
            val = input("Donner la nouvelle valeur de la periode : ")
            try :
                val = float(val)
                _period = val
            except :
                print ("erreur {} pas un float".format(val))
    elif answer == "duty" :
        while type(val) != type(0.5) :
            val = input("Donner la nouvelle valeur du duty entre 0 et 100 (%) : ")
            try :
                val = float(val)
                if val >= 0 and val <= 100 :
                    _duty = val
                else :
                    print ("La valeur donnéee n'est pas entre 0 et 100, on conserve la valeur précédente")
            except :
                print ("erreur {} pas un float".format(val))
    else : 
        print ("La valeur donnée a modifier n'est pas correcte")
    print ("Les valeurs rentrées sont : \nVolt = {}\nPeriode = {}\nDuty = {} %".format(_volt,_period,_duty))
    answer = input("Voulez vous modifier une valeur ? (y/n)")
    if answer == "y" :
        _period,_volt,_duty = question(_volt,_period,_duty)# recursivité du code
    return _period,_volt,_duty


def getGBF () :
    _period = gbf.query(":SOURce:PERiod?")
    _duty = gbf.query (":SOURce:PULSe:DCYCle?")
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

def lecture(CH):
    # oscillo.write(':MEAS:SOUR'+str(CH)+' CH'+str(CH))
    #oscillo.write(':MEAS:SOUR1 CH'+str(CH))
    time.sleep(1)
    oscillo.write(':ACQ'+str(CH)+":MEM?")
    _header = oscillo.read()
    try : #Parfois le header contient juste un \n (Pourquoi ?) donc on try, si ca marche ok, sinon on reread le header
        _vert_scale=float(_header.split(";")[12].split(',')[1])
        _time_scale=float(_header.split(";")[15].split(',')[1])
    except:
        _header = oscillo.read()
        _vert_scale=float(_header.split(";")[12].split(',')[1])
        _time_scale=float(_header.split(";")[15].split(',')[1])
    if CH == 2 :
        time.sleep(1) #A supprimer si ca fait crash lecture 2, le programme est encore assez instable, c'est un fix qui semble régler le soucis néanmoins
    try :
        _waveform = oscillo.read_binary_values(datatype='h',is_big_endian=True) 
    except :
        print ("erreur dans la mesure de la waveform du channel {}".format(CH))
        _waveform = np.zeros(10000)
    return _vert_scale,_time_scale,_waveform



def norm(_waveform,_vert_scale,AD=25) : #Permet de remettre la waveform en unité de potentiel
    wave = _waveform
    for i in range(0,len(wave)) :
        wave[i] = wave[i]/AD * _vert_scale
    return wave


def vidage(instr=oscillo) : #Fonction qui vide juste toutes les données a lire jusqu'au prochain crash
    k = 0
    while k == 0 :
        try :
            instr.read_raw()
            vidage()
        except :
            k = 1

def sauvegarde(fichier,t,liste,liste2) : #Save au format csv
    with open(fichier,'w') as file :
        for i in range (0, len(t)) :
            file.writelines([str(t[i]),",",str(liste[i]),",",str(liste2[i]),"\n"])

def graph(_waveform1, _waveform2,_t1, _t2):
    plt.plot(_t1, _waveform1,'orange', label="CH1")
    plt.plot(_t2,_waveform2,'c', label="CH2")
    plt.grid()
    plt.xlabel("Time (s)")
    plt.ylabel("Signal (V)")
    plt.legend()
    plt.show()

def notation_inge(nb) : #Fonction qui ressort n'importe quel nombre en notation inge lisible par l'oscillo
    if nb < 0 :
        string = "-"+notation_inge(-nb)
    else :
        exposant = int(np.floor(np.log10(nb)))
        nb = round(nb*10**(-1*exposant),5) #Round a changer
        nb = int(str(nb)[0])
        if nb != 1 and nb != 2 and nb != 5 :
            if nb > 5 :
                nb = 1
                exposant += 1
            elif nb > 2 :
                nb = 5
            elif nb > 1 :
                nb = 2
        string = str(nb)+"e"+str(exposant)
    return string

def notation_inge2(nb) : #Fonction qui ressort n'importe quel nombre en notation inge lisible par l'oscillo, plus précise que la premiere fonction
    if nb < 0 :
        string = "-"+notation_inge(-nb)
    else :
        exposant = int(np.floor(np.log10(nb)))
        nb = round(nb*10**(-1*exposant),5) #Round a changer
        nb = int(str(nb)[0])
        string = str(nb)+"e"+str(exposant)
    return string

def max_index(waveform1): #Fonction retournant l'index de valeur maximal d'une liste
    max_value = waveform1[0]
    max_index = 0
    for i in range(1, len(waveform1)):
        if waveform1[i] > max_value:
            max_value = waveform1[i]
            max_index = i
    return max_index

############################################################################################
        
#On check que les deux appereilles fonctionnent
print(oscillo.query("*IDN?"))
print(gbf.query("*IDN?"))
vidage()

#oscillo.timeout = 5000
oscillo.write(":ACQUIRE:MODE AVERAGE")
oscillo.write(":ACQUIRE:AVErage 128")
oscillo.write(':ACQ:RECO 1e+5') #Nombre de points (resolution) par defaut a 10000 points
gbf.write(":SOURce:FUNCtion PULSE") #On établit la forme du signal comme un pulse (a voir si il faut changer avec SQUare)

#On récupère toutes les données du gbf
gbf_period, gbf_volt, gbf_duty = getGBF()
gbf_period = float(gbf_period) # intialement les variables sont des String
gbf_volt = float(gbf_volt)
gbf_duty = float(gbf_duty)

#On demande a l'utilisateur de les changer
print ("Les valeurs rentrées sont : \nVolt = {}\nPeriode = {}\nDuty = {} %".format(gbf_volt,gbf_period,gbf_duty))
answer = input("Voulez vous modifier une valeur ? (y/n)")
if answer == "y" :
    gbf_period,gbf_volt,gbf_duty = question(gbf_period,gbf_volt,gbf_duty)

#On change les valeurs du gbf et on change la timebase de l'oscillo
setGBF(gbf_period,gbf_volt,gbf_duty)
oscillo.write(":TRIGger:SOURce CH1") 
oscillo.write(":TRIgger:Level "+notation_inge2(gbf_volt/4))
timescale_str = notation_inge(gbf_period/10) #periode/10 car 10 divisions sur l'oscillo
oscillo.write(":TIMebase:SCALe "+timescale_str)

time_pos = float(oscillo.query(":TIMebase:POSition?")) #on recupere le curseur

#position relative du curseur vertical
#On fait une premiere mesure pour bien aligner le timepos pour bien voir toute la figure sur notre écran
vert_scale1,time_scale1,waveform1 = lecture(1)
t1 = np.linspace(-5*time_scale1,5*time_scale1,len(waveform1)) #abscisse temporel de chaque points
vidage()
time_pos = notation_inge2(time_pos + t1[max_index(waveform1)] +4*time_scale1) #On cherche à mettre le max au debut du signal
oscillo.write(":TIMebase:POSition "+time_pos)

#Vraie bonne mesure de notre oscillo
vert_scale1,time_scale1,waveform1 = lecture(1) #recupere tous les points du signal
time.sleep(1)
vert_scale2,time_scale2,waveform2 = lecture(2)
waveform1 = norm(waveform1,vert_scale1)
waveform2 = norm(waveform2,vert_scale2)

#normalement t1=t2
t1 = np.linspace(-5*time_scale1,5*time_scale1,len(waveform1))
t2 = np.linspace(-5*time_scale2,5*time_scale2,len(waveform2))

graph(waveform1,waveform2,t1,t2)
vidage()

#On demande a l'utilisateur s'il veut enregistrer son fichier
sav = input("Désirez vous sauvegarder les données ? (y/n)")
if sav == "y" :
    try :
        fichier = input("Indiquer le nom du fichier : ")
        sauvegarde(fichier,t1,waveform1,waveform2)
    except :
        print ("Une erreur est survenue, enregistrement impossible")
