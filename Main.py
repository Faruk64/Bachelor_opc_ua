from LedStripe import *
from windrad import *
from readAdc import *

def getSolarLvl(adcVal): # Solar in Stufen einteilen
	if adcVal<35: # Stufe 1
		lvl = 1
	elif ((adcVal>=35)and(adcVal<38)): #Stufe 2
		lvl = 2
	elif ((adcVal>=38)and(adcVal<41)): #Stufe 3
		lvl = 3
	elif ((adcVal>=41)and(adcVal<45)): #Stufe 4
		lvl = 4
	elif adcVal>=45: #Stufe 5
		lvl = 5
    else:
        lvl = 1
	return lvl #Stufe ausgeben

# Erstellung der Objekte
Poti = readAdc(0x40, 0x48) # Poti Kanal 0x40 I2C 0x48
Solar = readAdc(0x42, 0x48) # Solar Kanal 0x42 I2C 0x48
Led = LedStripeTemp(18, 18, 0, 255) # Anz 18 Pin 18 TempMin 0 TempMax 255
WRad = Windrad(12, 30, 5) # Pin 12 MaxDC 30 LvL 5

try:
	WRad.start() #Windrad starten
	while True:
		Led.Temp(Poti.read())
		WRad.out(getSolarLvl(Solar.readMW()))
        
except KeyboardInterrupt:
	print("\n")
	WRad.stop()
	WRad.clear(12)
	print("Windrad Stop und GPIO clear")