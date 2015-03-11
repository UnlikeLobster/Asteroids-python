#   Drew Nagy-Kato
#   Asteroids!!!!


#imports the pygame library, and sys library.
import pygame, sys, random, math
#import all your key names
from pygame.locals import *

""" Added features:
    + Implemented asteroid generation
    + Implemented ship polygon rotation
    + Firing is semi-auto (only one bullet per spacebar press)
    + Implemented asteroid collision detection
        + placed all collision functions in asteroid class
    + Implemented multiple asteroid sizes (sml, med, lrg)
        + when hit, randomly break into several smaller asteroids
            1 lrg -> 1-3 med
            1 med -> 1-4 sml
    + Increased ship polygon complexity
    + Asteroids reset upon death
    + GAME OVER splash screen added
        + can quit via ESC or QUIT w/out seeing GAME OVER
    + Added bullet movement wrapping on window edges
"""

''' BUGS
    - **Occasional** crash upon deceleration
'''

''' TODO
    - Add asteroid-asteroid collisions
        + Modify asteroid generation so no asteroid generates intersecting/inside another asteroid
            + "master" ghost asteroid. If extant asteroids intersect master, don't generate
        - Implement asteroid bounce
            - need to add identification to differentiate objects
            - Collision angles need better calculation
        - Collision detection will be sketchy at window edges
    + Implement score keeping
        - Remaining 'mans' as drawn ships
    - Sounds?
'''

WIDTH = 1024
HEIGHT = 768

MANS = 3

BULLETSIZE = 1
SHIPSIZE = 10
FIRE_RANGE = 400
MAX_SHOTS = 20

MIN_SPEED = 0
MAX_SPEED = 14
INC_SPEED = 0.9
DEC_SPEED = 0.4

SM_ASTEROID = 9
MD_ASTEROID = 20
LG_ASTEROID = 27
ASTEROID_SPEED = 5
MIN_ASTEROIDS = 10

SB_YOFFSET = HEIGHT * 0.05

# draw the GAME OVER splash screen
def gameOver(canvas, textColor):
    GGfont = pygame.font.Font(pygame.font.get_default_font(), 128)
    GGstr = 'GAME OVER'

    textBox = GGfont.size(GGstr)
    position = ((WIDTH - textBox[0])/2, (HEIGHT - textBox[1])/2)
    board = GGfont.render(GGstr, 1, textColor, None)
    canvas.blit(board, Rect(position, textBox))

