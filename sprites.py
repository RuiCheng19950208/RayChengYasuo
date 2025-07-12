# Sprites for platform
from Setting import *
import pygame
import random
from os import path
import math

vec=pygame.math.Vector2


class Spritesheet:
    def __init__(self,filename):
        self.spritesheet = pygame.image.load(filename).convert()
    def get_image(self,x,y,w,h):
        image=pygame.Surface((w,h))
        image.blit(self.spritesheet,(0,0),(x,y,w,h))
        # image=pygame.transform.scale(image,(w//2,h//2)) #If you want to resize
        return image




class Player(pygame.sprite.Sprite):
    def __init__(self,game):
        self.game = game


        self.walking=False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.last_update_Q = -Q_cd
        self.last_update_W = -W_cd
        self.last_update_R = -R_cd


        self.Q_timer=0
        self.Q_upgrade=0

        self.R_getwind_timer = 0
        
        # Energy for passive shield
        self.energy = 0
        self.max_energy = 100
        self.last_position = None
        self.distance_traveled = 0


        self.load_images()


        pygame.sprite.Sprite.__init__(self)
        self.image =self.standing_frame[0]

        # self.image.fill(YELLOW)
        self.rect =self.image.get_rect()
        # Start player in the middle of the screen
        self.rect.center = (width/2, height/2)
        self.pos= vec(width/2, height/2)
        self.vel=  vec(0,0)
        self.acc=  vec(0,0)
        self.E_allowed=1

        # self.Q_allowed=10


    def load_images(self):
        self.standing_frame=[self.game.spritesheet.get_image(0,100,50,50)]
        for frame in self.standing_frame:
            frame.set_colorkey(BLACK)

        self.walk_frame_l=[self.game.spritesheet.get_image(0,0,45,50),
                           self.game.spritesheet.get_image(0, 50, 45, 50),
                           self.game.spritesheet.get_image(0, 100, 50, 50),
                           self.game.spritesheet.get_image(0, 50, 45, 50)]

        self.walk_frame_r=[]
        for frame in self.walk_frame_l:
            frame.set_colorkey(BLACK)
            self.walk_frame_r.append(pygame.transform.flip(frame,True,False))

        self.jump_frame=[self.game.spritesheet.get_image(0,150,50,50)]
        for frame in self.jump_frame:
            frame.set_colorkey(BLACK)


    def jump(self):
        self.rect.y +=2
        hits= pygame.sprite.spritecollide(self,self.game.platforms,False)
        self.rect.y -=2
        if hits and not self.jumping:
            self.game.effect_channel.play(self.game.jump_sound)
            self.jumping= True
            self.vel.y=player_jumpvel
    def update(self):
        self.animate()
        self.acc = vec(0, player_gravity)
        now_key = pygame.time.get_ticks()
        keys= pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.jump()
        if keys[pygame.K_DOWN] and self.vel.y<0:
            self.vel.y = 0
        if keys[pygame.K_LEFT]:
            self.acc.x = -player_acc
        if keys[pygame.K_RIGHT]:
            self.acc.x = player_acc
        
        if keys[pygame.K_q]  and self.game.Q_allowed==0:
            # Determine Q direction based on arrow key presses instead of velocity
            q_direction = 0
            
            if keys[pygame.K_RIGHT]:
                q_direction = 1
            elif keys[pygame.K_LEFT]:
                q_direction = -1
            else:
                # Fallback to velocity direction if no arrow keys are pressed
                q_direction = 1 if self.vel.x > 0 else -1
                
            # Create Q effect visual only for regular Q attacks, not tornado
            if self.Q_upgrade < 2:
                QEffect(self.game, self.pos.x, self.pos.y, q_direction, self.rect,False)
                
            if abs(self.vel.x)>=0 and self.Q_upgrade<2:
                self.game.ability_q_channel.play(self.game.Q_sound)
            self.last_update_Q = now_key
            
            if self.Q_upgrade<2:
                # Track if any mob was killed with this Q
                killed_mob = False
                
                for mob in self.game.mobs:
                    # Check all mobs in attack range
                    if q_direction >= 0:  # Attack right
                        if mob.rect.x - self.pos.x<150 and mob.rect.x - self.pos.x>0 and abs(mob.rect.y - self.rect.y)<60:
                            mob.die()
                            self.game.Q_hit.play()
                            killed_mob = True
                    elif q_direction < 0:  # Attack left
                        if mob.rect.x - self.pos.x>-150 and mob.rect.x - self.pos.x<0 and abs(mob.rect.y - self.rect.y)<60:
                            mob.die()
                            self.game.Q_hit.play()
                            killed_mob = True
                
                # Increment Q_upgrade only once if any mob was killed
                if killed_mob:
                    self.Q_upgrade += 1
                    self.Q_timer = self.last_update_Q
                    
                    # Check if we reached max stacks
                    if self.Q_upgrade == 2:
                        self.game.ability_q_channel.play(self.game.Q_getwind)
            else:
                if q_direction > 0:  # Cast wind right
                    Wind(self.game,1)
                    # Use dedicated channel with priority for hasaki sound
                    self.game.hasaki_channel.stop()  # Stop any currently playing sounds on this channel
                    self.game.hasaki_channel.play(self.game.Q_hasaki)
                    self.Q_upgrade = 0
                elif q_direction < 0:  # Cast wind left
                    Wind(self.game, -1)
                    # Use dedicated channel with priority for hasaki sound
                    self.game.hasaki_channel.stop()  # Stop any currently playing sounds on this channel
                    self.game.hasaki_channel.play(self.game.Q_hasaki)
                    self.Q_upgrade = 0








            # self.Q_allowed= self.Q_allowed-1



        if keys[pygame.K_w] and self.game.W_allowed==0:
            Windwall(self.game,150 ,0,0)
            Windwall(self.game, -150 , 0, 0)

            for mob in self.game.mobs:
                if abs(mob.rect.x - self.pos.x)<150 and abs(mob.rect.y - self.pos.y)<150:
                    mob.die()
                    self.game.w_block_channel.play(self.game.W_block)
            self.last_update_W = now_key


            self.game.ability_w_channel.play(self.game.W_sound1)

        if keys[pygame.K_e] and self.vel.y>0 and self.E_allowed>0:
            self.vel.y=-20
            self.E_allowed= self.E_allowed-1
            self.game.ability_e_channel.play(self.game.E_sound)
        if keys[pygame.K_r] and self.game.Fly_timer>0 and self.game.R_allowed==0:
            for mob in self.game.mobs:
                mob.die()
            self.last_update_R = now_key
            self.energy += 50


            self.vel.y = -50
            self.game.ultimate_channel.play(self.game.R_sound1)





        self.acc.x +=self.vel.x * player_friction
        self.vel += self.acc
        if abs(self.vel.x)<0.5:
            self.vel.x=0
        
        # Track last position for calculating distance traveled
        if self.last_position is None:
            self.last_position = self.pos.copy()
        
        # Update position
        self.pos += self.vel+0.5*self.acc
        
        # Calculate distance traveled since last frame
        distance = (self.pos - self.last_position).length()
        self.distance_traveled += distance
        
        
        energy_gain = distance * self.max_energy / PASSIVE_RECHARGE_DISTANCE
        self.energy = min(self.max_energy, self.energy + energy_gain)
        
        # Update last position
        self.last_position = self.pos.copy()

        if self.pos.x> width+ self.rect.w/2:
            self.pos.x=0-self.rect.w/2
        if self.pos.x< 0-self.rect.w/2:
            self.pos.x=width+self.rect.w/2

        self.rect.midbottom =self.pos

    def animate(self):
        now= pygame.time.get_ticks()
        if self.vel.x!=0:
            self.walking=True
        else:
            self.walking= False

        if  self.vel.y!=0:
            self.jumping=True
        else:
            self.jumping= False

        if not self.jumping and not self.walking:
            if now - self.last_update> 200:
                self.last_update = now

                self.current_frame = (1+self.current_frame)%len(self.standing_frame)
                bottom = self.rect.bottom
                self.image= self.standing_frame[self.current_frame]
                self.rect= self.image.get_rect()
                self.rect.bottom=bottom
        elif self.jumping:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (1 + self.current_frame) % len(self.jump_frame)
                bottom = self.rect.bottom
                self.image = self.jump_frame[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        elif self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (1 + self.current_frame) % len(self.walk_frame_l)
                bottom = self.rect.bottom
                if self.vel.x >0:
                    self.image = self.walk_frame_r[self.current_frame]
                else:
                    self.image = self.walk_frame_l[self.current_frame]


                self.rect = self.image.get_rect()
                self.rect.bottom = bottom




class platform(pygame.sprite.Sprite):
    def __init__(self,game,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.game=game
        
        # Get the first platform image
        first_image = self.game.spritesheet.get_image(104,100,64,32)
        first_image.set_colorkey(BLACK)
        
        # Create the second platform by concatenating two of the first image
        second_image = pygame.Surface((128, 32))  # Create a surface twice as wide
        second_image.fill(BLACK)  # Fill with black for transparency
        second_image.blit(first_image, (0, 0))  # Draw first image on left
        second_image.blit(first_image, (64, 0))  # Draw first image on right
        second_image.set_colorkey(BLACK)  # Set transparency
        
        # Choose between the two platform types
        images = [first_image, second_image]
        self.image = random.choice(images)

        # self.image = pygame.Surface((w,h))
        # self.image.fill(GREEN)
        self.rect= self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Mob(pygame.sprite.Sprite):
    def __init__(self,game):
        self.groups =game.all_sprites,game.mobs
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game =game
        self.image =self.game.spritesheet.get_image(50,0,24,20)
        self.image.set_colorkey(BLACK)  # Add this to make the background transparent
        self.rect=self.image.get_rect()
        self.rect.centerx=random.choice([-100,width+100])
        self.vx= random.randrange(3,10)
        if self.rect.centerx> width:
            self.vx *=-1
        self.rect.y =random.randrange(int(height*3/4))
        
        # Set vertical velocity based on spawn position
        # Use a range of values instead of just three options
        if self.rect.y > height/2:
            # Lower half of screen - bias upward movement
            # 70% chance of upward (-5 to -1), 20% chance of neutral, 10% chance of downward (1 to 3)
            rand_val = random.random()
            if rand_val < 0.7:
                self.vy = random.uniform(-3, 0)  # Upward movement
            elif rand_val < 0.9:
                self.vy = 0  # No vertical movement
            else:
                self.vy = random.uniform(0, 3)  # Slight downward movement
        else:
            # Upper half of screen - bias downward movement
            # 70% chance of downward (1 to 5), 20% chance of neutral, 10% chance of upward (-3 to -1)
            rand_val = random.random()
            if rand_val < 0.7:
                self.vy = random.uniform(0, 3)  # Downward movement
            elif rand_val < 0.9:
                self.vy = 0  # No vertical movement
            else:
                self.vy = random.uniform(-3, 0)  # Slight upward movement
                
        self.dy=1/2
        self.game.mob_channel.play(self.game.mobGenerate_Sound)

    def update(self):
        self.rect.x +=self.vx
        self.rect.y += self.vy
        if self.rect.left >width+100 or self.rect.right <-100:
            self.kill()
    
    def die(self):
        """Create explosion animation and then remove the mob"""
        # Create scrollable explosion at mob's position
        MobExplosion(self.game, self.rect.center, 'white')
        # Remove the mob
        self.kill()




class Windwall(pygame.sprite.Sprite):
    def __init__(self,game,x,y,r):
        self.groups =game.all_sprites,game.windwall
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game =game
        
        # Store the rotation angle
        self.rotation = r
        
        # Create the base surface
        self.base_image = pygame.Surface((windwallw, windwallh), pygame.SRCALPHA)
        self.base_image.fill(WHITE)
        
        # Create the initial rotated image
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        self.rect = self.image.get_rect()
        
        # Calculate the spawn position
        spawn_x = self.game.player.pos.x + x
        spawn_y = self.game.player.pos.y + y
        
        # Ensure the wall doesn't spawn outside the screen boundaries
        # Check horizontal boundaries
        if spawn_x < 0:
            spawn_x = 0
        elif spawn_x > width:
            spawn_x = width
            
        # Check vertical boundaries
        if spawn_y < 0:
            spawn_y = 0
        elif spawn_y > height:
            spawn_y = height
            
        # Set the final position
        self.rect.centerx = spawn_x
        self.rect.centery = spawn_y
        
        # Add lifespan variables
        self.birth_time = pygame.time.get_ticks()
        self.lifespan = windwall_life_span  # 3 seconds in milliseconds
        self.alpha = 255  # Start fully visible

    def update(self):
        # Calculate how much life is remaining
        now = pygame.time.get_ticks()
        elapsed = now - self.birth_time
        
        if elapsed >= self.lifespan:
            # Time is up, remove the wall
            self.kill()
        else:
            # Gradually fade out the wall
            remaining_pct = 1 - (elapsed / self.lifespan)
            self.alpha = int(255 * remaining_pct)
            
            # Create a new base image with updated alpha
            self.base_image = pygame.Surface((windwallw, windwallh), pygame.SRCALPHA)
            self.base_image.fill((255, 255, 255, self.alpha))
            
            # Rotate and update the image
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.base_image, self.rotation)
            self.rect = self.image.get_rect()
            self.rect.center = old_center







class Wind(pygame.sprite.Sprite):
    def __init__(self,game,leftorright):
        self.groups =game.all_sprites,game.wind
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game =game
        self.image =self.game.spritesheet.get_image(0,250,100,160)
        self.image.set_colorkey(BLACK)

        self.rect=self.image.get_rect()
        self.rect.x = self.game.player.pos.x + leftorright*50
        self.rect.y = self.game.player.pos.y -100
        self.vx= 15*leftorright
        self.vy=0

    def update(self):
        self.rect.x +=self.vx
        
        # Destroy wind if it goes too far off screen
        # Using a buffer of 300 pixels beyond screen edges
        if self.rect.right < -300 or self.rect.left > width + 300:
            self.kill()


class QIndicator(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((150, 75))  # Width of attack range, height for visibility
        self.image.set_alpha(100)  # Make it semi-transparent
        self.image.fill(BLUE)  # Blue color for the indicator
        self.rect = self.image.get_rect()
        self.active = False
        self.facing_right = True
        self.update_position()
        
    def update(self):
        # Check if Q is available and player is moving (has direction)
        now = pygame.time.get_ticks()
        
        # Calculate if Q is available similar to how main.py does it
        q_cooldown_remaining = max(Q_cd - now + self.game.player.last_update_Q, 0)
        q_available = q_cooldown_remaining == 0
        
        has_direction = abs(self.game.player.vel.x) > 0
        
        # Only show indicator when Q is available and player has a direction
        if q_available and has_direction:
            self.active = True
            # Update facing direction based on player velocity
            self.facing_right = self.game.player.vel.x > 0
            
            # Change color based on Q upgrade status
            if self.game.player.Q_upgrade == 2:
                # Wind ready - use a different color
                self.image.fill(RED)
            else:
                # Normal Q
                self.image.fill(BLUE)
                
            self.update_position()
        else:
            self.active = False
            # Move indicator off-screen when not active
            self.rect.x = -200
            
    def update_position(self):
        if not self.active:
            return
            
        # Position the indicator based on facing direction
        if self.facing_right:
            self.rect.left = self.game.player.pos.x
            self.rect.centery = self.game.player.pos.y - 20  # Slightly above player
        else:
            self.rect.right = self.game.player.pos.x
            self.rect.centery = self.game.player.pos.y - 20


class QEffect(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction, rect,is_wind):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Set up line properties - straight white line
        self.line_length = 150  # Length of attack
        self.line_height = 3    # Thin line
        
        # Create a white line
        self.image = pygame.Surface((self.line_length, self.line_height))
        self.image.fill(WHITE)  # White color for the line
        
        # Position based on direction - start from center of player
        self.rect = self.image.get_rect()
        if direction > 0:  # Facing right
            self.rect.midleft = (x, y - rect.height/2)  # Center of player, slightly above
        else:  # Facing left
            self.rect.midright = (x, y - rect.height/2)  # Center of player, slightly above
            
        # Very fast animation
        self.lifetime = 100  # Only show for 100ms
        self.birth_time = pygame.time.get_ticks()
        
    def update(self):
        # Remove the effect after its lifetime expires
        now = pygame.time.get_ticks()
        if now - self.birth_time > self.lifetime:
            self.kill()  # Animation complete, remove sprite


class AbilityIcon:
    def __init__(self, game, ability_name, icon_size=50):
        self.game = game
        self.name = ability_name
        self.size = icon_size
        self.cooldown = 0
        self.max_cooldown = 0
        self.base_name = ability_name
        self.special_state = False
        self.blink_timer = 0
        self.blink_state = False
        self.blink_speed = 200  # ms per blink
        
        # Load the ability icon
        self.load_icon(ability_name)
            
        # Create overlay surface for cooldown
        self.overlay = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Create highlight effect for special states
        self.highlight = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Gold/yellow highlight for special abilities
        self.highlight.fill((255, 215, 0, 80))
    
    def load_icon(self, ability_name):
        try:
            self.original_icon = pygame.image.load(path.join(self.game.snd_dir, f'Yasuo_{ability_name}.png')).convert_alpha()
            self.icon = pygame.transform.scale(self.original_icon, (self.size, self.size))
        except:
            # Create a fallback icon if image can't be loaded
            self.icon = pygame.Surface((self.size, self.size))
            self.icon.fill((100, 100, 100))
            print(f"Could not load icon: Yasuo_{ability_name}.png")
    
    def change_icon(self, new_suffix):
        """Change the icon based on the Q stack count or other state"""
        if new_suffix:
            self.load_icon(f"{self.base_name}_{new_suffix}")
        else:
            self.load_icon(self.base_name)
    
    def set_special_state(self, is_special):
        """Set if this ability is in a special state (should blink)"""
        self.special_state = is_special
        
    def update(self, current_cooldown, max_cooldown):
        self.cooldown = current_cooldown
        self.max_cooldown = max_cooldown
        
        # Update blink effect if in special state
        if self.special_state:
            now = pygame.time.get_ticks()
            if now - self.blink_timer > self.blink_speed:
                self.blink_timer = now
                self.blink_state = not self.blink_state
        else:
            self.blink_state = False
        
    def draw(self, surface, x, y):
        # Draw the ability icon
        surface.blit(self.icon, (x, y))
        
        # Draw highlight effect for special abilities if in blink-on state
        if self.special_state and self.blink_state and self.cooldown == 0:
            surface.blit(self.highlight, (x, y))
        
        # Only draw cooldown overlay if there is a cooldown
        if self.cooldown > 0 and self.max_cooldown > 0:
            # Calculate the percentage of cooldown remaining
            cooldown_percent = self.cooldown / self.max_cooldown
            
            # Clear the overlay
            self.overlay.fill((0, 0, 0, 0))
            
            # Draw a square cooldown overlay that reveals as cooldown progresses
            # The overlay covers a portion of the icon based on the cooldown percentage
            filled_height = int(self.size * cooldown_percent)
            
            # Draw the dark overlay rectangle
            if filled_height > 0:
                cooldown_rect = pygame.Rect(0, 0, self.size, filled_height)
                pygame.draw.rect(self.overlay, (0, 0, 0, 200), cooldown_rect) 
                
            # Draw the overlay on top of the icon
            surface.blit(self.overlay, (x, y))


class Explosion(pygame.sprite.Sprite):
    def __init__(self, game, center, type='blue'):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Speed of animation
        self.image = game.explosion_anim[self.type][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim[self.type]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_anim[self.type][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class MobExplosion(Explosion):
    """Special explosion for mobs that moves with screen scrolling"""
    def __init__(self, game, center, type='white'):
        super().__init__(game, center, type)
        # Track vertical movement (for scrolling)
        self.y_float = float(self.rect.centery)
        
    def update(self):
        # First perform standard explosion animation update
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim[self.type]):
                self.kill()
                return
            else:
                old_center = self.rect.center
                self.image = self.game.explosion_anim[self.type][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        
        # Handle scrolling - if player is near top of screen, scroll with everything else
        if self.game.player.rect.top < height/4:
            self.y_float += max(abs(self.game.player.vel.y), 2)
            self.rect.centery = int(self.y_float)
            
            # If explosion scrolls off screen, kill it
            if self.rect.top > height:
                self.kill()
















