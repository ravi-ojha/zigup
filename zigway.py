import sys
import pygame
import random
from pygame.locals import *

"""
Determine WIDTH and HEIGHT of the screen.
We have assigned constants right now.
Detect it from the device.
"""
WIDTH = 320
HEIGHT = 480
FPS = 60
FPSCLOCK = pygame.time.Clock()

"""
Colors used
"""
NIGHTSKY = (32,34,46)
LLGRAY = (183,198,200)
LGRAY = (162,175,175)
GRAY = (147,162,162)
DGRAY = (137,150,150)

"""
Setting up the screen and its size
"""
size = [WIDTH,HEIGHT]
screen = pygame.display.set_mode(size)


"""
Setting up the limits of gameplay
We don't want the roads to go to extreme ends
"""
# 10% padding from left
gameLeftLimit = (10*WIDTH)/100
# 10% padding from right
gameRightLimit = WIDTH - (10*WIDTH)/100

"""
segLen is like a brick
minFactor and maxFactor act as multiplier of brick
These help us in deciding where to place next turn in the road
"""
segLen = 10
segFactors = [1,1,1,1,1,2,2,2,2,2,3,3,4,5]
roadDirection = 1
roadPoints = []
speedFactor = 2

def addRoadSegment(currX, currY, roadDirection):
	factor = segFactors[random.randrange(len(segFactors))]
	if roadDirection == 1 and (currX + speedFactor*factor*segLen) < gameRightLimit:
		currX += speedFactor*factor*segLen
		currY -= factor*segLen
	elif (currX - speedFactor*factor*segLen) > gameLeftLimit:
		currX -= speedFactor*factor*segLen
		currY -= factor*segLen
	else:
		currX += speedFactor*factor*segLen
		currY -= factor*segLen
	return [currX, currY]

def initializeRoads(ballRect, roadDirection):
	# Warning: Do not mess around with these two values here
	currX = ballRect.left
	currY = ballRect.top + ballRect.height
	roadPoints.append([currX, currY])
	#this condition helps in adding segments until the road fills up the screen
	while currY >= -(HEIGHT):
		#print "here"
		tmp = addRoadSegment(currX, currY, roadDirection)
		currX = tmp[0]
		currY = tmp[1]
		roadPoints.append(tmp)
		roadDirection = 1 - roadDirection
		#print roadPoints
	return roadDirection

def wait():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                return

"""
This function works only for current game
If you change the slope of roads then this will break
"""
def gameOver(ballRect, roadWidth):
	roadPointsLen = len(roadPoints) - 1
	i = 0
	while i < roadPointsLen-1:

		# Find the line segment
		if ballRect.centery <= roadPoints[i][1] and ballRect.centery > roadPoints[i+1][1]:

			xcord = 0
			# Find the x co-ordinate
			# try to create a simple equation using line segment intersection geometry
			if roadPoints[i][0] < roadPoints[i+1][0]:
				xcord = roadPoints[i][0] + speedFactor*(roadPoints[i][1] - ballRect.centery)
			else:
				xcord = roadPoints[i][0] - speedFactor*(roadPoints[i][1] - ballRect.centery)

			leftLimit = xcord - roadWidth/2
			rightLimit = xcord + roadWidth/2

			if ballRect.centerx < leftLimit or ballRect.centerx > rightLimit:
				return True

			break
		i += 1
	return False

# TODO: Optimization
# I should not be using dirty update() or flip()
# Gotta blit only those things that change
def fallingDown(ball, ballRect, ballSpeed):
	gravity = 0.1
	vel = ballSpeed[:]
	while True:
		if ballRect.top > HEIGHT:
			return
		vel[1] += gravity
		screen.fill(0xffffff)
		roadPointsLen = len(roadPoints)
		i = roadPointsLen - 1
		ballRect = ballRect.move(vel)
		screen.blit(ball, ballRect)
		roadWidth = 3*ballRect.width
		while i > 0:
			frontPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]

			if roadPoints[i-1][0] < roadPoints[i][0]:
				topPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]
				rectPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1] + 1.5*roadWidth], [roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth]]
				pygame.draw.polygon(screen, GRAY, rectPoints, 0)
			else:
				topPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]
				rectPoints = [[roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth]]
				pygame.draw.polygon(screen, LGRAY, rectPoints, 0)
				# This line draws a line at the corners of the wall, don't know if it adds any good feel
				#pygame.draw.line(screen,GRAY,[roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1] + 1.5*roadWidth])

			pygame.draw.polygon(screen, LGRAY, frontPoints, 0)
			pygame.draw.polygon(screen, LLGRAY, topPoints, 0)

			i -= 1
		pygame.display.flip()
		FPSCLOCK.tick(FPS)

