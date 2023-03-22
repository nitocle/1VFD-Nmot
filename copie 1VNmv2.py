#1VNmV2 Version tempo test
#1Vnm pour 1 VFD n moteurs.

#!/usr/bin/env python

#Les imports
import minimalmodbus as mmbus
#mmbus.CLOSE_PORT_AFTER_EACH_CALL = True
import serial, time, gpiozero
from gpiozero import Button
import os
from gpiozero import LED
from gpiozero import Buzzer
from threading import Thread 
#configuration liaison (ne pas modifier)
ins = mmbus.Instrument('/dev/ttyUSB0', 1, mode="rtu")
#ins.debug = True #info pratique pour le dev
ins.serial.baudrate = 9600 #valeur unique pour les CR200X
ins.serial.bytesize = 8                                                                       
ins.serial.parity = serial.PARITY_NONE
ins.serial.stopbits = 1
ins.serial.timeout = 3

#verification du fonctionnement du VFD
#si besoin affichage erreur et alarme
#sinon affichage attente choix moteur

while True:
    try:
        print(ins.read_register(41),"VFD OK")
        print("Votre choix de moteur ?")
        break
    
    except IOError:
        print("VDF en erreur")
        print("Revoir connexion")
        i=10
        while i>1:
            print("essai ",i," sec")
            time.sleep(1)
            i-=1

            
#declarations
relaymot0 = gpiozero.OutputDevice(14, active_high=False, initial_value=False)
button0 = Button(13, pull_up = False, bounce_time = 0.5)#moteur 0 veut la main
led0 = LED(26) #correspond moteur 0
relaymot1 = gpiozero.OutputDevice(15, active_high=False, initial_value=False)
button1 = Button(19, pull_up = False, bounce_time = 0.5)#moteur 1 veut la main
led1 = LED(20) #correspond moteur 1
relaymot2 = gpiozero.OutputDevice(18, active_high=False, initial_value=False)
button2 = Button(16, pull_up = False, bounce_time = 0.5)#moteur 2 veut la main
led2 = LED(21) #correspond moteur 2

buttonemergent = Button(12, pull_up=True)
#buttonshutdown = Button(4)
buttonreverse = Button(6,pull_up=False)
ledreverse = LED(5)
global moteurs
moteurs=[0,1,2]
ledmot=[led0,led1,led2]
relaymot=[relaymot0,relaymot1,relaymot2]

#global listevaleursinterdisantdemarrage

def demarre(button):
    global nmot
    global listevaleursinterdisantdemarrage

    print("Demande d'alimentation par le bouton ",str(button.pin.number))
    if (button.pin.number==13):
        nmot=0
    if (button.pin.number==19):
        nmot=1
    if (button.pin.number==16):
        nmot=2
    # faire clignoter led moteur concerné, acquitement demande
    #verif que pas de moteur en route (si oui alarm)
    # leds=ledmot[nmot]
    ledmot[nmot].blink()

    listevaleursinterdisantdemarrage = [1,2,4]
    if (ins.read_register(4096))in listevaleursinterdisantdemarrage or (ins.read_register(12290)!=0): #si moteur pas stop ou si ampérage différent de 0 
        #display.text("Impossible",1)
        print('Impossible moteur en service',ins.read_register(4096))
        ledmot[nmot].off() 
    else:
        #couper les alim, eteindre led
        for i in range(len(moteurs)):
            relaymot[i].off()
            ledmot[i].off()
        ledmot[nmot].blink(0.6)
        #chargement des param du moteur demandé
        #display.text("charge parametres",1)
        #display.text("en cours mot."+nmot,2)
        writeparamset('referent') #mise au set de reference des paramétres
        print("Fin chargement param de reference")
        writeparamset(nmot)#mise des parametres au set du moteur demandé,
        print("Fin de chargement parametres du mot."+str(nmot))
        #affichage du moteur en service
        #display.text("Param charges",1)
        #display.text("Mot "+nmot+" en service",2)
        #print("Param charges")
        print("Mot ",nmot," en service")
        safestart(nmot,listevaleursinterdisantdemarrage)
        #while True:
        #    print(ins.read_register(4096),"valeur du param 4096")
        #    print(ins.read_register(4097),"valeur du param 4097")
        #    time.sleep(1)
            
