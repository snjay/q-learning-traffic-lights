import pygame
import random
from collections import defaultdict
from q_learning import QLearningAgent, Action

pygame.init()

display_width = 600
display_height = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
C1 = (0, 166, 255)

screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Traffic Sim')


def text_objects(text, font):
	textSurface = font.render(text, True, BLACK)
	return textSurface, textSurface.get_rect()


class Car(object):
	def __init__(self, x, y, width, height, light, group):
		self.rect = pygame.draw.rect(screen, C1, (x, y, width, height))
		self.drive = True
		self.light = light
		self.carInFront = None
		self.carGroup = group
		if len(self.carGroup) > 0:
			self.carInFront = self.carGroup[-1]

	def update(self, count):
		self.drive = True
		bucket = count // PERFORMANCE_STEPS
		if self.carGroup is topCars:
			# IF reached edge of screen DESTROY car
			if self.rect.y >= 610:
				i = self.carGroup.index(self)
				if len(self.carGroup) > 1:
					self.carGroup[i + 1].carInFront = None
				self.carGroup.remove(self)
				return
			# IF at traffic light or at rear of next car then STOP
			if (self.rect.y + self.rect.height \
				== self.light.rect.y + self.light.rect.height and \
				self.light.status == False) \
					or (self.carInFront is not None and \
						self.rect.y + self.rect.height >= self.carInFront.rect.y - 10):
				performance_dict[bucket] += 1
				self.drive = False
			# IF it's okay to drive then MOVE
			if self.drive:
				self.rect.move_ip(0, 10)
		elif self.carGroup is leftCars:
			if self.rect.x >= 610:
				i = self.carGroup.index(self)
				if len(self.carGroup) > 1:
					self.carGroup[i + 1].carInFront = None
				self.carGroup.remove(self)
				return

			if (
					self.rect.x + self.rect.width == self.light.rect.x + self.light.rect.width and self.light.status == False) or (
					self.carInFront is not None and self.rect.x + self.rect.width >= self.carInFront.rect.x - 10):
				performance_dict[bucket] += 1
				self.drive = False

			if self.drive:
				self.rect.move_ip(10, 0)
		elif self.carGroup is rightCars:
			if self.rect.x <= -20:
				i = self.carGroup.index(self)
				if len(self.carGroup) > 1:
					self.carGroup[i + 1].carInFront = None
				self.carGroup.remove(self)
				return

			if (self.rect.x == self.light.rect.x and self.light.status == False) or (
					self.carInFront is not None and self.rect.x <= self.carInFront.rect.x + self.carInFront.rect.width + 10):
				performance_dict[bucket] += 1
				self.drive = False

			if self.drive:
				self.rect.move_ip(-10, 0)
		elif self.carGroup is bottomCars:
			if self.rect.y <= -20:
				i = self.carGroup.index(self)
				if len(self.carGroup) > 1:
					self.carGroup[i + 1].carInFront = None
				self.carGroup.remove(self)
				return

			if (self.rect.y == self.light.rect.y and self.light.status == False) or (
					self.carInFront is not None and self.rect.y <= self.carInFront.rect.y + self.carInFront.rect.height + 10):
				performance_dict[bucket] += 1
				self.drive = False

			if self.drive:
				self.rect.move_ip(0, -10)

	def draw(self):
		pygame.draw.rect(screen, C1, self.rect)

	# Returns a value between 0 & 10
	# A distance of 10 means that there is no car
	def distanceFromLight(self):
		if self.carGroup is topCars:
			distance = ((self.light.rect.y + self.light.rect.height) \
						- (self.rect.y + self.rect.height)) / 10
		elif self.carGroup is leftCars:
			distance = ((self.light.rect.x + self.light.rect.width) \
						- (self.rect.x + self.rect.width)) / 10
		elif self.carGroup is rightCars:
			distance = (self.rect.x - self.light.rect.x) / 10
		elif self.carGroup is bottomCars:
			distance = (self.rect.y - self.light.rect.y) / 10
		return distance if 0 <= distance < 9 else 9


