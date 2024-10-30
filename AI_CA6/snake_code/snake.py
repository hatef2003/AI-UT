from cube import Cube
from constants import *
from utility import *

import random
import random
import numpy as np
def map_to_int(state : list):
    res = 0
    for i in range(len(state)):
        if(state[i]):
            res += 2**i 
    return res
def get_random_max(l):
    maximum_val = max(l)
    max_indexes = [i for i in range(len(l)) if l[i] == maximum_val]
    return  random.choice(max_indexes)
class Snake:
    body = []
    turns = {}

    def __init__(self, color, pos, file_name=None):
        # pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = Cube(pos, color=color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        self.it = int(0)
        try:
            self.q_table = np.load(file_name)
        except:
            self.q_table = np.zeros((2**13,4))

        self.lr = 0.01
        self.discount_factor =0.8
        self.epsilon =0.001

    def get_optimal_policy(self, state):
        return get_random_max(self.q_table[state])
        # TODO: Get optimal policy
        

    def make_action(self, state):
        chance = random.random()
        if chance < self.epsilon:
            action = random.randint(0, 3)
        else:
            action = self.get_optimal_policy(state)
        return action

    def update_q_table(self, state, action, next_state, reward):
        self.q_table[state][action] = self.q_table[state][action] + self.lr*(reward + self.discount_factor*np.max(self.q_table[next_state]) - self.q_table[state][action])
    def get_neighbors_locs(self):
        head_pos = self.head.pos
        left = (head_pos[0]-1 , head_pos[1])
        right =( head_pos[0]+1 , head_pos[1])
        up = (head_pos[0],head_pos[1]-1)
        down = (head_pos[0],head_pos[1]+1)
        return left , right , up , down
    def is_dangerous_loc(self , loc , other_snake) :
        if(loc[0] <= 9 or loc[0] >= ROWS-1 or loc[1] <= 9 or loc[1] >= ROWS-1):
            return True
        if(loc in list(map(lambda z: z.pos, self.body[1:]))):
            return True
        if loc in list(map(lambda z: z.pos, other_snake.body)):
            return True
        return False 
    def get_state(self, snack, other_snake):
        left , right , up , down = self.get_neighbors_locs()
        state = [
            # Danger Straight
            self.is_dangerous_loc(left, other_snake) ,
            self.is_dangerous_loc(right, other_snake),
            self.is_dangerous_loc(up, other_snake)  ,
            self.is_dangerous_loc(down, other_snake),
            snack.pos[0]>self.head.pos[0],
            snack.pos[0]<self.head.pos[0],
            snack.pos[1]>self.head.pos[1],
            snack.pos[1]<self.head.pos[1],
            self.dirnx == 1, 
            self.dirnx == -1, 
            self.dirny == 1,
            self.dirny == -1,
            len(self.body) > len(other_snake.body)
            ] # TODO: Create state
        return map_to_int(state)
    def move(self, snack, other_snake):
        self.it += 1 
        if (self.it == 1600 ):
            self.it = 0 
            self.epsilon*=0.8
        state = self.get_state(snack , other_snake)
        action = self.make_action(state)

        if action == 0: # Left
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 1: # Right
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 2: # Up
            self.dirny = -1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 3: # Down
            self.dirny = 1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

        updated_state = self.get_state(snack,other_snake)# TODO: Create new state after moving and other needed values and return them
        return state , updated_state,action
    def check_out_of_board(self):
        headPos = self.head.pos
        if headPos[0] >= ROWS - 1 or headPos[0] < 10 or headPos[1] >= ROWS - 1 or headPos[1] < 10:
            self.reset((random.randint(3, 18), random.randint(3, 18)))
            return True
        return False
    
    def calc_reward(self, snack, other_snake):
        reward = 0
        win_self, win_other = False, False
        
        if self.check_out_of_board():
            reward = -1000
            win_other = True
            reset(self, other_snake)
        
        if self.head.pos == snack.pos:
            self.addCube()
            snack = Cube(randomSnack(ROWS, self), color=(0, 255, 0))
            reward = 100
            
        if self.head.pos in list(map(lambda z: z.pos, self.body[1:])):
            reward = -1000
            win_other = True
            reset(self, other_snake)
            
            
        if self.head.pos in list(map(lambda z: z.pos, other_snake.body)):
            
            if self.head.pos != other_snake.head.pos:
                reward = -1000
                win_other = True
            else:
                if len(self.body) > len(other_snake.body):
                    reward = 200
                    win_self = True
                elif len(self.body) == len(other_snake.body):
                    reward = 0
                    pass
                else:
                    reward = -100
                    win_other = True
                    
            reset(self, other_snake)
            
        return snack, reward, win_self, win_other
    
    def reset(self, pos):
        self.head = Cube(pos, color=self.color)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), color=self.color))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), color=self.color))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), color=self.color))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), color=self.color))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def save_q_table(self, file_name):
        np.save(file_name, self.q_table)
