
width=700
height=700
fps=30
WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(255,0,0)
YELLOW=(255,255,0)
GREEN=(0,255,0)
BLUE=(0,0,255)

E_allowed=1
Dead=0

font_name= "arial"
HS_FILE= 'worldrecord.txt'
SPRITESHEET= 'yasuosheet.png'


mobfre=1000



windwallw=10
windwallh=300
windwall_life_span = 5000
PASSIVE_RECHARGE_DISTANCE=10000

Q_cd=300
W_cd=10000
R_cd=8000
Qwind_cd=10000

fly_time= 1100



#-----------player properties-----------

player_acc=0.7
player_friction= -0.1
player_gravity= 0.7
player_jumpvel= -10



platform_list=[(0,height-40),
               (width/2-50, height*3/4),
               (width/2+50, height*2/4),
               (200, 200),
               (560, 100)]