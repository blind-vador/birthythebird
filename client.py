import importlib, os, subprocess, sys, time
from src.platform_kernel import *

libs=["panda3d"]

if(detect_platform()=="Windows"):
	libs.append("accessible_output2")
else:
	libs.append("pyttsx3")
	

for lib in libs:
	try:
		print(f"Importing module {lib}")
		if(lib=="accessible_output2"):
			importlib.import_module(lib+".outputs.auto")
		else:
			importlib.import_module(lib)
			
		
		print(f"Module {lib} imported successfully.\n")
		
	except ImportError as e:
		print(f"Missing library: {e.name}. Installing it for you right now...")
		subprocess.check_call(["pip", "install", "--user", e.name])
		importlib.invalidate_caches()
		print("Waiting for library to be installed...")
		for i in range(10):
			try:
				importlib.import_module(e.name)
				break
			except ImportError:
				time.sleep(3)
		else:
			raise Exception("Unable to import library after installation")
			
		
	

from src import Game

game = Game()
game.run()