def main():
    #initialize the library and start a clock, just in case we want it.
    pygame.init()
    
    #initialize the clock that will determine how often we render a frame
    clock = pygame.time.Clock()

    #create our canvas that will be draw on.
    resolution = (WIDTH, HEIGHT)
    canvas = pygame.display.set_mode(resolution)
    pygame.display.set_caption('OMG Asteroids!')
    pygame.mouse.set_visible(False)

    #pick our background and other colors with R,G,B values between 0 and 255
    backgroundColor = pygame.Color(0,0,0)
    bulletColor = pygame.Color(255, 255, 255)
    shipColor = pygame.Color(255,255,255)
    astColor = pygame.Color(40,150,255)
    
    #initialize all the default values of variables we want to use
    keysPressed = []
    theShip = Ship(shipColor)
    theAsteroids = []
    theBullets= []
    mouseMovedX = 0
    mouseMovedY = 0
    global deaths
    global score
    deaths = 0
    score = 0
    done = False

    #placeholder asteroid prevents asteroid-generation collisions
    masterAster = Asteroid(0, 0, LG_ASTEROID, astColor)

    #prep scoreboard
    boardFont = pygame.font.Font(pygame.font.get_default_font(), 18)
    scoreStr = 'Score: ' + str(score) + '    Deaths: ' + str(deaths)

    #create a scoreboard
    scoreboard = Scoreboard(scoreStr, boardFont, bulletColor)
    
    #render each frame of the game.
    while not done:
        #get all input events that have happened since the last frame
        for event in pygame.event.get():

            #deal with window closing
            if event.type == QUIT:
                done = True
                pygame.quit()
                return

            #deal with key presses
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                    pygame.quit()
                    return
                else:
                    keysPressed.append(event.key)
                
            
            #deal with key releases
            elif event.type == KEYUP:
                if event.key != K_SPACE or K_SPACE in keysPressed:
                    keysPressed.remove(event.key)
                    
            #deal with mouse movement
            elif event.type == MOUSEMOTION:
                #the mouse has been moved
                mouseMovedX, mouseMovedY = event.pos
                
            #deal with mousebutton
            elif event.type == MOUSEBUTTONDOWN:
                mousePressedX, mousePressedY = event.pos
                if event.button in (1, 2, 3):
                    #left middle or right mouse click
                    pass
            
      
        #generate asteroids
        if len(theAsteroids) < MIN_ASTEROIDS and not any(masterAster.collide(ast) for ast in theAsteroids):
            ast_size = random.choice([LG_ASTEROID, MD_ASTEROID, SM_ASTEROID])
            theAsteroids.append(Asteroid(random.randint(-50, 0), random.randint(-50, 0), ast_size, astColor))

        #fire bullets
        if K_SPACE in keysPressed and len(theBullets) < MAX_SHOTS:
                keysPressed.remove(K_SPACE)
                theBullets.append(Bullet(theShip, bulletColor))
        
        #determine if a ship-asteroid collision happened
        for asteroid in theAsteroids:
            if asteroid.collideShip(theShip):
                deaths += 1

                # reset the game
                theAsteroids[:] = []
                theBullets[:] = []
                theShip.reset()
                break
        
        #determine if a bullet-asteroid collision happened
        for asteroid in theAsteroids:
            for bullet in theBullets:
                if asteroid.collide(bullet):
                    theAsteroids.extend(asteroid.breakup())
                    theAsteroids.remove(asteroid)
                    theBullets.remove(bullet)
                    score += 1
            
        #determine if an asteroid-asteroid collision happened
        for ast1 in theAsteroids:
            for ast2 in theAsteroids:
                if ast1 is not ast2 and ast1.collide(ast2):
                    d_prod = ast1.velocity.dot(ast2.velocity)
                    #print 'dot product: ' + str(d_prod)
                    #theta = math.acos(d_prod)

                    ast1.velocity = -ast1.velocity
                    ast2.velocity = -ast2.velocity
                    
            
        #adjust the ship velocity
        if K_UP in keysPressed:
            theShip.accelerate()
        else:
            theShip.decelerate()
            
        if K_LEFT in keysPressed:
            theShip.rotate(-15)
        if K_RIGHT in keysPressed:
            theShip.rotate(15)
            
        #move the asteroids, players, and bullets
        theShip.move()
        
        for asteroid in theAsteroids:
            asteroid.move()
        
        for bullet in theBullets:
            # delete bullets if they are out of range
            if bullet.distance > FIRE_RANGE:
                theBullets.remove(bullet)
            else:
                bullet.move()
            
            
            
        # Done dealing with events, lets draw updated things on our canvas
        # fill our canvas with a background color, effectively erasing the last frame
        canvas.fill(backgroundColor)
        
        # draw our asteroids
        for asteroid in theAsteroids:
            asteroid.draw(canvas)

        # draw our ship
        theShip.draw(canvas)

        # draw our crosshair
        
        # draw our bullets
        for bullet in theBullets:
            bullet.draw(canvas)

        # draw scoreboard
        scoreboard.draw(canvas)
        
        # done drawing all the stuff on our canvas, now lets show it to the user
        pygame.display.update()

        if deaths >= MANS:
            done = True

        # wait the amount of time
        clock.tick(30)

    # reset the game
    done = False
    canvas.fill(backgroundColor)
    scoreboard.draw(canvas)
    
    gameOver(canvas, bulletColor)

    pygame.display.update()
    
    while not done:
        for event in pygame.event.get():
            #deal with window closing
            if event.type == QUIT:
                done = True
                continue
            
            #deal with key presses
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                    continue
        
        # tick slower than during game
        clock.tick(60)
    
    pygame.quit()
    return

