from src.platform_kernel import *

class vocaliser:
	def __init__(self):
		self.speaker=None
		
		if(detect_platform()=='Windows'):
			self.speaker=accessible_output2.outputs.auto.Auto()
		else:
			self.speaker=pyttsx3.init()
			
		
	
	def output(self, message):
		if(detect_platform()=='Windows'):
			self.speaker.output(message)
		else:
			self.speaker.say(message)
			self.speaker.runAndWait()
			
		print("string saying: "+message+" receved and spoken correctly with setting for "+detect_platform())
		
	