class TrafficLight(object):
	def __init__(self, x, y, width, height, status):
		self.rect = pygame.draw.rect(screen, GREEN, (x, y, width, height))
		self.status = status
		self.colour = GREEN if status else RED

	def switch(self):
		self.colour = RED if self.status else GREEN
		self.status = not self.status

	def draw(self):
		pygame.draw.rect(screen, self.colour, self.rect)


def getState(time_delay):
	top_bottom_cars = {9}
	for c in topCars:
		top_bottom_cars.add(c.distanceFromLight())
	for c in bottomCars:
		top_bottom_cars.add(c.distanceFromLight())
	left_right_cars = {9}
	for c in leftCars:
		left_right_cars.add(c.distanceFromLight())
	for c in rightCars:
		left_right_cars.add(c.distanceFromLight())
	lightState = 1 if topLight.status else 0
	return int(min(top_bottom_cars)), int(min(left_right_cars)), lightState, time_delay

# for writing performance_dict to a file in csv format
def write_to_file(file_name, performance_dict):
	file = open(file_name, 'w+')
	for step in performance_dict:
		file.write(str(step) + ',' + str(performance_dict[step]) + '\n')
	file.close()


def start():
	count, time_delay = 0, 0
	clock = pygame.time.Clock()
	screen.fill(WHITE)

	# Setup Q-learning agent
	action = Action.STAY
	q_learning_agent = QLearningAgent(state=getState(time_delay), action=action)

	# Start main event loop
	run = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print(performance_dict)
				write_to_file("count" + str(count) + ".csv", performance_dict)
				pygame.quit()
				quit()

		# Randomly generate a new car in 1 direction
		if count % (random.randint(0, 10) + 5) == 0:
			car_to_append = random.randint(0, 3)
			if car_to_append == 0:
				topCars.append(Car(307, 0, 10, 10, topLight, topCars))
			elif car_to_append == 1:
				leftCars.append(Car(0, 283, 10, 10, leftLight, leftCars))
			if car_to_append == 2:
				rightCars.append(Car(590, 307, 10, 10, rightLight, rightCars))
			if car_to_append == 3:
				bottomCars.append(Car(283, 590, 10, 10, bottomLight, bottomCars))

		# text = pygame.font.Font('freesansbold.ttf',20)
		# TextSurf, TextRect = text_objects("Traffic Sim", text)
		# TextRect = pygame.Rect((0, 0, (display_width/2),(display_height/2)))
		# screen.blit(TextSurf, TextRect)
		pygame.draw.rect(screen, BLACK, (280, 0, 38, 600))
		pygame.draw.rect(screen, BLACK, (0, 280, 600, 38))

		# (1) Perform step with action and update state
		for carGroup in allCars:
			for c in carGroup:
				c.update(count=count)
				c.draw()
		for l in lights:
			l.draw()
		if action == Action.SWITCH and time_delay == 0:
			time_delay = 3
			for l in lights:
				l.switch()

		# (2) Get updated state s'
		new_state = getState(time_delay=time_delay)

		# (3) Choose action a' based off next state
		# (3a) Uncomment next line for manual switch every 10 counts
		# action = Action.SWITCH if count % 10 == 0 else Action.STAY
		# (3b) Uncomment next line for q_learning switch
		action = q_learning_agent.next_best_action(state=new_state)

		# Uncomment for timer to let you know # time of steps elapsed
		if count % 10000 == 0:
			print('count =', count)

		time_delay = max(time_delay - 1, 0)

		# Uncomment below to set an upper bound for the simulation's FPS
		# clock.tick(10)
		count = count + 1
		pygame.display.flip()


lights = list()
topLight = TrafficLight(295, 270, 10, 10, True)
rightLight = TrafficLight(320, 295, 10, 10, False)
bottomLight = TrafficLight(295, 320, 10, 10, True)
leftLight = TrafficLight(270, 295, 10, 10, False)
lights.append(topLight)
lights.append(rightLight)
lights.append(bottomLight)
lights.append(leftLight)

allCars = list()

topCars = list()
leftCars = list()
rightCars = list()
bottomCars = list()

allCars.append(topCars)
allCars.append(leftCars)
allCars.append(rightCars)
allCars.append(bottomCars)

PERFORMANCE_STEPS = 1000
performance_dict = defaultdict(int)

start()
pygame.quit()
quit()
