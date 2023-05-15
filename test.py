import importlib, os, subprocess, sys, time

libs=["panda3d","pyttsx3","accessible_output2"]

for lib in libs:
	try:
		print(f"Importing module {lib}")
		importlib.import_module(lib)
		
		
		print(f"Module {lib} imported successfully.")
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
			
		
	

print("All required libraries imported successfully.")

from vocaliser import *
from direct.interval.LerpInterval import LerpPosInterval
from panda3d.core import Point3
from direct.task import Task
from panda3d.core import NodePath, Vec3
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from panda3d.core import load_prc_file_data
from direct.showbase.Audio3DManager import Audio3DManager
from direct.interval.IntervalGlobal import *
from panda3d.core import AudioManager
from random import randrange

class Game(ShowBase):
	def __init__(self):
		#preparation of the main window
		wp=WindowProperties()
		
		#loading all the display interfaces
		load_prc_file_data("", "load-display p3tinydisplay")
		
		#setting the audio engine
		load_prc_file_data("", "audio-library-name p3openal_audio")
		load_prc_file_data("", "audio-volume-active 1")
		
		#initing the window, created on model determined earlyer.
		ShowBase.__init__(self,wp)  # passer les propriétés de la fenêtre
		
		#locking the mouse as it is a unusefull controll
		self.disableMouse()
		
		#loading controller of the tts
		self.speak=vocaliser()
		
		#loading the audio kernel
		self.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
		
		
		#maping du clavier
		self.keyMap = {
		"quit" : False,
		"left" : False,
		"right" : False,
		"down":False,
		"up":False,
		"baloon" : False,
		"getbirdpos":False,
		"telscore":False,
		"telbaloon":False
		}
		
		self.accept("arrow_right", self.updateKeyMap, ["right", True])
		self.accept("arrow_right-up", self.updateKeyMap, ["right", False])
		self.accept("arrow_left", self.updateKeyMap, ["left", True])
		self.accept("arrow_left-up", self.updateKeyMap, ["left", False])
		self.accept("arrow_up", self.updateKeyMap, ["up", True])
		self.accept("arrow_up-up", self.updateKeyMap, ["up", False])
		self.accept("arrow_down", self.updateKeyMap, ["down", True])
		self.accept("arrow_down-up", self.updateKeyMap, ["down", False])
		self.accept('escape', sys.exit)
		self.accept("space", self.updateKeyMap, ["baloon", True])
		self.accept("space-up", self.updateKeyMap, ["baloon", False])
		self.accept("p",self.updateKeyMap,["getbirdpos",True])
		self.accept("p-up",self.updateKeyMap,["getbirdpos",False])
		self.accept("s",self.updateKeyMap,["telscore",True])
		self.accept("s-up",self.updateKeyMap,["telscore",False])
		self.accept("b",self.updateKeyMap,["telbaloon",True])
		self.accept("b-up",self.updateKeyMap,["telbaloon",False])
		
		#modeling the univers where the bird should fly.
		self.env = self.loader.loadModel("models/environment")
		self.env.reparentTo(self.render)
		self.env.setScale(0.25, 0.25, 0.25)
		self.env.setPos(-10,42,0)
		
		#adding the river in the env
		
		#first pixel of river, totaly on right, the entrence of the river in the map
		self.riverPoint1=NodePath("river_pixel1")
		self.riverPoint1.reparentTo(self.env)
		self.riverPoint1.setPos(10,40,0)
		
		#second point on the river, to feed the stereo, around 5 a bit on the right to link betwin the entrence and the next part.
		self.riverPoint2=NodePath("river_pixel2")
		self.riverPoint2.reparentTo(self.env)
		self.riverPoint2.setPos(6,25,0)
		
		#next point a bit on the left from the center to feed betwin the midle and the end of the river
		self.riverPoint3=NodePath("river_pixel3")
		self.riverPoint3.reparentTo(self.env)
		self.riverPoint3.setPos(-6,40,0)
		
		#last point of the river, totaly on left, a small waterfall
		self.riverPoint4=NodePath("river_pixel4")
		self.riverPoint4.reparentTo(self.env)
		self.riverPoint4.setPos(-15,40,0)
		
		#creating the bird with his coordinates.
		self.bird=NodePath("Bird")
		self.bird.reparentTo(self.env)
		self.bird.setPos(Vec3(-9, 0, 10))
		self.bird_direction="r"
		self.bird_is_eating=False
		self.bird_speed=0.5
		
		#importing the required noises.
		#background noise
		self.embi_sound=self.audio3d.loadSfx('embi.wav')
		self.embi_sound.setLoop(True)
		self.embi_sound.play()
		self.embi_sound.setVolume(0.2)
		
		#sound for the river in the decore
		self.river_sound=self.audio3d.loadSfx('riverright.wav')
		self.river2_sound=self.audio3d.loadSfx('rivermidle.wav')
		self.river3_sound=self.audio3d.loadSfx('rivermidleft.wav')
		self.river4_sound=self.audio3d.loadSfx('riverleft.wav')
		
		#activating the looping mod
		self.river_sound.setLoop(True)
		self.river2_sound.setLoop(True)
		self.river3_sound.setLoop(True)
		self.river4_sound.setLoop(True)
		
		#linking sound ot audio
		self.audio3d.attachSoundToObject(self.river_sound,self.riverPoint1)
		self.audio3d.attachSoundToObject(self.river2_sound,self.riverPoint2)
		self.audio3d.attachSoundToObject(self.river3_sound,self.riverPoint3)
		self.audio3d.attachSoundToObject(self.river4_sound,self.riverPoint4)
		
		#seting volume to evoid smashing the background noise
		self.river_sound.setVolume(0.5)
		self.river2_sound.setVolume(0.8)
		self.river3_sound.setVolume(0.9)
		self.river4_sound.setVolume(0.6)
		self.river_sound.play()
		self.river2_sound.play()
		self.river3_sound.play()
		self.river4_sound.play()
		
		#throwing a seed:
		self.throw_sound=self.audio3d.loadSfx('seed.wav')
		self.superthrow_sound=self.audio3d.loadSfx('superthrow.wav')
		self.superload_sound=self.audio3d.loadSfx('superload.wav')
		
		#bird eat a seed:
		self.catch_sound=self.audio3d.loadSfx('catch.wav')
		self.supercatch_sound=self.audio3d.loadSfx('supercatch.wav')
		
		#throwing the seed in the wrong direction:
		self.miss_sound=self.audio3d.loadSfx('miss.wav')
		self.supermiss_sound=self.audio3d.loadSfx('supermiss.wav')
		self.supermiss_sound.setVolume(20)
		
		#loop of the bird:
		self.bird_sound=self.audio3d.loadSfx('bird.wav')
		self.birdland_sound=self.audio3d.loadSfx('birdland.wav')
		self.birdsleeping_sound=self.audio3d.loadSfx('birdsleeping.wav')
		
		
		#baloon blowing up:
		self.blow_sound=self.audio3d.loadSfx('blowup.wav')
		
		#baloon unflating
		self.unflating_sound=self.audio3d.loadSfx('unflating.wav')
		
		#baloon too much blowed, exploded
		self.explode_sound=self.audio3d.loadSfx('explode.wav')
		
		#touching the plastics bag of baloon to watch how much are inside
		self.baloonbag_sound=self.audio3d.loadSfx('baloonbag.wav')
		
		#game over cinematic
		self.gameover_sound=self.audio3d.loadSfx('gameover.wav')
		self.pgl_sound=self.audio3d.loadSfx('pgl.wav')
		self.pgf_sound=self.audio3d.loadSfx('pgf.wav')
		self.pgb_sound=self.audio3d.loadSfx('pgb.wav')
		self.pgh_sound=self.audio3d.loadSfx('pgh.wav')
		
		
		#placing the player in the midle of the univers.
		self.player=NodePath("player")
		self.player.reparentTo(self.env)
		self.player.setPos(Vec3(0, 0, 0))
		
		#initing the base camera to the players cordinates.
		base.camera.setPos(0, 0, 0)
		base.camera.setHpr(0, 0, 0)
		base.camera.reparentTo(self.player)
		
		#linking sound emited by the player to his cordinates
		self.audio3d.attachSoundToObject(self.throw_sound, self.player)
		self.audio3d.attachSoundToObject(self.baloonbag_sound, self.player)
		self.audio3d.attachSoundToObject(self.superthrow_sound, self.player)
		self.audio3d.attachSoundToObject(self.superload_sound, self.player)
		self.audio3d.attachSoundToObject(self.miss_sound, self.player)
		self.audio3d.attachSoundToObject(self.blow_sound, self.player)
		self.audio3d.attachSoundToObject(self.explode_sound, self.player)
		
		#link noise to the bird
		self.bird_sound.setLoop(True)
		self.birdsleeping_sound.setLoop(True)
		self.audio3d.attachSoundToObject(self.bird_sound, self.bird)
		self.audio3d.attachSoundToObject(self.birdland_sound, self.bird)
		self.audio3d.attachSoundToObject(self.catch_sound, self.bird)
		self.audio3d.attachSoundToObject(self.supercatch_sound, self.bird)
		self.audio3d.attachSoundToObject(self.birdsleeping_sound, self.bird)
		
		#modeling a baloon to push the bird up
		self.baloon=NodePath("baloon")
		self.baloon.reparentTo(self.env)
		self.baloon.setPos(Vec3(0, 0, 0))
		
		#percentage of allready unflated
		self.baloon_unflated=0
		
		#say if the baloon is unflating actualy or staying at a fixe condition
		self.baloon_unflating=False
		
		#represent the action to put the baloon in the mouth of the player to blow inside
		self.baloon_in_mouth=False
		
		#say if the baloon is blowing his air, flying up.
		self.baloon_flying=False
		
		#determine if the baloon is spawned or not
		self.baloon_spawned=True
		
		#determine the speed of the baloon
		self.baloon_speed=0.3
		
		#determine how much baloon the player got in his bag when he haven't any more he can't push the bird up
		self.baloon_bag=10
		
		#linking the sound of the unflating baloon to his coordinate
		self.audio3d.attachSoundToObject(self.unflating_sound, self.baloon)
		
		#loading the tasks
		self.taskMgr.doMethodLater(1,self.move_bird, "movebird")
		self.bird_sound.play()
		
		
		#basic variables of the games like game over, score, status of the superseed...
		self.score=0
		self.overcopter=None
		
		self.superseed=None
		self.superseed_fase=0
		self.superseed_armed=False
		self.superseed_used=False
	
	
	def gameover(self,task):
		first=Point3(10,-10,20)
		next=Point3(10,10,18)
		last=Point3(-10,10,16)
		diagonale=Point3(6,-7,10)
		waydown=Point3(-5,5,6)
		land=Point3(0,3,0)
		if(self.overcopter==None):
			self.bird_sound.stop()
			self.speak.output("appearing")
			self.overcopter=NodePath("overcoper")
			self.overcopter.reparentTo(self.env)
			self.overcopter.setPos(-10,-10,20)
			self.overcopter_step=0
			self.audio3d.attachSoundToObject(self.gameover_sound, self.overcopter)
			
			self.audio3d.attachSoundToObject(self.pgl_sound, self.overcopter)
			self.audio3d.attachSoundToObject(self.pgf_sound, self.overcopter)
			
			self.gameover_sound.play()
			self.birdsleeping_sound.play()
			return task.again
			
		
		#first aproaching
		if(self.overcopter.getX()<=10) and (self.overcopter.getY()==-10) and (self.overcopter_step==0):
			print(str(self.overcopter.getX())+" x "+str(self.overcopter.getY())+" Y ")
			self.overcopter.set_x(self.overcopter,1)
			
			if(self.overcopter.getX()==10) and (self.overcopter.getY()==-10) and (self.overcopter_step==0):
				self.overcopter_step=1
				
			
			return task.again
			
		
		#going in first corner
		if(self.overcopter.getY()<=10) and (self.overcopter.getX()==-10) and (self.overcopter_step==1):
			print(str(self.overcopter.getX())+" x "+str(self.overcopter.getY())+" Y ")
			self.overcopter.set_x(self.overcopter,1)
			if(self.overcopter.getY()==10) and (self.overcopter.getX()==10) and (self.overcopter_step==1):
				self.overcopter_step=2
				
			
			return task.again
			
		
		#last left corner
		if(self.overcopter.getX()>-10) and (self.overcopter.getY()==10) and (self.overcopter_step==2):
			self.speak.output("step 3")
			self.overcopter.set_x(self.overcopter,-1)
			if(self.overcopter.getZ()>16):
				self.overcopter.set_z(self.overcopter,-1)
				
			if(self.overcopter.getX()==-10) and (self.overcopter.getY()==10) and (self.overcopter_step==2):
				self.overcopter_step=3
				
			
			return task.again
			
		
		#aproaching of landing point
		if(self.overcopter.getX()==-10) and (self.overcopter.getY()==10) and (self.overcopter_step==3):
			self.speak.output("step 4")
			self.overcopter.set_x(self.overcopter,1)
			if(self.overcopter.getPos()==first):
				self.overcopter_step=4
				
			
			return task.again
			
		
	
	def move_bird(self,task):
		task.setDelay(1)
		
		if(self.bird_direction=="r"):
			self.bird.set_x(self.bird,self.bird_speed)
		if(self.bird_direction=="l"):
			self.bird.set_x(self.bird,-self.bird_speed)
			
		
		if(self.bird.getX()>10):
			self.birdland_sound.play()
			self.bird.setPos(9,0,self.bird.getZ()-1)
			self.bird_direction="l"
			self.superseed_used=False
		if(self.bird.getX()<-10):
			self.birdland_sound.play()
			self.bird.setPos(-9,0,self.bird.getZ()-1)
			self.bird_direction="r"
			self.superseed_used=False
			
		if(self.superseed!=None) and (self.bird.getX()>=-5) and (self.bird.getX()<=5):
			if(self.bird.getZ()<=self.superseed.getZ()) or (self.bird.getZ()-5<=self.superseed.getZ()) or (self.bird.getZ()+5<=self.superseed.getZ()):
				self.supercatch_sound.play()
				
			
		
		if(int(self.bird.getZ())<=0):
			self.speak.output("game over.")
			self.taskMgr.add(self.gameover,"overing")
			return task.exit
			
		return task.again
	
	#unflationing the baloon if the space key is pressed
	def unflatebaloon(self,task):
		if(self.baloon_in_mouth==True) and (self.baloon_unflating==False) and (self.baloon_unflated>=0) and (self.baloon_unflated<100) and (self.baloon_spawned==True):
			self.baloon_unflating=True
			if(self.baloon_unflated>0):
				self.blow_sound.setPlayRate(1.0/(1.0+1.000001*(self.baloon_unflated/100.0)))
				
			self.blow_sound.play()
			waitTime=self.blow_sound.length()+(self.baloon_unflated/100)
			task.setDelay(waitTime)
			task.pause(waitTime)
			self.baloon_unflated+=randrange(10,25)
			
			self.baloon_unflating=False
			return task.again
			
		
		if(self.baloon_in_mouth==True) and (self.baloon_unflating==False) and (self.baloon_unflated>100) and (self.baloon_spawned==True):
			self.blow_sound.stop()
			self.blow_sound.setPlayRate(1)
			self.explode_sound.play()
			self.baloon_unflated=0
			self.baloon_in_mouth=False
			self.baloon_unflating=False
			self.baloon_flying=False
			self.baloon_spawned=False
			self.baloon_bag-=1
			task.pause(3)
			self.baloon_spawned=True
			return task.done
			
		
	
	def flybaloon(self,task):
		if(self.baloon_in_mouth==False) and (self.baloon_unflating==False) and (self.baloon_unflated>0) and (self.baloon_flying==False):
			self.baloon_bag-=1
			self.speak.output("lift off")
			self.baloon_spawned=False
			self.blow_sound.stop()
			self.blow_sound.setPlayRate(1)
			self.baloon_flying=True
			self.unflating_sound.play()
			return task.cont
			
		
		if(self.baloon_flying==True) and (self.baloon_unflated>0):
			self.baloon.set_z(self.baloon,1)
			if(self.baloon.getX()==self.bird.getX()) and (self.baloon.getZ()==self.bird.getZ()):
				self.speak.output("bump! the balloon push the bird up!")
				self.bird.setZ(self.bird,+1)
				
			self.baloon_unflated-=1
			return task.again
			
		
		if(self.baloon_unflated<=0) and (self.baloon_flying==True):
			self.speak.output("Flap! The balloon fall back in the graces!")
			self.baloon_flying=False
			self.unflating_sound.stop()
			self.baloon.setPos(0,0,0)
			task.pause(3)
			self.baloon_spawned=True
			return task.done
			
		
	
	def flysuperseed(self,task):
		#task.setDelay(1)
		if(self.superseed.getZ()<=15) and (self.superseed_fase==1):
			print("climbing up is at "+str(self.superseed.getZ()))
			self.superseed.setZ(self.superseed,+0.5)
			return task.again
		elif(self.superseed.getZ()>=15) and (self.superseed_fase==1):
			print("geting in fase 2")
			self.superseed_fase=2
			return task.again
		
		if(self.superseed.getZ()==15) or (self.superseed.getZ()>0) and (self.superseed_fase==2):
			print("falling down is at "+str(self.superseed.getZ()))
			self.superseed.setZ(self.superseed,-0.5)
			return task.again
		elif(self.superseed.getZ()==0) and (self.superseed_fase==2):
			print("geting in fase 3")
			self.superseed_fase=3
			return task.again
			
		
		if(self.superseed.getZ()==0) and (self.superseed_fase==3):
			self.speak.output("The hevy seed sadly fall back on the ground, bounsing back away... well done, nice shot!")
			self.superseed.setZ(self.superseed,1)
			self.superseed_fase=4
			return task.again
		
		if(self.superseed.getY()<self.riverPoint2.getY()) and (self.superseed_fase==4):
			self.superseed.setY(self.superseed,1)
			print("flying to the river, is actually at "+str(self.superseed.getY()))
			return task.again
		elif(self.superseed.getY()==self.riverPoint2.getY()) and (self.superseed_fase==4):
			print("ready to fall in river")
			self.superseed_fase=5
			return task.again
			
		
		if(self.superseed_fase==5):
			print("super seed falled in watter")
			self.supermiss_sound.play()
			task.pause(self.supermiss_sound.length())
			self.superseed=None
			self.superseed_fase=0
			
			return task.exit
			
		
	
	def eat_seed(self,task):
		if(self.bird_is_eating==False):
			self.bird_is_eating=True
			self.catch_sound.play()
			self.score+=1
			task.setDelay(self.catch_sound.length())
			#self.taskMgr.doMethodLater(self.catch_sound.length(),self.eat_seed,"haveyoufinish")
			return Task.again
		else:
			self.bird_is_eating=False
			return task.done
		
	
	def throw_seed(self,direction):
		self.throw_sound.play()
		if(not self.bird_is_eating):
			if(direction=="l") and (self.bird_direction=="r") or (direction=="r") and (self.bird_direction=="l"):
				self.taskMgr.doMethodLater(0,self.eat_seed,"eating")
			else:
				self.miss_sound.play()
				
			
		else:
			self.miss_sound.play()
			
		
	
	def updateKeyMap(self, controlName, controlState):
		self.keyMap[controlName] = controlState
		
		if(self.keyMap["right"]==True) and (self.overcopter==None):
			self.throw_seed("r")
		if(self.keyMap["left"]==True) and (self.overcopter==None):
			self.throw_seed("l")
			
		if(self.keyMap["getbirdpos"]==True):
			self.speak.output("The bird is actualy at : "+str(self.bird.getX())+", "+str(self.bird.getZ()))
			
		if(self.keyMap["telscore"]==True):
			self.speak.output("Your score is : "+str(self.score)+" points")
			
		if(self.keyMap["baloon"]==True) and (self.baloon_in_mouth==False) and (self.baloon_unflating==False) and (self.overcopter==None) and (self.baloon_bag>0):
			self.baloon_in_mouth=True
			self.taskMgr.add(self.unflatebaloon, "baloon_unflatingtsk")
		if(self.keyMap["baloon"]==False) and (self.overcopter==None):
			taskMgr.remove("baloon_unflatingtsk")
			self.baloon_in_mouth=False
			if(self.baloon_unflated>0):
				self.taskMgr.add(self.flybaloon,"flying")
				
			
		if(self.keyMap["down"]==True) and (self.superseed_armed==False) and (self.overcopter==None) and (self.superseed_used==False):
			self.speak.output("super seed loaded")
			self.superseed_armed=True
			self.superload_sound.play()
			
		if(self.keyMap["up"]==True) and (self.superseed_armed==True) and (self.overcopter==None) and (self.superseed_used==False):
			self.superseed_used=True
			self.superthrow_sound.play()
			self.superseed=NodePath("superseed")
			self.superseed.reparentTo(self.env)
			self.superseed.setPos(0,0,0)
			self.superseed_fase=1
			self.taskMgr.add(self.flysuperseed,"flyseed")
			self.superseed_armed=False
		if(self.keyMap["telbaloon"]==True) and (self.overcopter==None):
			self.baloonbag_sound.play()
			self.speak.output("you have "+str(self.baloon_bag)+" balloons in your bag.")
			
		
	


game = Game()
game.run()