class Asteroid:
    def __init__(self, x, y, size, astColor):
        self.size = size #radius pretty much
        self.color = astColor
        self.x = x
        self.y = y
        self.velocity = pygame.math.Vector2(random.randint(-5,5), random.randint(-5,5))
        
    def draw(self, canvas):
        pygame.draw.circle(canvas, self.color, (int(self.x), int(self.y)), self.size, 5)
        
    def move(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        if (self.y >  HEIGHT + self.size):
            self.y = - self.size*2
        elif (self.y < -self.size*2):
            self.y = HEIGHT + self.size
        if (self.x > WIDTH + self.size):
            self.x = -self.size*2
        elif (self.x < -self.size*2):
            self.x = WIDTH + self.size

    # determine whether the asteroid has collided with a bullet or
    # another asteroid
    def collide(self, other):
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

        if self.size + other.size > distance:
            return True
        else:
            return False

    # determine whether asteroid has collided with the ship
    def collideShip(self, ship):
        # make list of ship's boundaries then determine
        # if any boundary segment intersects or is
        # inside asteroid
        verts = ship.pointlist
        numSides = len(verts)

        # create list of edges, check each for collision
        for curr in verts:
            prev = verts[(verts.index(curr) - 1) % numSides]

            dist_a = pygame.math.Vector2(self.x - curr[0], self.y - curr[1])
            dist_b = pygame.math.Vector2(self.x - prev[0], self.y - prev[1])

            # entire segment is inside asteroid
            if dist_a.length() <= self.size and dist_b.length() <= self.size:
                return True
            else:
                closest = self.closest_pt_on_seg(curr, prev)

                dist = pygame.math.Vector2(self.x - closest[0], self.y- closest[1])

                # if length of dist vector is < radius, then segment intersects
                if dist.length() < self.size:
                    return True
                else:
                    return False

    # determine closest point on line segment to center of asteroid
    def closest_pt_on_seg(self, pt_a, pt_b):
        lnseg = pygame.math.Vector2(pt_b[0] - pt_a[0], pt_b[1] - pt_a[1])
        pt_v = pygame.math.Vector2(self.x - pt_a[0], self.y - pt_a[1])
        seg_unit = lnseg/lnseg.length()
        proj_v_mag = pt_v.dot(seg_unit)

        if proj_v_mag < 0:
            return pt_a
        elif proj_v_mag >= lnseg.length():
            return pt_b
        else:
            proj_v = proj_v_mag * seg_unit
            return pt_a + proj_v
    
    # hit asteroid breaks into smaller asteroids upon collision
    def breakup(self):
        if self.size == LG_ASTEROID:
            pieces = random.randint(1, 3)
            return [Asteroid(self.x, self.y, MD_ASTEROID, self.color) for x in range(pieces)]
        elif self.size == MD_ASTEROID:
            pieces = random.randint(1, 4)
            return [Asteroid(self.x, self.y, SM_ASTEROID, self.color) for x in range(pieces)]
        else:
            return []

        
class Ship:
    def __init__(self, shipColor):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.size = SHIPSIZE
        self.dimensions = []

        # vectors from center to nose, tail, & wings (nose must be last item in list)
        self.Lwing = pygame.math.Vector2(-self.size/2, -self.size/2)
        self.dimensions.append(self.Lwing)
        self.tail = pygame.math.Vector2(-self.size/10, 0)
        self.dimensions.append(self.tail)
        self.Rwing = pygame.math.Vector2(-self.size/2, self.size/2)
        self.dimensions.append(self.Rwing)
        self.nose = pygame.math.Vector2(self.size, 0)
        self.dimensions.append(self.nose)

        # initial velocity in direction of nose
        self.velocity = pygame.math.Vector2(self.nose)
        self.velocity.scale_to_length(MIN_SPEED)
        self.color = shipColor
        
        self.setPoints()

    # rotate ship polygon
    def rotate(self, degrees):
        for x in self.dimensions:
            x.rotate_ip(degrees)
            
        self.setPoints()

    # update points in polygon
    def setPoints(self):
        self.pointlist = [(self.x + x, self.y + y) for (x,y) in self.dimensions]
        
    def draw(self, canvas):
        pygame.draw.polygon(canvas, self.color, [(int(x), int(y)) for (x,y) in self.pointlist], 0)

    # modify ship velocity
    def accelerate(self):
        if self.velocity.length() == MIN_SPEED:
            self.velocity += self.nose
            self.velocity.normalize()
        # accelerate in direction of nose
        else:
            accVec = pygame.math.Vector2(self.nose)
            accVec.scale_to_length(INC_SPEED)
            self.velocity += accVec
            
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)

    # TODO: create new vector of length DEC_SPEED, in direction of self.velocity.
    def decelerate(self):
        if self.velocity.length() == MIN_SPEED:
            pass
        elif self.velocity.length() >= DEC_SPEED:
            decel = pygame.math.Vector2(self.velocity)
            decel.scale_to_length(DEC_SPEED)
            self.velocity -= decel
        #elif self.velocity.length() > MIN_SPEED:
        #    decel = pygame.math.Vector2(self.velocity)
        #    
        else:
            pass
    
    # move ship
    def move(self):
        self.x += self.velocity.x
        self.y += self.velocity.y

        # ship moves beyond edges of window, wrap to other side
        if (self.y >  HEIGHT + self.size):
            self.y = - self.size
        elif (self.y < -self.size):
            self.y = HEIGHT + self.size
        if (self.x > WIDTH + self.size):
            self.x = -self.size
        elif (self.x < -self.size):
            self.x = WIDTH + self.size

        self.setPoints()

    def reset(self):
        self.x = WIDTH/2
        self.y = HEIGHT/2

        self.velocity = pygame.math.Vector2(self.nose)
        self.velocity.scale_to_length(MIN_SPEED)
        
        self.setPoints()


