#!python3.7

from scene import *
import sound
import random
import math
A = Action
import ui
import time
import console
from PIL import Image as PILImage


class Solavou_Lives (SpriteNode):
	# Maintain player number of lives
	# Add Solavou Lives graphic
	def __init__(self,**kwargs):
		img= Texture(ui.Image.named('spc:PlayerLife1Red'))
		SpriteNode.__init__(self,img,**kwargs)
		
class Solavou (SpriteNode):
	# Main player
	def __init__(self, **kwargs):
		img = Texture(ui.Image.named('images/IMG_0284.PNG'))
		SpriteNode.__init__(self, img, **kwargs)
		self.destroyed = False

class FlyingBoss (SpriteNode):
	# Multiple groups of enemies. Each group different path. slight variations with each group
	def __init__(self, **kwargs):
		img = Texture(ui.Image.named('images/IMG_0304.PNG'))
		SpriteNode.__init__(self, img, **kwargs)
		self.destroyed = False

	def launch_attack(self):
		self.laser=SpriteNode(Texture(ui. Image.named('images/IMG_0286.PNG')))
		self.add_child(self.laser)
		actions = [Action.move_by(0, -self.size.h, 1.2 * self.speed), Action.remove()]
		self.laser.run_action(Action.sequence(actions))

class FlyingSaucer (SpriteNode):
	# Multiple groups of enemies. Each group different path. slight variations with each group

	def __init__(self, **kwargs):
		# image is 8 sep images of a flying saucer, horizontal on outside and vert in 5th position
		seq=[]
		img = Texture(ui.Image.named('images/IMG_0312.PNG')).subtexture((0,0,0.125,1))
		SpriteNode.__init__(self, img, **kwargs)
		self.destroyed = False
	def move_saucer(self,sender,idx):
		seq=[]
		for x in range(0, random.randint(180,250), 6):
			new_action= Action.move_to(math.sin(x/57)*300, 800-3*x)
			seq.append(new_action)
		seq.append(Action.remove())
		sender.items[idx].run_action(Action.sequence(seq))
		
class MyScene (Scene):
	def setup(self):
		self.scrolling=False
		# First add background
		#BG Image IMG_0278.PNG=(1024.00, 2900.00); iPhone Xr=(375.0 812.0)
		self.sprite = SpriteNode(Texture(ui.Image.named('images/IMG_0278.PNG')),position=(0,0), anchor_point = (0.5,0.0),scale=1.6,speed=0.5)
		self.add_child(self.sprite)
		self.speed = 1
		self.lasers=[]
		self.bombs=[]		
		self.game_over = True

		self.started=False
		self.explosion_index=0
		self.solavou_lives=3
		self.lives=[]
		self.items=[]
		self.spawned = False
		
		self.score = 0
		
		# Add Lives bottom left screen
		for i in range(0,3):
			self.lives.append (Solavou_Lives(position=(30+30*i, 30),parent=self, scale = 0.8))

		#add title
		self.xevious = SpriteNode(Texture(ui.Image.named('images/IMG_0279.PNG')),position=(self.size.w/2,self.size.h/2),x_scale=0.3,y_scale= 0.3)
		self.add_child(self.xevious)
		
		# Add Solavou 
		self.solavou= Solavou(position=(self.size.w/2,self.size.h/2-50),scale=1,anchor_point=(0.5,0.02),speed=3.2,blend_mode=BLEND_NORMAL)
		self.add_child(self.solavou)

		# Add "Insert Coins"
		self.insertcoins = LabelNode('INSERT COINS', position=(self.size.w/2, self.size.h/2-80), font = ('Copperplate',24))
		self.add_child(self.insertcoins)
		
		# Add "Namco"
		self.namco = LabelNode('\u00a9'+'   1982 NAMCO LTD.', position=(self.size.w/2, self.size.h/2-120), font = ('Copperplate',24))
		self.add_child(self.namco)
		
		# Add "P right"		
		self.pright = LabelNode('\u2117', position=(self.size.w/2-102, self.size.h/2-122), font = ('Copperplate',18))
		self.add_child(self.pright)
		
		# Add "Player Up"		
		self.playerup = LabelNode('1 UP', position=(40, self.size.h-30), font = ('Copperplate', 20))
		self.add_child(self.playerup)
		
		#add score label
		self.score_label = LabelNode('0', position=(40, self.size.h-50),font = ('Copperplate', 20))		
		self.add_child(self.score_label)		
		
		# Add "Highscore"		
		self.highscore = LabelNode('HIGH SCORE', position=(self.size.w/2, self.size.h-40), font = ('Copperplate', 20))
		self.add_child(self.highscore)		
		
		# Add bomb: change similar to laser?
		self.bomby=SpriteNode(Texture(ui. Image.named('shp:sparkle')), position=(self.size.w/2,self.size.h/2-50),scale=0.5)
		
		# Add bomb end position Cross
		self.bomb_target= SpriteNode(Texture(ui.Image.named('images/IMG_0285.PNG')), position=(self.size.w/2,self.size.h/2-50),scale=1)
		
	def did_change_size(self):
		pass
		
	def stop(self):
		sound.stop_all_effects()
	
	def update(self):
		if self.game_over:
			return
