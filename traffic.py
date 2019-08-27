import pygame
import random
import itertools
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
pygame.display.set_caption('Q-learning traffic lights')


class Car(object):
    def __init__(self, x, y, width, height, light, group):
        self.rect = pygame.draw.rect(screen, C1, (x, y, width, height))
        self.drive = True
        self.light = light
        self.carGroup = group
        self.carInFront = self.carGroup[-1] if len(self.carGroup) > 0 else None

    def update(self, count):
        self.drive = True
        car_group, car, light, car_in_front = self.carGroup, self.rect, self.light, self.carInFront
        if car_group is topCars:
            # IF reached edge of screen DESTROY car
            if car.y >= 610:
                i = car_group.index(self)
                if len(car_group) > 1:
                    car_group[i + 1].carInFront = None
                car_group.remove(self)
                return
            # IF at traffic light or at rear of next car then STOP
            if (car.y + car.height == light.rect.y + light.rect.height and light.status is False) \
                    or (car_in_front is not None and car.y + car.height >= car_in_front.rect.y - 10):
                self.drive = False
            # IF it's okay to drive then MOVE
            if self.drive:
                car.move_ip(0, 10)
        elif car_group is leftCars:
            if car.x >= 610:
                i = car_group.index(self)
                if len(car_group) > 1:
                    car_group[i + 1].carInFront = None
                car_group.remove(self)
                return
            if (car.x + car.width == light.rect.x + light.rect.width and light.status is False) or (
                    car_in_front is not None and car.x + car.width >= car_in_front.rect.x - 10):
                self.drive = False
            if self.drive:
                car.move_ip(10, 0)
        elif car_group is rightCars:
            if car.x <= -20:
                i = car_group.index(self)
                if len(car_group) > 1:
                    car_group[i + 1].carInFront = None
                car_group.remove(self)
                return
            if (car.x == light.rect.x and light.status is False) or (
                    car_in_front is not None and car.x <= car_in_front.rect.x + car_in_front.rect.width + 10):
                self.drive = False
            if self.drive:
                car.move_ip(-10, 0)
        elif car_group is bottomCars:
            if car.y <= -20:
                i = car_group.index(self)
                if len(car_group) > 1:
                    car_group[i + 1].carInFront = None
                car_group.remove(self)
                return
            if (car.y == light.rect.y and light.status is False) or (
                    car_in_front is not None and car.y <= car_in_front.rect.y + car_in_front.rect.height + 10):
                self.drive = False
            if self.drive:
                car.move_ip(0, -10)
        # Record performance
        if self.drive is False:
            bucket = count // PERFORMANCE_STEPS
            performance_dict[bucket] += 1

    def draw(self):
        pygame.draw.rect(screen, C1, self.rect)

    # Returns a value between 0 & 10
    # A distance of 10 means that there is no car
    def dist_from_light(self):
        light, car, car_group = self.light, self.rect, self.carGroup
        distance = -1
        if car_group is topCars:
            distance = ((car.y + car.height) - (car.y + car.height)) / 10
        elif car_group is leftCars:
            distance = ((light.rect.x + light.rect.width) - (car.x + car.width)) / 10
        elif car_group is rightCars:
            distance = (car.x - light.rect.x) / 10
        elif car_group is bottomCars:
            distance = (car.y - light.rect.y) / 10
        return distance if 0 <= distance < 9 else 9


class TrafficLight(object):
    def __init__(self, x, y, width, height, status):
        self.rect = pygame.draw.rect(screen, GREEN, (x, y, width, height))
        self.colour = GREEN if status else RED
        self.status = status

    def switch(self):
        self.colour = RED if self.status else GREEN
        self.status = not self.status

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.rect)


def get_state(time_delay):
    closest_top_bottom_car = 9
    closest_left_right_car = 9
    for c in itertools.chain(topCars, bottomCars):
        closest_top_bottom_car = min(closest_top_bottom_car, c.dist_from_light())
    for c in itertools.chain(leftCars, rightCars):
        closest_left_right_car = min(closest_left_right_car, c.dist_from_light())
    light_state = 1 if topLight.status else 0
    return closest_top_bottom_car, closest_left_right_car, light_state, time_delay


# for writing performance_dict to a file in csv format
def write_to_file(file_name, results_dict):
    file = open(file_name, 'w+')
    for step in results_dict:
        file.write(str(step) + ',' + str(results_dict[step]) + '\n')
    file.close()


def start():
    count, time_delay = 0, 0
    # clock = pygame.time.Clock()
    screen.fill(WHITE)

    # Setup Q-learning agent
    action = Action.STAY
    q_learning_agent = QLearningAgent(state=get_state(time_delay), action=action)

    # Start main event loop
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                write_to_file(f"count_{count}.csv", performance_dict)
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

        # Draw lanes
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
        new_state = get_state(time_delay=time_delay)

        # (3) Choose action a' based off next state
        # (3a) Uncomment next line for manual switch every 10 counts
        action = Action.SWITCH if count % 3 == 0 else Action.STAY
        # (3b) Uncomment next line for q_learning switch
        # action = q_learning_agent.next_best_action(state=new_state)

        # Uncomment for timer to let you know # time of steps elapsed
        if count % 1000 == 0:
            print('count =', count // 1000)
        time_delay = max(time_delay - 1, 0)

        # Uncomment below to set an upper bound for the simulation's FPS
        # clock.tick(10)
        count = count + 1
        pygame.display.flip()


if __name__ == '__main__':
    topLight = TrafficLight(295, 270, 10, 10, True)
    rightLight = TrafficLight(320, 295, 10, 10, False)
    bottomLight = TrafficLight(295, 320, 10, 10, True)
    leftLight = TrafficLight(270, 295, 10, 10, False)
    lights = [topLight, rightLight, bottomLight, leftLight]

    topCars = []
    bottomCars = []
    leftCars = []
    rightCars = []
    allCars = [topCars, leftCars, rightCars, bottomCars]

    PERFORMANCE_STEPS = 1000
    performance_dict = defaultdict(int)

    start()
    pygame.quit()
    quit()