class Bullet:
    def __init__(self, ship, bulletColor):
        # bullet's point of origin (nose of ship)
        self.initX = ship.pointlist[-1][0]
        self.initY = ship.pointlist[-1][1]
        # bullet's current location
        self.x = self.initX
        self.y = self.initY
        # calculate initial direction
        self.velocity = pygame.math.Vector2(ship.nose)
        self.velocity.scale_to_length(max(ship.velocity.length() + ship.nose.length(), 10))
        self.color = bulletColor
        self.size = BULLETSIZE
        self.distance = 0    #distance bullet has traveled


    def draw(self, canvas):
        pygame.draw.circle(canvas, self.color, (int(self.x), int(self.y)), self.size, 0)

    def move(self):
        self.distance += pygame.math.Vector2(self.velocity.x, self.velocity.y).length()
        self.x += self.velocity.x
        self.y += self.velocity.y

        # ship moves beyond edges of window, wrap to other side
        if (self.y >  HEIGHT + self.size):
            self.y = -self.size
        elif (self.y < -self.size):
            self.y = HEIGHT + self.size
        if (self.x > WIDTH + self.size):
            self.x = -self.size
        elif (self.x < -self.size):
            self.x = WIDTH + self.size

        ''' this is why bullets don't draw on other side'''
        #self.distance = pygame.math.Vector2(self.x - self.initX, self.y - self.initY).length()

class Scoreboard:
    def __init__(self, scoreStr, boardFont, scoreColor):
        #font of the scoreboard
        self.boardFont = boardFont
        #string containing the score
        self.scoreStr = scoreStr
        self.color = scoreColor

    def update(self):
        self.scoreStr = "Score: " + str(score) + "    Deaths: " + str(deaths)

    def draw(self, canvas):
        #(height,width) of rect needed to render string
        self.update()
        textBox = self.boardFont.size(self.scoreStr)
        position = ((WIDTH - textBox[0])* 0.95, SB_YOFFSET)
        board = self.boardFont.render(self.scoreStr, 1, self.color, None)
        canvas.blit(board, Rect(position, textBox))

main()
