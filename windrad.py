from RPi import GPIO
from time import sleep

class Windrad:
	def __init__(self, Pin, maxDC, level):
		self.Pin = Pin		# Pin an welchem Windrad ist
		self.maxDC = maxDC	# maximaler DutyCycle Windrad
		self.level = level	# Anzahl Stufen
		GPIO.setmode(GPIO.BCM) # Pin bezeichnen mit GPIO-Nr.
		GPIO.setup(Pin, GPIO.OUT)	# Pin als Output
		self.pwm = GPIO.PWM(Pin, 100)	# PWM definiert mit 100Hz
		self.start0 = 1	# Variablen der Klasse
		
	def start(self):
		self.pwm.start(0)	# PWM mit DutyCycle = 0 starten
		
	def out(self, i_lvl):
		if i_lvl > self.level:
			i_lvl = self.level
        elif i_lvl < 1:
            i_lvl = 1
		pwm = self.pwm # In anderere Variable speichern damit kürzer
		
		if self.start0 == 1 and i_lvl != 1: # Erfolgt Start von 0 aus?
			pwm.ChangeDutyCycle(80) #Starthilfe
			sleep(0.1) # von 0,3 Sekunden
		
		if i_lvl == 1: # Ist die Stufe 0?
			dc = 0	# Stufe 1 = stehen		
			self.start0 = 1 # Flag ob vorheriger Status = 0
        else:
            dc = self.maxDC/(self.level-1)*(i_lvl-1)	#DutyCycle je nach Anzahl von Stufen berechnen
            self.start0 = 0 # Kein Start von 0
            if dc < 7:	# dc darf nicht kleiner als 7 sein, da Windrad sonst steht // Frequenz 100 // 5 Volt
                dc = 7
		pwm.ChangeDutyCycle(dc) # Ermittelten dc übertragen
	def stop(self):
		self.pwm.stop()