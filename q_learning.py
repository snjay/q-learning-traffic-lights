from typing import Tuple, Dict, List
from enum import Enum
import itertools
import random

"""
NOTES
-----
State =
    closest car position from intersection for road 1 (0-8, 9 if no cars) X
    closest car position from intersection for road 2 (0-8, 9 if no cars X
    light setting (ie 0-green, 1 red for one of the roads) X
    light delay (0-3)
 Reward -1.0 if a car is stopped at a red light on either road, zero otherwise.
 Optimise discounted sum of future reward.
 Use discount factor: gamma = .9
 Use learning rate: alpha = .1
 Epsilon-greedy exploration 10%
"""

# Parameters
ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor
EPSILON = 0.1  # Epsilon-greedy exploration

# Type hints to help understand inputs and outputs of functions
Reward = float
State = Tuple[int, int, int, int]
Q_Table = Dict[State, List[Reward]]


class Action(Enum):
    """
    Two actions: decide to switch or not.
    """
    STAY = 0
    SWITCH = 1


class QLearningAgent:
    def __init__(self, state: State, action: Action):
        self._q_table = self._init_q_table()
        self._state = state
        self._action = action

    @staticmethod
    def _init_q_table() -> Q_Table:
        """
        Init function to generate the q_table
        :return: q_table mapping State -> List[STAY reward, SWITCH reward]
        """
        # Define the state space
        state_to_record = (
            range(10),  # closest car position from intersection for road 1 (0-8, 9 if no cars) X
            range(10),  # closest car position from intersection for road 2 (0-8, 9 if no cars X
            range(2),   # light setting (ie 0-green, 1 red for one of the roads) X
            range(4)    # light delay (0-3)
        )
        _q_table = {}
        for i, j, k, l in itertools.product(*state_to_record):
            _q_table[(i, j, k, l)] = [0.0, 0.0]
        return _q_table

    @staticmethod
    def calculate_reward(state: State) -> Reward:
        """
        Calculate reward given a state
        :param state: current state
        :return: The reward at given state
        """
        car_waiting_in_top_bot_lanes = state[0] == 0
        car_waiting_in_left_right_lanes = state[1] == 0
        car_is_waiting = car_waiting_in_top_bot_lanes or car_waiting_in_left_right_lanes
        return -1.0 if car_is_waiting else 0

    def _choose_action(self, state: State) -> Action:
        """
        10% (EPSILON) chance of picking up random choice
        otherwise, pick action from the q_table
        :return: An action to perform
        """
        if random.uniform(0, 1) < EPSILON:
            # Randomly choose an action with probability EPSILON
            action = random.choice([Action.SWITCH, Action.STAY])
        else:
            # Otherwise, pick action with the max payoff in q_table
            q_entry = self._q_table[state]
            # Look at two conditions to determine whether it is better to switch
            # (1) Only allow switch if time_delay == 0
            can_switch = state[3] == 0
            # (2) It is better to switch if pay off for switching better than staying
            better_to_switch = q_entry[1] > q_entry[0]
            # Then, make a decision to switch or not to switch
            if can_switch and better_to_switch:
                action = Action.SWITCH
            else:
                action = Action.STAY
        return action

    def next_best_action(self, state: State):
        """
        Main Q-learning algorithm that determines best action
        and updates the q-table
        :param state: current game's state after taking prev action
        :return: next best action
        """
        # Choose a from given state using q_table
        new_action = self._choose_action(state=state)

        # Observe s' and r of new state
        new_state, reward = state, self.calculate_reward(state=state)

        # Define some short-hand variables to make calculations more legible
        q = self._q_table
        s, a = self._state, self._action.value,
        s_, a_ = new_state, new_action.value

        # Calculate the differences between q(s',a') - q(s,a)
        #   and then, update the q_table
        q[s][a] += ALPHA * (reward + (GAMMA * q[s_][a_]) - q[s][a])

        # Update my internal record of state
        self._state, self._action = s_, new_action

        # Return the new action
        return new_action

    def _debug_q_agent(self):
        import pprint
        q_table = self._q_table
        pprint.pprint([(q, q_table[q]) for q in q_table if q_table[q][0] != 0.0 or q_table[q][1] != 0.0])


if __name__ == '__main__':
    q_learning = QLearningAgent(state=(9, 9, 0, 3), action=Action.STAY)