def safestart(nmot,listevaleursinterdisantdemarrage):
    
    print("test secu demarrage intempestif")
    print (nmot)
    print (listevaleursinterdisantdemarrage)
    # stocker la frequence dans une variable nivfreq
    nivfreq = ins.read_register(12288)
    print("stockage de la frequence dans une variable nivfreq, NIC COURANT-",nivfreq)
    # stocker leorigine controle frequences dans une variable orifreq        
    orifreq=ins.read_register(1)
    print("stockage orgine controle frequence dans une variable orifreq", orifreq)
    # la ferquance est controlée par le pi
    ins.write_register(1,7)
    print ("la ferquance est controlée par le pi")
    # mettre frequence à 0
    ins.write_register(8192,0)
    print ("la ferquance est à 0")
    relaymot[nmot].on()#alimentation du moteur et de la telecommande
    print(ins.read_register(4096),"valeur du param 4096")
    print(ins.read_register(4097),"valeur du param 4097")
    ledmot[nmot].blink(0.5)
    while (ins.read_register(4096) in listevaleursinterdisantdemarrage or ins.read_register(4097) in listevaleursinterdisantdemarrage): #start is non off
       time.sleep(1)
       print ("alarme risque de démarrage intempestif,")
    # remettre la fréquence à freq
    nivfreq=int((nivfreq/50)*100)
    print("variable nivfreq, en % de 50",nivfreq)
    ins.write_register(8192,nivfreq)
    # remettre le controle de fréquences
    ins.write_register(1,int(orifreq))
    ledmot[nmot].on()#allumage led locale fixe +bip
        
def writeparamset(fichier):#ouvre le fichier texte passé en parametre, lit chaque ligne, une ligne c'est un param et sa valeur
    print ('Chargement des parametres du fichier ',fichier)
    file = open(str(fichier)+'.txt', "r")
    line = file.readline() # utilisez readline() pour lire la première ligne
    while line:
        para=line.split()
        print (para)
        print('para0 ',para[0])
        print('para1 ',para[1])
        ins.write_register(int(para[0]),int(para[1]))
        line = file.readline()# utilisez readline() pour lire la ligne suivante
    file.close()

def stoppy():
    print("Arrêt du Pi en cours...")
    os.system("sudo shutdown -h now")


def emergencystop():
    global nmot
    #pause 2 secondes pour permettre l'injection de courant de freinage
    time.sleep(2)
    print(ins.read_register(8192),'htz à l netrée en au')
    print(ins.read_register(12289),'frequence courante netrée en au')
    print(ins.read_register(12288),'frequence cible netrée en au')

    #couper les alim, clignotememnt de toutes les led
    
    for i in range(len(moteurs)):
        print ('i =',i)
        ledmot[i].off()
        relaymot[i].off()
        ledmot[i].blink(0.05)

    #mettre le moteurs sur stop
    ins.write_register(2,2)    
    ins.write_register(4096,5)
    ins.write_register(2,1)    
    print (buttonemergent.value,'valeur bouton au')
    print(ins.read_register(4096),"valeur du param 4096")
    print(ins.read_register(4097),"valeur du param 4097")
    while (buttonemergent.value==1):
        print ("Arret d'urgence en cours")

    #à la fin de l'au, coupe toutes les led
    for i in range(len(moteurs)):
        ledmot[i].off()
        #relaymot[i].off()

    nmot = None #efface le numéro du moteur courant
    print ("FIN d'arret d'urgence")

def reverse(): #gère le changement de sens du var
    print ("passe en fonction dinversion")
    if nmot == 0:
        ins.write_register(2,2)
        ins.write_register(4096,5)
        if ins.read_register(80) ==1 :#si le bouton déclencehe la marche avant, on le pase en arrière
            ins.write_register(80,2)
            print ("passe en sens reverse",ins.read_register(80))
            ##ledreverse.on
        elif ins.read_register(80) == 2: #si le bouton délcanche marche arrière on le passe en avant
            ins.write_register(80,1)
            #ledreverse.off
            print ("passe en fonction reverse",ins.read_register(80))
        ins.write_register(2,1)
        ledreverse.toggle()
    
while True:
    button0.when_pressed = demarre
    button1.when_pressed = demarre
    button2.when_pressed = demarre
 #   buttonshutdown.when_pressed = stoppy
    buttonemergent.when_pressed = emergencystop
    buttonreverse.when_pressed = reverse
    
pause()