def playGame():

	pygame.init()

	#TODO: control speed by ball speed not time delay
	delaySpeed = 8
	score = 0
	"""
	Loading our ball, the main character of the game
	And its aura, the rectangle that surrounds the ball
	This rectangle is going to be very helpful throughout
	"""
	#TODO: draw the ball instead of capturing the image
	ball = pygame.image.load("assets/3d-ball.png")
	ballRect = ball.get_rect()
	#ball's positon from top
	ballRect.top = HEIGHT/2 - ballRect.height/2
	#ball's position from left
	ballRect.left = WIDTH/2 - ballRect.width/2

	roadDirection = 1
	roadDirection = initializeRoads(ballRect, roadDirection)

	# If flag is 1, then wait for the tap or key down to start the game
	flag = 1

	# Initialize ball speed
	#print ballRect
	ballSpeed = [speedFactor,0]
	while True:

		"""
		Handle user activities by checking event log
		For instance: Change ball's direction, Quit game and more
		"""
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				# TODO: ask before they quit in a subtle manner
				return
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					score += 1
					ballSpeed[0] = -ballSpeed[0]
				elif event.key == pygame.K_LEFT:
					if ballSpeed[0] > 0:
						score += 1
						ballSpeed[0] = -ballSpeed[0]
				elif event.key == pygame.K_RIGHT:
					if ballSpeed[0] < 0:
						score += 1
						ballSpeed[0] = -ballSpeed[0]

		"""
		Check for Game Over!
		"""
		if gameOver(ballRect, 3*ballRect.width):
			fallingDown(ball, ballRect, ballSpeed)
			print "Game Over!"
			print "Your Score: %d" % (score)
			return

		# Keep the ball rolling
		ballRect = ballRect.move(ballSpeed)

		"""
		Add new segments to roadPoints as and when required
		When 2nd last point is in the screen and last point is out of the screen
		We should add a new segment
		"""
		if roadPoints[-1][1]+HEIGHT <= 0 and roadPoints[-2][1]+HEIGHT >= 0:
			roadPoints.append(addRoadSegment(roadPoints[-1][0], roadPoints[-1][1], roadDirection))
			roadDirection = 1 - roadDirection

		"""
		Remove points from roadPoints when they are no longer useful
		"""
		if roadPoints[1][1] > HEIGHT:
			del roadPoints[0]

		roadPointsLen = len(roadPoints)

		"""
		Blit things on the screen
		"""
		screen.fill(0xffffff)
		#fill_gradient(screen,DCYANIC,BCYANIC)
		i = roadPointsLen - 1
		roadWidth = 3*ballRect.width
		#print i
		while i > 0:
			frontPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]
			if roadPoints[i-1][0] < roadPoints[i][0]:
				topPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]
				rectPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1] + 1.5*roadWidth], [roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth]]
				pygame.draw.polygon(screen, GRAY, rectPoints, 0)

			else:
				topPoints = [[roadPoints[i-1][0] + roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] + roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]]]
				rectPoints = [[roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1] + 1.5*roadWidth], [roadPoints[i-1][0] - roadWidth/2, roadPoints[i-1][1] + 1.5*roadWidth]]
				pygame.draw.polygon(screen, LGRAY, rectPoints, 0)
				# This line draws a line at the corners of the wall, don't know if it adds any good feel
				#pygame.draw.line(screen,GRAY,[roadPoints[i][0] - roadWidth/2, roadPoints[i][1]], [roadPoints[i][0] - roadWidth/2, roadPoints[i][1] + 1.5*roadWidth])

			pygame.draw.polygon(screen, LGRAY, frontPoints, 0)
			pygame.draw.polygon(screen, LLGRAY, topPoints, 0)

			i -= 1

		for i in xrange(roadPointsLen):
			roadPoints[i][1] += 1

		screen.blit(ball, ballRect)

		if flag:
			# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
			font=pygame.font.Font(None,20)

			# render text
			label = font.render("Press any key to play!", 1, DGRAY)
			labelrect = label.get_rect()
			labelrect.centerx = screen.get_rect().centerx
			labelrect.centery = HEIGHT - 2*labelrect.height
			screen.blit(label, labelrect)

		pygame.display.flip()

		if flag:

			wait()
			flag = 0

		FPSCLOCK.tick(FPS)

playGame()
