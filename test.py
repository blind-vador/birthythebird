import accessible_output2.outputs.auto, panda3d, threading, time, sys
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
		self.speak=accessible_output2.outputs.auto.Auto()
		
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
		"telscore":False
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
		
		#modeling the univers where the bird should fly.
		self.env = self.loader.loadModel("models/environment")
		self.env.reparentTo(self.render)
		self.env.setScale(0.25, 0.25, 0.25)
		self.env.setPos(-10,42,0)
		
		#creating the bird with his coordinates.
		self.bird=NodePath("Bird")
		self.bird.reparentTo(self.env)
		self.bird.setPos(Vec3(8, 0, 1))
		self.bird_direction="r"
		self.bird_is_eating=False
		
		#importing the required noises.
		#background noise
		self.embi_sound=self.audio3d.loadSfx('embi.wav')
		self.river_sound=self.audio3d.loadSfx('river.wav')
		self.embi_sound.setLoop(True)
		self.embi_sound.play()
		self.embi_sound.setVolume(0.2)
		self.river_sound.setLoop(True)
		self.river_sound.setVolume(0.1)
		self.river_sound.play()
		
		#throwing a seed:
		self.throw_sound=self.audio3d.loadSfx('seed.wav')
		self.superthrow_sound=self.audio3d.loadSfx('superseedthrow.wav')
		self.superload_sound=self.audio3d.loadSfx('superseedload.wav')
		
		#bird eat a seed:
		self.catch_sound=self.audio3d.loadSfx('catch.wav')
		self.supercatch_sound=self.audio3d.loadSfx('superseedcatch.wav')
		
		#throwing the seed in the wrong direction:
		self.miss_sound=self.audio3d.loadSfx('miss.wav')
		self.supermiss_sound=self.audio3d.loadSfx('superseedmiss.wav')
		
		#loop of the bird:
		self.bird_sound=self.audio3d.loadSfx('bird.wav')
		self.birdland_sound=self.audio3d.loadSfx('birdland.wav')
		
		#baloon blowing up:
		self.blow_sound=self.audio3d.loadSfx('blowup.wav')
		
		#baloon unflating
		self.unflating_sound=self.audio3d.loadSfx('unflating.wav')
		
		#baloon too much blowed, exploded
		self.explode_sound=self.audio3d.loadSfx('explode.wav')
		
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
		#initing the score
		self.score=0
		
		#linking sound emited by the player to his cordinates
		self.audio3d.attachSoundToObject(self.throw_sound, self.player)
		self.audio3d.attachSoundToObject(self.superthrow_sound, self.player)
		self.audio3d.attachSoundToObject(self.superload_sound, self.player)
		self.audio3d.attachSoundToObject(self.miss_sound, self.player)
		self.audio3d.attachSoundToObject(self.blow_sound, self.player)
		self.audio3d.attachSoundToObject(self.explode_sound, self.player)
		
		#link noise to the bird
		self.bird_sound.setLoop(True)
		self.audio3d.attachSoundToObject(self.bird_sound, self.bird)
		self.audio3d.attachSoundToObject(self.birdland_sound, self.bird)
		self.audio3d.attachSoundToObject(self.catch_sound, self.bird)
		self.audio3d.attachSoundToObject(self.supercatch_sound, self.bird)
		
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
		self.baloon_speed=1
		
		#linking the sound of the unflating baloon to his coordinate
		self.audio3d.attachSoundToObject(self.unflating_sound, self.baloon)
		
		#loading the tasks
		self.taskMgr.doMethodLater(1,self.move_bird, "movebird")
		self.bird_sound.play()
		
		self.overcopter=None
		self.superseed_armed=False
	
	def gameover(self,task):
		first=Point3(10,-10,20)
		next=Point3(10,10,18)
		last=Point3(-10,10,16)
		diagonale=Point3(6,-7,10)
		waydown=Point3(-5,5,6)
		land=Point3(0,3,0)
		if(self.overcopter==None):
			self.speak.output("appearing")
			self.overcopter=NodePath("overcoper")
			self.overcopter.reparentTo(self.env)
			self.overcopter.setPos(-10,-10,20)
			self.overcopter_step=0
			self.audio3d.attachSoundToObject(self.gameover_sound, self.overcopter)
			
			self.audio3d.attachSoundToObject(self.pgl_sound, self.overcopter)
			self.audio3d.attachSoundToObject(self.pgf_sound, self.overcopter)
			
			self.gameover_sound.play()
			return task.cont
			
		
		#first aproaching
		while(self.overcopter.getX()<10) and (self.overcopter.getY()==-10) and (self.overcopter_step==0):
			self.speak.output("step 1")
			self.overcopter.set_x(self.overcopter,0.1)
			
		if(self.overcopter.getX()==10) and (self.overcopter.getY()==-10) and (self.overcopter_step==0):
			self.overcopter_step=1
			return task.again
			
		
		#going in first corner
		while(self.overcopter.getY()<10) and (self.overcopter.getX()==-10) and (self.overcopter_step==1):
			self.speak.output("step 2")
			self.overcopter.set_x(self.overcopter,1)
			
		if(self.overcopter.getY()==10) and (self.overcopter.getX()==-10) and (self.overcopter_step==1):
			self.overcopter_step=2
			return task.again
			
		
		#last left corner
		while(self.overcopter.getX()>-10) and (self.overcopter.getY()==10) and (self.overcopter_step==2):
			self.speak.output("step 3")
			self.overcopter.set_x(self.overcopter,-1)
			if(self.overcopter.getZ()>16):
				self.overcopter.set_z(self.overcopter,-1)
				
			
		if(self.overcopter.getX()==-10) and (self.overcopter.getY()==10) and (self.overcopter_step==2):
			self.overcopter_step=3
			return task.again
			
		
		#aproaching of landing point
		if(self.overcopter.getX()==10) and (self.overcopter.getY()==10) and (self.overcopter_step==3):
			self.speak.output("step 4")
			self.overcopter.set_x(self.overcopter,1)
			task.pause(1)
			return task.again
			
		
		if(self.overcopter.getPos()==first):
			self.overcopter_step=1
			return task.again
		elif(self.overcopter.getPos()==next):
			self.overcopter_step=2
			return task.again
			
		
	
	def move_bird(self,task):
		if(self.bird_direction=="r"):
			self.bird.set_x(self.bird,1)
		if(self.bird_direction=="l"):
			self.bird.set_x(self.bird,-1)
			
		
		if(self.bird.getX()>10):
			self.birdland_sound.play()
			self.bird.setPos(9,0,self.bird.getZ()-1)
			self.bird_direction="l"
		if(self.bird.getX()<-10):
			self.birdland_sound.play()
			self.bird.setPos(-9,0,self.bird.getZ()-1)
			self.bird_direction="r"
			
		
		if(int(self.bird.getZ())<=0):
			self.speak.output("game over.")
			self.taskMgr.add(self.gameover,"overing")
			return task.done
			
		return Task.again
		
	
	#unflationing the baloon if the space key is pressed
	def unflatebaloon(self,task):
		if(self.baloon_in_mouth==True) and (self.baloon_unflating==False) and (self.baloon_unflated>=0) and (self.baloon_unflated<100) and (self.baloon_spawned==True):
			self.baloon_unflating=True
			if(self.baloon_unflated>0):
				self.blow_sound.setPlayRate(1.0/(1.0+1.000001*(self.baloon_unflated/100.0)))
				
			self.blow_sound.play()
			waitTime=self.blow_sound.length()+(self.baloon_unflated/100)
			self.taskMgr.doMethodLater(waitTime,self.unflatebaloon,"blowagain")
			task.pause(waitTime)
			self.baloon_unflated+=randrange(10,25)
			
			self.baloon_unflating=False
			return task.done
			
		
		if(self.baloon_in_mouth==True) and (self.baloon_unflating==False) and (self.baloon_unflated>100) and (self.baloon_spawned==True):
			self.blow_sound.stop()
			self.explode_sound.play()
			self.baloon_unflated=0
			self.baloon_in_mouth=False
			self.baloon_unflating=False
			self.baloon_flying=False
			self.baloon_spawned=False
			task.pause(3)
			self.baloon_spawned=True
			return task.exit
			
		
		if(self.baloon_in_mouth==False):
			self.blow_sound.stop()
			return task.done
			
		
	
	def flybaloon(self,task):
		if(self.baloon_in_mouth==False) and (self.baloon_unflating==False) and (self.baloon_unflated>0) and (self.baloon_flying==False):
			self.speak.output("lift off")
			self.baloon_spawned=False
			self.blow_sound.stop()
			self.baloon_flying=True
			self.unflating_sound.play()
			self.taskMgr.doMethodLater(0,self.flybaloon,"flying")
			return task.done
			
		
		if(self.baloon_flying==True) and (self.baloon_unflated>0):
			self.speak.output("the rocket is on his way")
			self.baloon.set_z(self.baloon,1)
			self.baloon_unflated-=1
			return task.again
			
		
		if(self.baloon_unflated<=0) and (self.baloon_flying==True):
			self.speak.output("flight ending normally.")
			self.baloon_flying=False
			self.unflating_sound.stop()
			self.baloon.setPos(0,0,0)
			task.pause(3)
			self.baloon_spawned=True
			return task.done
			
		
	
	def eat_seed(self,task):
		if(self.bird_is_eating==False):
			self.bird_is_eating=True
			self.catch_sound.play()
			self.score+=1
			self.taskMgr.doMethodLater(self.catch_sound.length(),self.eat_seed,"haveyoufinish")
			return Task.done
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
			
		
	
	def blowing(self):
		self.baloon_unflated=self.baloon_unflated+1
		if(self.baloon_unflated>100):
			self.explode_sound.play()
			self.baloon_unflated=0
			
		
	
	def releazbaloon(self):
		flightduration=2*(self.baloon_unflated/100)**2
		elapsed_time=globalClock.getFrameTime() - self.start_time
		self.unflating_sound.play()
		if(elapsed_time<time_of_flight):
			self.baloon.setPos(self.baloon.getX(), self.baloon.getY(), self.baloon.getZ()+1)
			return Task.again
		else:
			self.deflating_sound.stop()
			self.baloon_unflated=0
			return Task.done
			
		
	
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
			
		if(self.keyMap["baloon"]==True) and (self.baloon_in_mouth==False) and (self.baloon_unflating==False) and (self.overcopter==None):
			self.baloon_in_mouth=True
			self.taskMgr.add(self.unflatebaloon, "baloon_unflatingtsk")
		if(self.keyMap["baloon"]==False) and (self.overcopter==None):
			taskMgr.remove("baloon_unflatingtsk")
			self.baloon_in_mouth=False
			if(self.baloon_unflated>0):
				self.taskMgr.add(self.flybaloon,"flying")
				
			
		if(self.keyMap["down"]==True) and (self.superseed_armed==False) and (self.overcopter==None):
			self.speak.output("super seed loaded")
			self.superseed_armed=True
			self.superload_sound.play()
			
		
	


game = Game()
game.run()