#		self.update_player()
		self.check_item_collisions()
		self.check_laser_collisions()	
		self.check_bomb_collisions()		
		if len(self.items) == 0:
			self.spawned = False	
		if random.random() < 0.008 * self.speed:
			self.spawn_item()
		self.score_label.text = str(self.score)
	
	def touch_began(self, touch):
		self.game_over = False
		# A fix for playing music after theme: insert after fade sequence (6s)
		if (self.started==False):
			self.xevious.run_action(Action.sequence( [Action.fade_to(0,6),Action.call(play_norm)]))
			self.started=True
		self.insertcoins.run_action(Action.fade_to(0,3))		
		self.namco.run_action(Action.fade_to(0,3))
		self.pright.run_action(Action.fade_to(0,3))

		if self.scrolling == False:
			# Play theme. move later?
			sound.play_effect('music/xeviousTheme.caf')
			self.scroll_background()
		if touch.location[1] >= self.size.h/4:
			self.shoot_laser()
		else:
			self.shoot_bomb()
		
	def touch_moved(self, touch):
		if self.solavou.destroyed==True:
			return 
		#calculate solavu move based on touch
		init_position= touch.prev_location
		new_position=touch.location
		delta_position=(new_position-init_position)
		self.solavou.run_action(Action.move_by(delta_position[0],delta_position[1],0.0))
	
	def touch_ended(self, touch):
		pass
		# test enemy.boss attack
#		self.boss.launch_attack()

	def spawn_item(self):
		if self.spawned == True:
			return 
			
		# empty items
		self.items=[]

		if random.random() < 0.6 * self.speed:
			self.spawned = True
			for i in range(0,5):
				saucer_temp= FlyingSaucer(position=(-10, self.size.h -12),parent=self, scale = 1.5,speed= 8-i)
				self.items.append(saucer_temp)
				self.items[i].destroyed = False
				self.items[i].move_saucer(self,i)
				
#				self.spawned = False			
		else:
