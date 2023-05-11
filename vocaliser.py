import platform
if(platform.system() == 'Windows'):
	import accessible_output2.outputs.auto
else:
	import pyttsx3

class vocaliser:
	def __init__(self):
		self.platform=platform.system()
		self.speaker=None
		
		if self.platform == 'Windows':
			self.speaker = accessible_output2.outputs.auto.Auto()
		else:
			self.speaker = pyttsx3.init()
			
		
	
	def output(self, message):
		if(self.platform=='Windows'):
			self.speaker.output(message)
		else:
			self.speaker.say(message)
			self.speaker.runAndWait()
			
		print(message+"sended and read correctly with setting for "+self.platform)
		
	