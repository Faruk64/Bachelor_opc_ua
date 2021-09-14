from rpi_ws281x import *

class LedStripeTemp():
	
	def __init__(
					self,LedCnt, LedPin, TempMin, TempMax, LedFrq=800000, LedDma=10,
					LedBri=255, LedInv=False, LedCha=0):
		
		self.LedCnt = LedCnt
		self.LedPin = LedPin
		self.LedFrq = LedFrq
		self.LedDma = LedDma
		self.LedBri = LedBri
		self.LedInv = LedInv
		self.LedCha = LedCha
		
		self.TempMin = TempMin # Temperatur Minimum
		self.TempMax = TempMax # Temperatur Maximum
		self.TempDelta = TempMax - TempMin # Temperatur Bereich Delta
		
		self.strip = PixelStrip(LedCnt, LedPin, LedFrq, LedDma, LedInv, LedBri, LedCha) # strip Objekt erstellt
		
		self.strip.begin() # Anfangsinitialisierung
		
	def Temp(self, Temp):
		
		G_Wert = 255 - int((Temp - self.TempMin) * (255 / self.TempDelta)) # Berechne Grün Wert anhand eingegebener Temperatur
		
		for i in range(self.LedCnt): # Wiederhole so oft wie Anzahl der LEDs
			self.strip.setPixelColorRGB(i, 255, G_Wert, 0) # Stelle berechneten Wert ein
		
		self.strip.show() # Übergebe Werte aller LEDs an den Lichtstreifen