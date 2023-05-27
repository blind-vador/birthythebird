import platform

def detect_platform():
	return platform.system()
	

if(detect_platform()=="Windows"):
	import accessible_output2
else:
	import pyttsx3
	
