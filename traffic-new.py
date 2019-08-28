import time
import random

LANE_LENGTH = 8
NUM_LANES = 2
lanes, lights = [], []
for i in range(NUM_LANES):
    lanes.append([0] * LANE_LENGTH * 2)
    lights.append(i % 2 == 0)


def switch_lights():
    global lights
    lights = [not l for l in lights]


def min_dist_from_light(lane_id: int):
    lane = lanes[lane_id]
    mid = len(lane) // 2
    upcoming_traffic = lane[:mid]
    return upcoming_traffic[::-1].index(1) if 1 in upcoming_traffic else 9


def update_cars(lane_id: int, count: int):
    lane = lanes[lane_id]
    lights_are_on = lights[lane_id]
    should_generate_new_car = count % (random.randint(0, 10) + 5) == 0
    if lights_are_on:
        lane.insert(0, 1) if should_generate_new_car else lane.insert(0, 0)
        lane.pop()


def traffic_simulation():
    epsiodes = range(1000)
    for t in epsiodes:
        for r in range(len(lanes)):
            update_cars(lane_id=r, count=t)
        if t % 50 == 0:
            switch_lights()
        print(lanes, min_dist_from_light(0), lights, end='\r')
        time.sleep(0.05)
    print()
    pass


if __name__ == '__main__':
    traffic_simulation()
