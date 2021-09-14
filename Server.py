from opcua_srv import *
from LedStripe import *
from windrad import *
from readAdc import *
import time
from datetime import datetime

def getSolarLvl(adcVal): # Solar in Stufen einteilen
	if adcVal < 35: # Stufe 1
		lvl = 1
	elif ((adcVal >= 35) and (adcVal < 38)): # Stufe 2
		lvl = 2
	elif ((adcVal >= 38) and (adcVal < 41)): # Stufe 3
		lvl = 3
	elif ((adcVal >= 41) and (adcVal < 45)): # Stufe 4
		lvl = 4
	elif adcVal >= 45: # Stufe 5
		lvl = 5
	else:
		lvl = 1
	return lvl # Stufe ausgeben

# Server erstellen und starten
serveropc = ua_server(4840,'','OPC_UA_SERVER','OPC UA SERVER',user="TestUser",pwd ="TestPwd")

# Werte für Poti erstellen
serveropc.registerValue('FlagPoti', False, True)
serveropc.registerValue('realPotiWert', 0)
serveropc.registerValue('PotiWert', 0, True)

# Werte für Solar erstellen
serveropc.registerValue('FlagSolar', False, True)
serveropc.registerValue('realSolarWert', 0)
serveropc.registerValue('SolarWert', 0, True)

# Benötigte Objekte mit Initialisierung erstellen
Poti = readAdc(0x40, 0x48) # Poti Kanal 0x40 I2C 0x48
Solar = readAdc(0x42, 0x48) # Solar Kanal 0x42 I2C 0x48
Led = LedStripeTemp(18, 18, 0, 255) # Anz 18 Pin 18 TempMin 0 TempMax 255
WRad = Windrad(12, 30, 5) # Pin 12 MaxDC 30 LvL 5

time.sleep(0.1) # Warte 0,1 Sek
# Flags initialisieren und übergeben
FlagPoti = True
FlagSolar = True
serveropc.setValue('FlagPoti', datetime.utcnow(), FlagPoti)
serveropc.setValue('FlagSolar', datetime.utcnow(), FlagSolar)

try:
	
	WRad.start() # Motor PWM starten
	while True:
		
		# Teil für Poti
		FlagPoti = serveropc._dicValues.get('FlagPoti').value
		if FlagPoti == True: # Nicht ändern
			realPotiWert = Poti.read()
			PotiWert = realPotiWert
			serveropc.setValue('PotiWert', datetime.utcnow(), PotiWert)
			serveropc.setValue('realPotiWert', datetime.utcnow(), realPotiWert)
		elif FlagPoti == False: # Werte ändern
			realPotiWert = Poti.read()
			serveropc.setValue('realPotiWert', datetime.utcnow(), realPotiWert)
			PotiWert = serveropc._dicValues.get('PotiWert').value
			# Eingabegrenzen
			if PotiWert > 255:
				PotiWert = 255
			elif PotiWert < 0:
				PotiWert = 0
			serveropc.setValue('PotiWert', datetime.utcnow(), PotiWert)
		Led.Temp(PotiWert) # Wert weitergeben
		
		# Teil für Solar
		FlagSolar = serveropc._dicValues.get('FlagSolar').value
		if FlagSolar == True: # Nicht ändern
			realSolarWert = Solar.readMW()
			SolarWert = realSolarWert
			serveropc.setValue('SolarWert', datetime.utcnow(), SolarWert)
			serveropc.setValue('realSolarWert', datetime.utcnow(), realSolarWert)
		elif FlagSolar == False: # Werte ändern
			realSolarWert = Solar.readMW()
			serveropc.setValue('realSolarWert', datetime.utcnow(), realSolarWert)
			SolarWert = serveropc._dicValues.get('SolarWert').value
			#Eingabegrenzen
			if SolarWert > 50:
				SolarWert = 50
			elif SolarWert < 0:
				SolarWert = 0
			serveropc.setValue('SolarWert', datetime.utcnow(), SolarWert)
		WRad.out(getSolarLvl(SolarWert)) # Wert weitergeben

except KeyboardInterrupt:
	print("\n")
	WRad.stop()
	WRad.clear(12)
	print("Windrad Stop und GPIO clear")
	serveropc.shutdown()
	print("ServerShutdown")