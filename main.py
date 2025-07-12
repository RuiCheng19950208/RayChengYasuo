import pygame
from Setting import *
from sprites import *
import random
from pygame.locals import *
from sys import exit
import math
from os import path
from sprites import Player, platform, Mob, Windwall, Wind, Spritesheet, AbilityIcon, Explosion

vec = pygame.math.Vector2


class Game:
    def __init__(self):

        # game window initialize
        pygame.init()
        pygame.mixer.init()  # 
        
        # Set up sound channels to prevent overlapping audio
        pygame.mixer.set_num_channels(16)  # Increase total available channels (default is 8)
        self.effect_channel = pygame.mixer.Channel(0)  # For general effects
        self.ability_q_channel = pygame.mixer.Channel(1)  # For Q abilities
        self.ability_w_channel = pygame.mixer.Channel(2)  # For W ability main sound
        self.w_block_channel = pygame.mixer.Channel(3)  # For W ability block sound
        self.ability_e_channel = pygame.mixer.Channel(4)  # For E abilities
        self.ultimate_channel = pygame.mixer.Channel(5)  # For R ability (highest priority)
        self.passive_channel = pygame.mixer.Channel(6)  # For passive shield
        self.mob_channel = pygame.mixer.Channel(7)  # For mob sounds
        self.ui_channel = pygame.mixer.Channel(8)  # For UI sounds
        self.death_channel = pygame.mixer.Channel(9)  # For primary death sound
        self.death_channel2 = pygame.mixer.Channel(10)  # For secondary death sound
        self.hasaki_channel = pygame.mixer.Channel(11)  # Dedicated channel for hasaki sound
        
        # Set volume levels
        self.mob_channel.set_volume(0.5)
        self.hasaki_channel.set_volume(1.0)  # Maximum volume for hasaki
        
        # Get information about the display
        info = pygame.display.Info()
        self.monitor_width = info.current_w
        self.monitor_height = info.current_h
        
        # Create the screen in fullscreen mode
        self.screen = pygame.display.set_mode((self.monitor_width, self.monitor_height), FULLSCREEN, 32)
        # self.screen = pygame.display.set_mode((width, height), 0, 32)
        
        # Calculate the offset to center the game canvas
        self.offset_x = (self.monitor_width - width) // 2
        self.offset_y = (self.monitor_height - height) // 2
        
        # Create a separate surface for the actual game at the original resolution
        self.game_surface = pygame.Surface((width, height))
        
        pygame.display.set_caption("Ray Cheng Yasuo!")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font(font_name)
        self.dead = Dead
        
        # Initialize shared particles for all screens
        self.particles = []
        for i in range(25):  # Create 25 particles
            self.particles.append([random.randint(0, width), random.randint(0, height), random.randint(1, 3)])
        
        self.loaddata()
        self.Fly_timer = 0
        self.last_fly = 0
        
        # Initialize cooldown attributes
        self.Q_allowed = 0
        self.W_allowed = 0
        self.R_allowed = 0
        self.Quptime = 0

    def loaddata(self):
        self.dir = path.dirname(__file__)
        img_dir=path.join(self.dir)
        with open(path.join(self.dir, HS_FILE),'r+') as f:
            try:
                self.highscore= int(f.read())
            except:
                self.highscore = 0

        self.spritesheet=Spritesheet(path.join(img_dir,SPRITESHEET))

        self.snd_dir = path.join(self.dir,'NewYasuo')
        self.jump_sound= pygame.mixer.Sound(path.join(self.snd_dir,'File0053jump.wav'))

        self.passive_sound= pygame.mixer.Sound(path.join(self.snd_dir, 'passive.ogg'))
        self.passive_sound.set_volume(1)


        self.Q_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'File0461QAttack.wav'))
        # self.Q_sound.set_volume()




        self.Q_hit = pygame.mixer.Sound(path.join(self.snd_dir, 'Q.wav'))

        self.Q_getwind = pygame.mixer.Sound(path.join(self.snd_dir, 'File0409getwind.wav'))
        self.Q_getwind.set_volume(0.5)

        self.Q_hasaki = pygame.mixer.Sound(path.join(self.snd_dir, 'hasaki.wav'))
        self.Q_hasaki.set_volume(1.5)  # Ensure maximum volume


        self.Q_windhit = pygame.mixer.Sound(path.join(self.snd_dir, 'File0405Windhit.wav'))
        self.Q_windhit.set_volume(0.5)







        # self.W_sound1 = pygame.mixer.Sound(path.join(self.snd_dir, 'W.wav'))
        self.W_sound1 = pygame.mixer.Sound(path.join(self.snd_dir, 'W.ogg'))




        self.W_block= pygame.mixer.Sound(path.join(self.snd_dir, 'File0464block.wav'))
        self.W_block.set_volume(0.2)

        self.E_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'File0429E.wav'))
        self.E_sound.set_volume(0.5)



        self.R_sound1 = pygame.mixer.Sound(path.join(self.snd_dir, 'R.wav'))

        self.mobGenerate_Sound = pygame.mixer.Sound(path.join(self.snd_dir, 'ping_missing.mp3'))
        self.mobGenerate_Sound.set_volume(0.3)

        





        # self.start_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Yasuo.wav'))
        self.start_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Yasuo.ogg'))

        self.dead_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'File0030doge.wav'))
        self.dead_sound2 = pygame.mixer.Sound(path.join(self.snd_dir, 'yasuodead.wav'))
        self.dead_sound.set_volume(0.4)

        # Load explosion animation
        self.explosion_anim = {}
        self.explosion_anim['blue'] = []
        self.explosion_anim['white'] = []
        
        # Load blue explosions (shield effect)
        explosionsize = 100  # Size of explosion sprites
        explosion_sheet = pygame.image.load(path.join(self.snd_dir, 'explosion.png')).convert()
        
        # Function to extract images from spritesheet
        def get_image(sheet, x, y, width, height):
            image = pygame.Surface((width, height))
            image.blit(sheet, (0, 0), (x, y, width, height))
            return image
        
        # Load blue explosion animation frames from spritesheet
        for i in range(7):  # Assuming 7 frames in the spritesheet
            imgblue = get_image(explosion_sheet, 373 + 34 * i, 150, 34, 34)
            imgblue.set_colorkey(BLACK)
            imgblue = pygame.transform.scale(imgblue, (explosionsize, explosionsize))
            self.explosion_anim['blue'].append(imgblue)
            
        # Optional: Load white explosion animation for other effects
        for i in range(7):
            imgyellow = get_image(explosion_sheet, 373+34*i,9,34,34)
            imgyellow.set_colorkey(BLACK)
            imgyellow = pygame.transform.scale(imgyellow, (explosionsize, explosionsize))
            self.explosion_anim['white'].append(imgyellow)



    def new(self):
        #restart
        self.score=0

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.mobs= pygame.sprite.Group()
        self.windwall = pygame.sprite.Group()
        self.wind = pygame.sprite.Group()

        self.mob_timer = 0
        
        # Create gameplay gradient background - enhanced blue
        self.background = pygame.Surface((width, height))
        for y in range(height):
            # Rich blue gradient from top to bottom
            blue_value = max(0, 80 - int(y * 60 / height))
            # Add slight cyan tint with a touch of green
            green_value = max(0, 20 - int(y * 20 / height))
            self.background.fill((0, green_value, blue_value), (0, y, width, 1))
        
        # Reset particle positions (using shared particles)
        for p in self.particles:
            p[0] = random.randint(0, width)
            p[1] = random.randint(0, height)

        # Create ability icons
        self.passive_icon = AbilityIcon(self, "Way_of_the_Wanderer")
        self.q_icon = AbilityIcon(self, "Steel_Tempest")
        self.w_icon = AbilityIcon(self, "Wind_Wall")
        self.e_icon = AbilityIcon(self, "Sweeping_Blade")
        self.r_icon = AbilityIcon(self, "Last_Breath")

        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Create predefined platforms from the platform_list
        for plat in platform_list:
            p = platform(self, *plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
            
        # Create a starting platform at the center-bottom of the screen
        start_platform_width = 200
        start_platform_x = width/2 - start_platform_width/2
        start_platform_y = height - 100  # 100 pixels from the bottom
        start_platform = platform(self, start_platform_x, start_platform_y)
        self.all_sprites.add(start_platform)
        self.platforms.add(start_platform)
        
        # Position player on the starting platform
        self.player.pos.x = start_platform.rect.centerx
        self.player.pos.y = start_platform.rect.top
        self.player.rect.midbottom = self.player.pos
        self.player.vel = vec(0, 0)
        self.player.acc = vec(0, 0)
        self.player.last_position = self.player.pos.copy()
            
        pygame.mixer.music.load(path.join(self.snd_dir,'File0031Music.wav'))
        self.run()

    def run(self):
        # game loop
        pygame.mixer.music.play(loops=-1)

        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
        
        # Player died, transition the background to red
        if self.running:  # Only do transition if game is still running (player died but didn't quit)
            # Play death sounds on separate channels to allow them to play simultaneously
            self.death_channel.play(self.dead_sound)
            self.death_channel2.play(self.dead_sound2)
            self.transition_to_red()
            
        pygame.mixer.music.fadeout(1000)

    def transition_to_red(self):
        # Create destination red gradient background - make sure it matches show_gameover_screen
        red_background = pygame.Surface((width, height))
        for y in range(height):
            color_value = max(0, 50 - int(y * 50 / height))
            red_background.fill((color_value, 0, 0), (0, y, width, 1))
        
        # Create a copy of the current blue background
        current_background = self.background.copy()
        
        # Clear all sprites immediately
        self.all_sprites.empty()
        self.platforms.empty()
        self.mobs.empty()
        self.windwall.empty()
        self.wind.empty()


        
        
        # Perform the transition
        start_time = pygame.time.get_ticks()
        transition_duration = 1500  # 1.5 seconds for transition
        

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - start_time
            
            # Calculate transition progress (0.0 to 1.0)
            if elapsed >= transition_duration:
                progress = 1.0
                running = False
            else:
                progress = elapsed / transition_duration
            
            # Create transition frame by blending between backgrounds
            transition_frame = pygame.Surface((width, height))
            for y in range(height):
                # Get colors from both backgrounds at this y position
                current_pixel = current_background.get_at((1, y))
                red_pixel = red_background.get_at((1, y))
                
                # Blend the colors based on progress
                r = int(current_pixel[0] * (1 - progress) + red_pixel[0] * progress)
                g = int(current_pixel[1] * (1 - progress) + red_pixel[1] * progress)
                b = int(current_pixel[2] * (1 - progress) + red_pixel[2] * progress)
                
                transition_frame.fill((r, g, b), (0, y, width, 1))
            
            # Fill entire screen with black
            self.screen.fill(BLACK)
            
            # Draw transition on game surface
            self.game_surface.blit(transition_frame, (0, 0))
            
            # Update particles - transition from blue to red particles
            for p in self.particles:
                p[1] = (p[1] + p[2]/2) % height
                # Change particle color from gameplay color (100, 180, 255) to game over color (255, min(100, p[1] % 200), min(100, p[1] % 200))
                particle_r = int(100*(1-progress) + 255*progress)
                particle_g = int(180*(1-progress) + min(100, p[1] % 200)*progress)
                particle_b = int(255*(1-progress) + min(100, p[1] % 200)*progress)
                pygame.draw.circle(self.game_surface, (particle_r, particle_g, particle_b), (p[0], p[1]), p[2])
            
            # Draw score on game surface
            self.draw_text('Score:'+str(self.score), 22, WHITE, 50, 50, self.game_surface)
            
            # Blit game surface to screen at centered position
            self.screen.blit(self.game_surface, (self.offset_x, self.offset_y))
            
            # Check for quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                # Check for ESC key press to exit immediately
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    self.running = False
            
            # Also check for held ESC key
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False
                self.running = False
            
            pygame.display.flip()
            self.clock.tick(fps)

    def update(self):
        #loop update
        self.all_sprites.update()
        now= pygame.time.get_ticks()
        
        # Update background particles
        for p in self.particles:
            p[1] = (p[1] + p[2]) % height  # Move particles up and wrap around

        # self.player.W_timer= max(0,now-self.player.W_timer)
        self.Quptime =   max(Qwind_cd-now + self.player.Q_timer, 0)
        self.Q_allowed = max(Q_cd- now + self.player.last_update_Q, 0)
        self.W_allowed = max(W_cd- now + self.player.last_update_W, 0)
        self.R_allowed = max(R_cd- now + self.player.last_update_R, 0)
        self.Fly_timer = max(fly_time - now + self.last_fly, 0)
        # self.player.R_getwind_timer = max(0, now - self.player.R_getwind_timer)

        # Update Q icon based on stacks
        if self.player.Q_upgrade == 0:
            self.q_icon.change_icon(None)  # Base icon
            self.q_icon.set_special_state(False)
        elif self.player.Q_upgrade == 1:
            self.q_icon.change_icon("2")   # One stack
            self.q_icon.set_special_state(False)
        elif self.player.Q_upgrade == 2:
            self.q_icon.change_icon("3")   # Two stacks (tornado ready)
            self.q_icon.set_special_state(True)  # Make icon blink when tornado is ready
            
        # Set R to blink when it's available to use
        self.r_icon.set_special_state(self.Fly_timer > 0)
        
        # Update passive icon based on energy level
        self.passive_icon.update(
            self.player.max_energy - self.player.energy,  # Use remaining energy as "cooldown"
            self.player.max_energy
        )
        # Set blinking state when shield is ready
        self.passive_icon.set_special_state(self.player.energy >= self.player.max_energy)
            
        # Update ability icons cooldowns
        self.q_icon.update(self.Q_allowed, Q_cd)
        self.w_icon.update(self.W_allowed, W_cd)
        self.e_icon.update(0 if self.player.E_allowed > 0 else 1, 1)  # E is binary (available or not)
        self.r_icon.update(self.R_allowed, R_cd)

        if self.Quptime == 0:
            self.player.Q_upgrade=0

        if now- self.mob_timer> max(250, mobfre - self.score):
            self.mob_timer= now
            Mob(self)

        mob_hits = pygame.sprite.spritecollide(self.player,self.mobs,False)
        if mob_hits:
            # Check if passive shield is ready
            if self.player.energy >= self.player.max_energy:
                # Shield absorbs the hit
                for mob in mob_hits:
                    mob.die()
                # Reset shield energy
                self.player.energy = 0
                # Play shield activation sound
                self.passive_channel.play(self.passive_sound)
                
                # Create a single explosion effect at the player's position
                Explosion(self, self.player.rect.center)
            else:
                # No shield, player dies
                self.playing = False

        for mob in self.mobs:
            if pygame.sprite.spritecollide(mob,self.windwall,False):
                mob.die()
                self.w_block_channel.play(self.W_block)
            if pygame.sprite.spritecollide(mob,self.wind,False):
                mob.die()
                self.last_fly = now
                self.ability_q_channel.play(self.Q_windhit)

        if self.player.vel.y>0:
            hits = pygame.sprite.spritecollide(self.player,self.platforms,False)
            if hits:
                lowest=hits[0]
                for h in hits:
                    if h.rect.bottom > lowest.rect.bottom:
                        lowest =h

                if self.player.pos.x < lowest.rect.right and self.player.pos.x > lowest.rect.left:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.pos.y=lowest.rect.top
                        self.player.vel.y=0
                        self.player.E_allowed=1

        #Scroll screen option

        if self.player.rect.top < height/4:

                self.player.pos.y += max(abs(self.player.vel.y),2)
                for mob in self.mobs:

                    mob.rect.y += max(abs(self.player.vel.y),2)
                    if mob.rect.top> height:
                        mob.kill()

                for wall in self.windwall:

                    wall.rect.y += max(abs(self.player.vel.y),2)
                    if wall.rect.top> height:
                        wall.kill()

                for w in self.wind:

                    w.rect.y += max(abs(self.player.vel.y),2)
                    if w.rect.top> height:
                        w.kill()



                for plat in self.platforms:

                    plat.rect.y += max(abs(self.player.vel.y),2)
                    if plat.rect.top> height:
                        plat.kill()
                        self.score +=10


        if self.player.rect.bottom>height:
            for i in self.all_sprites:
                i.rect.y -= max(self.player.vel.y,10)
                if i.rect.bottom <0:
                    i.kill()
        if len(self.platforms)==0:
            self.playing = False

        while len(self.platforms)<6:
            
            # Try to create a platform that doesn't overlap with existing ones
            self.spawn_platform()

    def spawn_platform(self):
        """Spawn a new platform ensuring it doesn't overlap with existing platforms"""
        # Platform dimensions - get from spritesheet dimensions to be accurate
        plat_width = random.randrange(50, 100)
        plat_height = 32  # Height of platforms in the spritesheet
        
        # Maximum attempts to find non-overlapping position
        max_attempts = 15
        attempts = 0
        
        while attempts < max_attempts:
            # Generate random position
            x = random.randrange(0, width - plat_width)
            y = random.randrange(-70, -20)
            
            # Create a temporary rect to check for collisions
            test_rect = pygame.Rect(x, y, plat_width, plat_height)
            
            # Check if this rect overlaps with any existing platform
            overlap = False
            for plat in self.platforms:
                if test_rect.colliderect(plat.rect):
                    overlap = True
                    break
            
            # If no overlap found, create the platform and exit loop
            if not overlap:
                p = platform(self, x, y)
                self.platforms.add(p)
                self.all_sprites.add(p)
                return True
            
            attempts += 1
        
        # If we reach max attempts and still can't place a platform
        # Place one anyway at the last tried position (better than nothing)
        p = platform(self, x, y)
        self.platforms.add(p)
        self.all_sprites.add(p)
        return False

    def events(self):

        #define trigger

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                if self.playing:
                    self.playing = False
                self.running = False

                



    def draw_mob_indicators(self):
        """Draw indicators at screen edges for approaching mobs that are off-screen"""
        indicator_inset = 10  # Distance from edge where indicators appear
        circle_radius = 10    # Size of the indicator circle
        
        for mob in self.mobs:
            # Check if mob is outside the visible screen area
            if mob.rect.right < 0 or mob.rect.left > width:
                # Determine which side the mob is approaching from
                if mob.rect.right < 0 and mob.vx > 0:  # Coming from left
                    # Draw circle indicator inside left edge
                    pygame.draw.circle(self.game_surface, RED, 
                                     (indicator_inset, mob.rect.centery), 
                                     circle_radius)
                elif mob.rect.left > width and mob.vx < 0:  # Coming from right
                    # Draw circle indicator inside right edge
                    pygame.draw.circle(self.game_surface, RED, 
                                     (width - indicator_inset, mob.rect.centery), 
                                     circle_radius)

    def draw(self):
        # draw in the window - now using game_surface instead of screen directly
        # self.screen.fill(BLACK)
        
        # Fill the entire screen with black
        self.screen.fill(BLACK)
        
        # Draw the background gradient on game_surface
        self.game_surface.blit(self.background, (0, 0))
        
        # Draw background particles with a brighter color
        for p in self.particles:
            # Lighter blue/cyan particles that stand out against the background
            pygame.draw.circle(self.game_surface, (100, 180, 255), (p[0], p[1]), p[2])
        
        # Draw all sprites on the game surface
        self.all_sprites.draw(self.game_surface)
        
        # Draw edge indicators for approaching mobs that are off-screen
        self.draw_mob_indicators()
        
        # Draw score text
        self.draw_text('Score:'+str(self.score), 22, WHITE, 50, 50, self.game_surface)
        
        # Draw ability icons in a column at the top left corner
        icon_x = 30  # Position at top left
        icon_spacing = 60     # Space between icons
        
        # Draw passive icon (above Q)
        self.passive_icon.draw(self.game_surface, icon_x, 80)
        
        # Draw Q icon (moved down)
        self.q_icon.draw(self.game_surface, icon_x, 80 + icon_spacing)
            
        # Draw W icon (moved down)
        self.w_icon.draw(self.game_surface, icon_x, 80 + icon_spacing*2)
        
        # Draw E icon (moved down)
        self.e_icon.draw(self.game_surface, icon_x, 80 + icon_spacing*3)
            
        # Draw R icon (moved down)
        self.r_icon.draw(self.game_surface, icon_x, 80 + icon_spacing*4)
        
        # Blit the game surface onto the screen at the centered position
        self.screen.blit(self.game_surface, (self.offset_x, self.offset_y))
        
        pygame.display.flip()

    def show_start_screen(self):
        pygame.mixer.music.load(path.join(self.snd_dir, 'File0490.wav'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()
        self.ui_channel.play(self.start_sound)

        # Create the same blue gradient background as gameplay
        background = pygame.Surface((width, height))
        for y in range(height):
            # Rich blue gradient from top to bottom
            blue_value = max(0, 80 - int(y * 60 / height))
            # Add slight cyan tint with a touch of green
            green_value = max(0, 20 - int(y * 20 / height))
            background.fill((0, green_value, blue_value), (0, y, width, 1))
        
        # Reset particle positions for start screen
        for p in self.particles:
            p[0] = random.randint(0, width)
            p[1] = random.randint(0, height)
        
        # Title and instructions
        title = 'Ray Cheng YASUO'
        subtitle = 'The Cancer'
        
        waiting = True
        while waiting:
            self.clock.tick(fps)
            
            # Check for exit or continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False
                # Check for ESC key press to exit immediately
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                    self.running = False
            
            # Also check for held ESC key
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                waiting = False
                self.running = False
            
            # Fill screen with black
            self.screen.fill(BLACK)
            
            # Draw background on game surface
            self.game_surface.blit(background, (0, 0))
            
            # Update and draw particles with the same color as gameplay
            for p in self.particles:
                p[1] = (p[1] + p[2]) % height
                pygame.draw.circle(self.game_surface, (100, 180, 255), (p[0], p[1]), p[2])
            
            # Draw title with shadow effect
            self.draw_text(title, 50, WHITE, width/2, height/6, self.game_surface)
            self.draw_text(subtitle, 25, (150, 150, 255), width/2, height/6 + 90, self.game_surface)
            
            # Draw divider
            pygame.draw.line(self.game_surface, (100, 100, 255), (width/4, height/3 + 40), (width*3/4, height/3 + 40), 2)
            
            # Ability descriptions in a cleaner layout
            ability_y = height/3 + 70
            ability_spacing = 55
            
            # Draw ability descriptions with icons
            self.draw_text('Abilities:', 30, WHITE, width/2, ability_y, self.game_surface)
            
            # Q ability
            self.draw_text('Q - Steel Tempest', 22, (200, 200, 255), width/2, ability_y + ability_spacing, self.game_surface)
            self.draw_text('Strike forward dealing damage. Hit twice to create a tornado!', 16, WHITE, width/2, ability_y + ability_spacing + 25, self.game_surface)
            
            # W ability
            self.draw_text('W - Wind Wall', 22, (200, 200, 255), width/2, ability_y + ability_spacing*2, self.game_surface)
            self.draw_text('Create a protective barrier that blocks enemy attacks', 16, WHITE, width/2, ability_y + ability_spacing*2 + 25, self.game_surface)
            
            # E ability
            self.draw_text('E - Sweeping Blade', 22, (200, 200, 255), width/2, ability_y + ability_spacing*3, self.game_surface)
            self.draw_text('Dash upward with an extra jump when falling', 16, WHITE, width/2, ability_y + ability_spacing*3 + 25, self.game_surface)
            
            # R ability
            self.draw_text('R - Last Breath', 22, (200, 200, 255), width/2, ability_y + ability_spacing*4, self.game_surface)
            self.draw_text('Powerful attack available after hitting enemies with tornado', 16, WHITE, width/2, ability_y + ability_spacing*4 + 25, self.game_surface)
            
            # Start prompt with pulsing effect
            pulse = (math.sin(pygame.time.get_ticks() / 300) + 1) * 20 + 215
            start_color = (255, min(255, int(pulse)), min(255, int(pulse)))
            self.draw_text('Press Any Key To Start', 36, start_color, width/2, height - 100, self.game_surface)
            
            # Blit game surface to screen at centered position
            self.screen.blit(self.game_surface, (self.offset_x, self.offset_y))
            
            pygame.display.flip()
        
        pygame.mixer.music.fadeout(1000)


    def show_gameover_screen(self):
        if not self.running:
            return

        # No need to play death sounds here as they are played during transition
        # self.dead_sound.play()
        # self.dead_sound2.play()
        self.dead = self.dead + 1

        # Create a gradient background (dark red to black)
        # This should match the final frame in transition_to_red
        background = pygame.Surface((width, height))
        for y in range(height):
            color_value = max(0, 50 - int(y * 50 / height))
            background.fill((color_value, 0, 0), (0, y, width, 1))
        
        # Don't reset particle positions - maintain continuity from gameplay
        
        # Death messages - randomly select one
        death_messages = [
            "DEFEAT",
            "DEATH IS LIKE THE WIND...",
            "A YASUO HAS FALLEN",
            "DISHONOR"
        ]
        death_message = random.choice(death_messages)
        
        waiting = True
        start_time = pygame.time.get_ticks()
        
        while waiting:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - start_time
            self.clock.tick(fps)
            
            # Check for exit or continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP and elapsed > 1000:  # Prevent accidental skipping
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                    self.running = False
            
            # Also check for held ESC key
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                waiting = False
                self.running = False
            
            # Fill screen with black
            self.screen.fill(BLACK)
            
            # Draw background on game surface
            self.game_surface.blit(background, (0, 0))
            
            # Update and draw particles - using the same color scheme as the final frame in transition_to_red
            for p in self.particles:
                p[1] = (p[1] + p[2]) % height
                # Use consistent red particle colors that match the end of transition
                pygame.draw.circle(self.game_surface, (255, min(100, p[1] % 200), min(100, p[1] % 200)), (p[0], p[1]), p[2])
            
            # Draw death message with glowing effect
            glow = (math.sin(current_time / 300) + 1) * 30 + 150
            self.draw_text(death_message, 35, (255, min(150, int(glow)), min(150, int(glow))), width/2, height/6, self.game_surface)
            
            # Draw score info in a box
            score_box_y = height/3 + 30
            score_box_height = 150
            pygame.draw.rect(self.game_surface, (50, 0, 0), (width/4, score_box_y, width/2, score_box_height))
            pygame.draw.rect(self.game_surface, (150, 0, 0), (width/4, score_box_y, width/2, score_box_height), 2)
            
            if self.score > self.highscore:
                self.highscore = self.score
                with open(path.join(self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.score))
                # Draw new highscore indicator
                self.draw_text('NEW RECORD!', 26, (255, 255, 0), width/2, score_box_y + 15, self.game_surface)
                y_offset = 30
            else:
                y_offset = 0
                
            self.draw_text(f'SCORE: {self.score}', 28, WHITE, width/2, score_box_y + 40 + y_offset, self.game_surface)
            self.draw_text(f'BEST: {self.highscore}', 22, (200, 200, 200), width/2, score_box_y + 75 + y_offset, self.game_surface)
            
            # Draw K/D/A stats
            kda_y = score_box_y + score_box_height + 30
            pygame.draw.rect(self.game_surface, (40, 0, 0), (width/3, kda_y, width/3, 70))
            pygame.draw.rect(self.game_surface, (100, 0, 0), (width/3, kda_y, width/3, 70), 2)
            
            self.draw_text('K / D / A', 15, (200, 200, 0), width/2, kda_y + 10, self.game_surface)
            self.draw_text(f'0 / {self.dead} / 0', 15, (255, 255, 0), width/2, kda_y + 40, self.game_surface)
            
            # Draw retry prompt with pulsing effect
            if elapsed > 1000:  # Only show after a short delay
                pulse = (math.sin(current_time / 300) + 1) * 20 + 215
                retry_color = (min(255, int(pulse)), min(255, int(pulse/2)), 0)
                self.draw_text('Press Any Key To Try Again', 25, retry_color, width/2, height - 100, self.game_surface)
            
            # Blit game surface to screen at centered position
            self.screen.blit(self.game_surface, (self.offset_x, self.offset_y))
            
            pygame.display.flip()
            
        pygame.mixer.music.fadeout(500)

    def draw_text(self,text,size,color,x,y,surface=None):
        font=pygame.font.Font(self.font_name,size)
        text_surface = font.render(text,True,color)
        text_rect= text_surface.get_rect()
        if surface:
            text_rect.midtop=(x,y)
            surface.blit(text_surface,text_rect)
        else:
            text_rect.midtop=(x,y)
            self.screen.blit(text_surface,text_rect)

    def waitforkey(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False
g=Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_gameover_screen()

pygame.quit()

