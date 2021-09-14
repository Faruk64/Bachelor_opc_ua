import PCF8591

class readAdc:
	def __init__(self, Channel, i2cAddress):
		self.Channel = Channel
		self.i2cAddress = i2cAddress
		self.adc = PCF8591
	def read(self):
		self.adc.readADCvalue(self.i2cAddress, self.Channel)
		return self.adc.readADCvalue(self.i2cAddress, self.Channel)
	def readMW(self):
		self.adc.readADCvalue(self.i2cAddress, self.Channel)
		val1 = self.adc.readADCvalue(self.i2cAddress, self.Channel)
		val2 = self.adc.readADCvalue(self.i2cAddress, self.Channel)
		val3 = self.adc.readADCvalue(self.i2cAddress, self.Channel)
		val = int(round((val1 + val2 + val3)/3, 0))
		return val