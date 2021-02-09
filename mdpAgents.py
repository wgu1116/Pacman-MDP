# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Malcolm (wgu1996@gmail.com), based on the code 
# on https://github.com/wpddmcmc/Pacman_MDP/blob/master/mdpAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # Lists to store useful informations
        self.visited_pos = []            # A list to store visited locations
        self.food_pos = []               # Store a permanent list of food
        self.capsules_pos = []
        self.walls_pos = []

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # Clear all storage data before next time run
        self.visited_pos = []
        self.food_pos = []   
        self.capsules_pos = []
        self.walls_pos = []

    def map_size(self,state):
        """Get the maximum of row and column of layout by api.

        Parameter:
        state: the state of pacman.

        Returns a tuple of row and column.
        """
        corners = zip(*(api.corners(state)))
        return max(corners[0]), max(corners[1])
    
    def map_update(self,state):
        """Update each coordinate of the map once the pacman moved.

        Returns the map with updated value.
        """
        # Get the new information from current state of pacman
        pacman = api.whereAmI(state)  
        food = api.food(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        ghosts = api.ghosts(state)
 

        if pacman not in self.visited_pos:
            self.visited_pos.append(pacman)

        for i in food:
			if i not in self.food_pos:
				self.food_pos.append(i)

        for i in walls:
            if i not in self.walls_pos:
                self.walls_pos.append(i)

        for i in capsules:
            if i not in self.capsules_pos:
                self.capsules_pos.append(i)


        # make a dictionary and give a reward value
        food_map = dict.fromkeys(self.food_pos, 5)
        capsules_map = dict.fromkeys(self.capsules_pos, 5)
        walls_map = dict.fromkeys(self.walls_pos, -5)

        # make a dictionary to store these three together to get a complete map
        value_map = {}
        value_map.update(food_map)
        value_map.update(capsules_map)
        value_map.update(walls_map)

        # Set any other coordinate to 0
        edge = self.map_size(state)
        for i in range(edge[0]):
            for j in range(edge[1]):
                if (i,j) not in value_map.keys():
                    value_map[(i,j)] = 0

        # update value of the dictionary key

        # if food_pos was visited, update the coordinate with 0
        for i in self.food_pos:
            if i in self.visited_pos:
                value_map[i] = 0

        # If  capsules_position was visited, update the coordinate with 0
        for i in self.capsules_pos:
            if i in self.visited_pos:
                value_map[i] = 0

        # Set the coordinate of ghosts to -100
        if ghosts:
            for g in ghosts:
                value_map[(round(g[0]),round(g[1]))] = -100

        return value_map

    def value_iteration(self, state, map, map_type):
        """This function uses Bellman equation to iterate.

        Parameters:
        map: the value map.
        map_type: smallGrid or mediumClassic.

        Returns the value map after iterating by Bellman equation.
        """
        # Parameters of Bellman equation
        reward = -1     # the immediate reward
        gamma = 0.8     # the discount parameter

        # Get the current information(local parameter) in this function
        ghosts = api.ghosts(state)
        food = api.food(state)
        capsules = api.capsules(state)
        walls = api.walls(state)

        """Create a list store coordinates that near the ghost whithin 3 steps in smallGrid and 5 steps in mediumClass.
        The coordinates stored in the list need to be updated by Bellman equation.
        """
        near_ghost = []
            
        """Set a nagtive value to the near ghost coordinates to make pacman stay away from the areas. 
        The value is -10 * (6-distance) for mediumClass when ghosts within 3 steps and -15 * (3-distance) for smallGrid when ghosts within 2 steps.
        """
        # mediumClass
        if map_type=='mediumClass':
            for g in ghosts:
                g_int = (round(g[0]),round(g[1]))
                """Does the value updated is a wall?  0-No, 1-Yes.
                If there is a wall between the pacman and ghost,the value will not be set if the pacman is at the other side of the wall.
                walls_flag indices: 0-east, 1-west, 2-north, 3-south, 4-northeast, 5-northwest, 6-southeast, 7-southwest
                """
                walls_flag = [0,0,0,0,0,0,0,0]

                for i in range(5):
                    # east
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]))
                    # set a negative value
                    if i <=3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i)  
                        if near_ghost_position in walls:
                            walls_flag[0] = 1

                    # west
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i)
                        if near_ghost_position in walls:
                            walls_flag[1] = 1

                    # north
                    near_ghost_position = (int(g_int[0]), int(g_int[1]+i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[2] = 1

                    # south
                    near_ghost_position = (int(g_int[0]), int(g_int[1]-i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[3] = 1

                    # northeast
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]+i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[4] = 1

                    # northwest
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]+i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[5] = 1

                    # southeast
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]-i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and (near_ghost_position) not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[6] = 1

                    # southwest
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]-i))
                    # set a negative value
                    if i <= 3 and near_ghost_position not in walls and (near_ghost_position) not in ghosts and near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        map[near_ghost_position] = -10 * (6-i) 
                        if near_ghost_position in walls:
                            walls_flag[7] = 1

                    # Other coordinates need to be updated
                    for j in range(5):
                        near_ghost_position = (int(g_int[0]+i), int(g_int[1]+j))
                        if near_ghost_position not in near_ghost and walls_flag[0] == 0:
                            near_ghost.append(near_ghost_position)    
                        near_ghost_position = (int(g_int[0]+i), int(g_int[1]-j))
                        if near_ghost_position not in near_ghost and walls_flag[0] == 0:
                            near_ghost.append(near_ghost_position)
                        near_ghost_position = (int(g_int[0]-i), int(g_int[1]+j))
                        if near_ghost_position not in near_ghost and walls_flag[0] == 0:
                            near_ghost.append(near_ghost_position)
                        near_ghost_position = (int(g_int[0]-i), int(g_int[1]-j))
                        if near_ghost_position not in near_ghost and walls_flag[0] == 0:
                            near_ghost.append(near_ghost_position)

        # For smallGrid
        else:
            for g in ghosts:
                g_int = (round(g[0]),round(g[1]))
                walls_flag = [0,0,0,0,0,0,0,0]      
                for i in range(3):
                    # east
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]))
                    if near_ghost_position not in near_ghost and walls_flag[0] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <=3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10 * (3-i)  
                        if near_ghost_position in walls:
                            walls_flag[0] = 1

                    # west
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]))
                    if near_ghost_position not in near_ghost and walls_flag[1] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10 * (3-i)
                        if near_ghost_position in walls:
                            walls_flag[1] = 1

                    # north
                    near_ghost_position = (int(g_int[0]), int(g_int[1]+i))
                    if near_ghost_position not in near_ghost and walls_flag[2] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10*(3-i) 
                        if near_ghost_position in walls:
                            walls_flag[2] = 1
                    # west
                    near_ghost_position = (int(g_int[0]), int(g_int[1]-i))
                    if near_ghost_position not in near_ghost and walls_flag[3] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10 * (3-i) 
                        if near_ghost_position in walls:
                            walls_flag[3] = 1

                    # northeast
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]+i))
                    if near_ghost_position not in near_ghost and walls_flag[4] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10 * (3-i) 
                        if near_ghost_position in walls:
                            walls_flag[4] = 1

                    # northwest
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]+i))
                    if near_ghost_position not in near_ghost and walls_flag[5] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and near_ghost_position not in ghosts:
                            map[near_ghost_position] = -10 * (3-i) 
                        if near_ghost_position in walls:
                            walls_flag[5] = 1

                    # southeast
                    near_ghost_position = (int(g_int[0]+i), int(g_int[1]-i))
                    if near_ghost_position not in near_ghost and walls_flag[6] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and (near_ghost_position) not in ghosts:
                            map[near_ghost_position] = -10 * (3-i) 
                        if near_ghost_position in walls:
                            walls_flag[6] = 1

                    # southwest
                    near_ghost_position = (int(g_int[0]-i), int(g_int[1]-i))
                    if near_ghost_position not in near_ghost and walls_flag[7] == 0:
                        near_ghost.append(near_ghost_position)
                        # set a negative value
                        if i <= 3 and near_ghost_position not in walls and (near_ghost_position) not in ghosts:
                            map[near_ghost_position] = -10 * (3-i) 
                        if near_ghost_position in walls:
                            walls_flag[7] = 1   
            
        # If there is food not near the ghost. The coordinates are no need to be updated.
        not_near_ghost = []
        for f in food:
            if f not in near_ghost:
                not_near_ghost.append(f)

        # Iteration times for mediumClass is 40 and for smallGrid is 20.
        if map_type=='mediumClass':
            loops = 40
        else:
            loops = 20

        edge = self.map_size(state)
        while loops > 0:
            temp_map = map   
            # avoid the coordinate out of map range
            for i in range(edge[0]):
                for j in range(edge[1]):
                    # Iterate the value map by Bellman equation if needed
                    if (i,j) not in walls and (i,j) not in not_near_ghost and (i,j) not in ghosts and (i,j) not in capsules:
                        utilities = self.calculate_utilities((i,j),temp_map)
                        # Take the maximum utility of four directions as the utility at (i,j)
                        map[(i,j)] = reward + gamma * max(utilities.values())
            loops -= 1
        return map



    def calculate_utilities(self, position, map):
        """This function is used to calaulate the utilities of four directions.

        Parameters:
        pos: the positon of pacman.
        map: the value map.

        Returns the utilities of four directions.
        """

        # Initial utilities of four directions
        utilities = {"north_u": 0.0, "south_u": 0.0, "east_u": 0.0, "west_u": 0.0}

        # Flag the grids to each direction of pacman
        north = (position[0],position[1]+1)
        south = (position[0],position[1]-1)
        west = (position[0]-1,position[1])
        east = (position[0]+1,position[1])
        stay = position


        # The motion of model is non-deterministic, pacman has a probablity of 0.1 that move to perpendicular direction and in order to avoid ghost
        # Expectaion of utilities = 0.7 * (value of Grid to pacman's intended direction) + 0.1 * (perpendicular) + 0.1 * (perpendicular) + 0.1 * (back)

        # North
        if map[north] != -5:
            north_u = (0.7 * map[north])
        else:
            north_u = (0.7 * map[stay])
        if map[east] != -5:
            north_u += (0.1 * map[east])
        else:
            north_u += (0.1 * map[stay])
        if map[west] != -5:
            north_u += (0.1 * map[west])
        else:
            north_u += (0.1 * map[stay])
        if map[south] != -5:
            north_u += (0.1 * map[south])
        else:
            north_u += (0.1 * map[stay])
        utilities["north_u"] = north_u

        # South
        if map[south] != -5:
            south_u = (0.7 * map[south])
        else:
            south_u = (0.7 * map[stay])
        if map[east] != -5:
            south_u += (0.1 * map[east])
        else:
            south_u += (0.1 * map[stay])
        if map[west] != -5:
            south_u += (0.1 * map[west])
        else:
            south_u += (0.1 * map[stay])
        if map[north] != -5:
            south_u += (0.1 * map[north])
        else:
            south_u += (0.1 * map[stay])
        utilities["south_u"] = south_u

        # East
        if map[east] != -5:
            east_u = (0.7 * map[east])
        else:
            east_u = (0.7 * map[stay])
        if map[north] != -5:
            east_u += (0.1 * map[north])
        else:
            east_u += (0.1 * map[stay])
        if map[south] != -5:
            east_u += (0.1 * map[south])
        else:
            east_u += (0.1 * map[stay])
        if map[west] != -5:
            east_u += (0.1 * map[west])
        else:
            east_u += (0.1 * map[stay])
        utilities["east_u"] = east_u

        # West
        if map[west] != -5:
            west_u = (0.7 * map[west])
        else:
            west_u = (0.7 * map[stay])
        if map[north] != -5:
            west_u += (0.1 * map[north])
        else:
            west_u += (0.1 * map[stay])
        if map[south] != -5:
            west_u += (0.1 * map[south])
        else:
            west_u += (0.1 * map[stay])
        if map[east] != -5:
            west_u += (0.1 * map[east])
        else:
            west_u += (0.1 * map[stay])
        utilities["west_u"] = west_u

        return utilities

    def where_to_move(self, state, map):
        """Calculate the maximum expected utility to make decision of where to move.

        Parameters:
        state: the state of pacman.
        map: the value map.

        Returns the direction of move.
        """
        pacman = api.whereAmI(state)

        # Update utilities of pacman current postion
        utilities = self.calculate_utilities(pacman, map)    

        # Get the e maximum expected utility and store values & keys in dictionary
        move_decision = max(zip(utilities.values(),utilities.keys()))
        
        # Return the direction of move
        if move_decision[1] == 'north_u':
            return Directions.NORTH
        if move_decision[1] == 'south_u':
            return Directions.SOUTH
        if move_decision[1] == 'west_u':
            return Directions.WEST
        if move_decision[1] == 'east_u':
            return Directions.EAST
        
    def getAction(self, state):
        """ This function is used to make pacman move.

        Parameter:
        state: the state of pacman.

        Returns the move of pacman.
        """

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # Get the size of layout
        rows,columns = self.map_size(state) 

        # Judge the map_type is mediumClass or smallGrid
        map_type = 'mediumClass'
        if rows >= 10 and columns >= 10:   
            map_type = 'mediumClass'
        else:
            map_type = 'smallGrid'

        # Update the value map once pacman moved
        value_map = self.map_update(state)

        # Update the value map with value_iteration
        value_map = self.value_iteration(state, value_map, map_type)
    
        # Make move
        return api.makeMove(self.where_to_move(state,value_map), legal)