#			self.spawned = False			
			pass
			
	def check_bomb_collisions(self):
		for bomb in list(self.bombs):
			if not bomb.parent:
				self.bombs.remove(bomb)
				continue	
				
	def check_laser_collisions(self):
		''' Method to monitor Solavou lasers to destroy saucers, etc, remove objects and lasers, make sounds.
		'''
		for laser in list(self.lasers):
			# Remove lasers gone off screen
			if not laser.parent:
				self.lasers.remove(laser)
				continue
			for item in self.items:
				# if item is not saucer...
				if not isinstance(item, FlyingSaucer):					
					print(',',end='')
					continue
				#...or its any destroyed object...
				if item.destroyed:
					continue
				#... or item is of the screen
				if not item.parent:
					self.items.remove(item)
					continue				
				if item.frame.contains_point(laser.position):
					self.lasers.remove(laser)
					laser.remove_from_parent()
					self.destroy_saucer(item)			
					self.items.remove(item)		
					self.score+=30
					break
	def destroy_saucer(sender,item):
		sound.play_effect('arcade:Coin_2')
		item.destroyed=True
		item.remove_from_parent()
	
	def check_item_collisions(self):
		if self.solavou.destroyed == True:
			return
		# define a frame for player. note player is solavou and crosshairs
		player_hitbox = Rect(self.solavou.position.x - 15, self.solavou.position.y-15, 25, 25)

		# Check for overlap (collision)
		for item in list(self.items):
			if item.frame.intersects(player_hitbox):
				self.solavou_hit(self)

	def solavou_hit(self,sender):
		''' This is not working the second time round for some reason. Parent is same, image object, all looks right. maybe Node/action issue
		'''
		self.solavou.destroyed=True		
		sound.play_effect('arcade:Explosion_2')
		actions=[A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.move_by(0,-5),A.call(self.change_image),A.fade_to(0,2),A.wait(2),A.call(self.return_image)]
		self.solavou.run_action(Action.sequence(actions))
		#Actions run in near parallel time so this removes solavou before all explosion pics done.
		self.lives[self.solavou_lives-1].remove_from_parent()
		
		if self.solavou_lives != 0:
			self.solavou_lives-=1
			#re-spawn player
			self.start_over(self)
		else:
			self.game_over_cleanup()
		

	def change_image(self):
		''' built in pics work fine. subtext not working. Why?: The % must have low precedence or?
		'''

		self.solavou.texture= Texture(ui.Image.named('images/IMG_0355.PNG')).subtexture(((0.143*(self.explosion_index%7)),0,0.143,1))
		self.solavou.scale=4.2
		self.solavou.anchor_point=(0.55,0.35)
		self.explosion_index+=1

	def return_image(self):
		self.solavou.texture= Texture(ui.Image.named('images/IMG_0284.PNG'))
		self.solavou.position= (self.size.w/2,self.size.h/2-50)
		self.solavou.scale=1
		self.solavou.anchor_point=(0.5,0.02)
		self.solavou.speed=3.2
		self.solavou.alpha=1
		self.solavou.destroyed=False

	def shoot_laser(self):
		# limit 3 lasers at a Time
		if len(self.lasers) >= 3:
			return
		laser_temp=SpriteNode(Texture(ui. Image.named('images/IMG_0286.PNG')), parent= self)

		laser_temp.position= self.solavou.position+(0,15)
		actions = [Action.move_by(0, self.size.h, 1.2 * self.speed), Action.remove()]

		laser_temp.run_action(A.sequence(actions))

		self.lasers.append(laser_temp)
		sound.play_effect('digital:Laser4')


	def shoot_bomb(self):		
		# limit 1 bomb at a Time
		if len(self.bombs) >= 1:
			return
		self.bomb_target.position= self.solavou.position+(0,195)
		self.add_child(self.bomb_target)
		
		target_action = [Action.move_by(0, -50, 0.5* self.speed), Action.remove()]		
		self.bomb_target.run_action(Action.sequence(target_action))
		
		self.add_child(self.bomby)
		self.bomby.position= self.solavou.position+(0,25)
		
		actions = [Action.move_by(0, 120, 0.5* self.speed), Action.remove()]		
		self.bomby.run_action(Action.sequence(actions))
		self.bombs.append(self.bomby)		
		sound.play_effect('music/bomb.caf')	

	def scroll_background(self):
		# Scroll main background in 4 slices mimicking endless world
		# todo: pause for bosses and loop until dead, etc
		
		self.scrolling=True
		seq=[Action.move_by(0,-3850,20),Action.move_to(-444,0,0),Action.move_by(0,-3830,20),Action.move_to(820,0,0),Action.move_by(0,-3830,20),Action.move_to(445,0,0),Action.move_by(0,-3830,20)]
		self.sprite.run_action(Action.sequence(seq))
		
	def start_over(self1,self):
		''' This is so far doing nothing, last image was a section of explosion from list. Could sub texture be why no see ship again
		
		self.solavou.run_action (Action.fade_to(1,2))
		self.solavou.texture=Texture(ui.Image.named('shp:WhitePuff10'))
#		self.solavou.scale=5

		self.add_child(self.solavou)
#		print('self children:',self.children)
#		print('parent',self.solavou.position)
		
		# below was screwing up change image?!
		
		self.solavou=Solavou(position=(self.size.w/2,self.size.h/2-50),scale=1,anchor_point=(0.5,0.02),speed=3.2,blend_mode=BLEND_NORMAL)
		self.add_child(self.solavou)
		'''
		pass
	def game_over_cleanup(self):
		end_label = LabelNode('Game Over',position=(self.size.w/2-50,self. size.h/2),font=('Marker Felt',29))
		self.add_child(end_label)

def play_theme():
	# Play theme. move later+ constant
	sound.play_effect('music/xeviousTheme.caf')	
def play_norm():
	sound.play_effect('music/normPlay.caf')

if __name__ == '__main__':
	console.clear()
	run(MyScene(), PORTRAIT, show_fps=True)
