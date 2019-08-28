import time
import random

LANE_LENGTH = 10
NUM_LANES = 1
lanes = [[0] * LANE_LENGTH * 2 for i in range(NUM_LANES)]


def min_dist_from_light(lane_id: int):
    lane = lanes[lane_id]
    mid = len(lane) // 2
    upcoming_traffic = lane[:mid]
    return upcoming_traffic[::-1].index(1) if 1 in upcoming_traffic else 9


def update_cars(lane_id: int, count: int):
    lane = lanes[lane_id]
    should_generate_new_car = count % (random.randint(0, 10) + 5) == 0
    lane.insert(0, 1) if should_generate_new_car else lane.insert(0, 0)
    lane.pop()


def traffic_simulation():
    epsiodes = range(100)
    for t in epsiodes:
        [update_cars(lane_id=r, count=t) for r in range(len(lanes))]
        print(lanes[0], min_dist_from_light(0), end='\r')
        time.sleep(0.05)
    print()
    pass


if __name__ == '__main__':
    traffic_simulation()
