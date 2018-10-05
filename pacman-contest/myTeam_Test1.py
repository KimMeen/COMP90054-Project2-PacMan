#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:36:49 2018

@author: kimmeen
"""


"""
老哥们，开始前，必须说明这个myTeam_Test1以及baselineTeam是为了给大家思路
它完全来着GitHub，咱们就算采取类似的思路也要换个写法
先看一下这个方法的大概思路：

Our approach:

- 1 attacker, 1 defender
- The Attacker takes 4 enemy pellets and then return gain score
- The Defender guards the power pellet
- If we have score advantage, the Attacker switches to defense mode.

"""

import random

import util
from captureAgents import CaptureAgent
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

team = []
START = 0
ATTACK = 1
DEFEND = 2
RETREAT = 3

MIN_VALID_SCORE = 6
MAX_CARRY_VAL = 3
ENEMY_MAX_CARRY = 4


class ReflexCaptureAgent(CaptureAgent):
    MAP_WIDTH = 32
    MAP_HEIGHT = 16

    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing)
        team.append(self)
        
        if self.index % 2 == 0:
            self.isRed = True
            self.middle = (ReflexCaptureAgent.MAP_WIDTH / 4, ReflexCaptureAgent.MAP_HEIGHT / 2)
        else:
            self.isRed = False
            self.middle = (ReflexCaptureAgent.MAP_WIDTH * 3 / 4), (ReflexCaptureAgent.MAP_HEIGHT / 2)


    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 20:
            bestDist = 1000
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}

    def getScoreDifference(self, gameState):
        enemyFood = self.getFood(gameState)
        myFood = self.getFoodYouAreDefending(gameState)
        return len(myFood.asList()) - len(enemyFood.asList())

    def isPacman(self, gameState):
        myState = gameState.getAgentState(self.index)
        return myState.isPacman

    @staticmethod
    def getRemainingScareTime(gameState, agentIndex):
        return gameState.getAgentState(agentIndex).scaredTimer
  
    def getMaxScareTime(self, gameState):
        opponents = self.getOpponents(gameState)
        maxScareTime = 0
        for opponent in opponents:
            scareTime = gameState.getAgentState(opponent).scaredTimer
            if scareTime > maxScareTime:
                maxScareTime = scareTime
        return maxScareTime
  
    def getEnemies(self, gameState):
        enemies = []
        for j in team:
            for i in j.getOpponents(gameState):
                newEnemy = gameState.getAgentState(i)
                newEnemy.agentIndex = i
                if newEnemy not in enemies:
                    myPos = newEnemy.getPosition()
                    if myPos is not None:
                        enemies.append(newEnemy)
        return enemies
  
    def getMaxEnemyCarry(self, gameState):
        maxNumCarring = 0
        enemies = self.getEnemies(gameState)
        for enemy in enemies:
            numCarrying = enemy.numCarrying
            if numCarrying > maxNumCarring:
                maxNumCarring = numCarrying
        return maxNumCarring


class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).
        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)
        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)
        '''
        You should change this in your own agent.
        '''
        return random.choice(actions)

class OffensiveReflexAgent(ReflexCaptureAgent):

    def __init__(self, index, timeForComputing=.1):
        """
        Lists several variables you can query:
        self.index = index for this agent
        self.red = true if you're on the red team, false otherwise
        self.agentsOnTeam = a list of agent objects that make up your team
        self.distancer = distance calculator (contest code provides this)
        self.observationHistory = list of GameState objects that correspond
            to the sequential order of states that have occurred so far this game
        self.timeForComputing = an amount of time to give each turn for computing maze distances
            (part of the provided distance calculator)
        """
        # Agent index for querying state
        ReflexCaptureAgent.__init__(self, index, timeForComputing)

        self.enemyFoodOfLastState = 0        # number of enemy food of previous gameState
        self.unofficialScore = 0
        self.lastScore = -1
        self.myState = START

    def getFeatures(self, gameState, action):

        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        score = self.getScoreDifference(gameState)  # My defined score
        officialScore = self.getScore(gameState)  # Getting official score

        if officialScore > self.lastScore:
            self.lastScore = officialScore
            self.unofficialScore = 0
        
        def removeItemsNearerToEnemy(itemList, my_pos):
            for item in itemList:
                for opponent in enemies:
                    oppPos = opponent.getPosition()
                    scareTime = self.getRemainingScareTime(gameState, opponent.agentIndex)
                    if oppPos is not None and not opponent.isPacman and scareTime == 0:
                        if self.getMazeDistance(oppPos, item) < self.getMazeDistance(my_pos, item):
                            itemList.remove(item)
                            break
            return itemList
        
        enemyFoodRemaining = len(self.getFood(gameState).asList())
        
        # Updates unofficial score when we eat new pellet
        if enemyFoodRemaining < self.enemyFoodOfLastState:  
            self.unofficialScore += self.enemyFoodOfLastState - enemyFoodRemaining
            self.enemyFoodOfLastState = enemyFoodRemaining            
        elif enemyFoodRemaining > self.enemyFoodOfLastState:  # our Pacman has been killed by enemies
            self.unofficialScore = 0
            self.enemyFoodOfLastState = enemyFoodRemaining
            self.myState = START
            self.lastScore = -1

        if self.myState == START:              # start mode
            if officialScore > MIN_VALID_SCORE:  # if we are winning by specific point
                self.myState = DEFEND            # switch to defense mode
            else:
                maxNumCarring = self.getMaxEnemyCarry(gameState)      
                if maxNumCarring > ENEMY_MAX_CARRY: # if enemy have eaten more than specific point
                    self.myState = DEFEND           # switch to defense mode
                else:
                    self.myState = ATTACK           
        elif self.myState == ATTACK:          # attack mode
            maxScareTime = self.getMaxScareTime(gameState)         
            if not self.isPacman(gameState):
                maxNumCarring = self.getMaxEnemyCarry(gameState)
                if maxNumCarring > ENEMY_MAX_CARRY:
                    self.myState = DEFEND
            elif (self.unofficialScore < MAX_CARRY_VAL and maxScareTime == 0) \
                    or (self.unofficialScore < MAX_CARRY_VAL * 2 and maxScareTime > 0):
                self.myState = ATTACK
            else:
                self.myState = RETREAT
        elif self.myState == RETREAT:        # retreat mode
            if self.isPacman(gameState):     # set to retreat when agent is Pacman
                self.myState = RETREAT       # if not, Pacman  continue to attack until there is no food
            else:
                self.unofficialScore = 0
                if officialScore > MIN_VALID_SCORE:  #defend when we are winning
                    self.myState = DEFEND
                else:
                    maxNumCarring = self.getMaxEnemyCarry(gameState)
                    if maxNumCarring > ENEMY_MAX_CARRY:
                        self.myState = DEFEND
                    else:
                        self.myState = ATTACK
        elif self.myState == DEFEND:            # defense mode
            if officialScore > MIN_VALID_SCORE:
                self.myState = DEFEND
            else:
                if officialScore > MIN_VALID_SCORE:
                    self.myState = DEFEND
                else:
                    maxNumCarring = self.getMaxEnemyCarry(gameState)
                    if maxNumCarring > ENEMY_MAX_CARRY:
                        self.myState = DEFEND
                    else:
                        self.myState = ATTACK

        enemies = self.getEnemies(successor)

        if self.myState == DEFEND:
            features['onDefense'] = 1
            myState = successor.getAgentState(self.index)
            myPos = myState.getPosition()
            if myState.isPacman:
                features['onDefense'] = 0
                features['isPacman'] = 1
                
            # Computes distance to invaders we can see
            invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
            features['numInvaders'] = len(invaders)
            if len(invaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)

            if action == Directions.STOP:
                features['stop'] = 1
            rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
            if action == rev:
                features['reverse'] = 1

            myPos = successor.getAgentState(self.index).getPosition()
            foodList = self.getFoodYouAreDefending(successor).asList()
            capsuleList = self.getCapsulesYouAreDefending(successor)
            foodToDefend = foodList + capsuleList
            minEnemyDist = 1000
            nearestEnemy = None

            for enemy in enemies:
                if enemy.getPosition() is not None:
                    if self.getMazeDistance(myPos, enemy.getPosition()) < minEnemyDist and enemy.isPacman:
                        minEnemyDist = self.getMazeDistance(myPos, enemy.getPosition())
                        nearestEnemy = enemy

            if nearestEnemy is None:
                for enemy in enemies:
                    if enemy.getPosition() is not None:
                        if self.getMazeDistance(myPos, enemy.getPosition()) < minEnemyDist:
                            minEnemyDist = self.getMazeDistance(myPos, enemy.getPosition())
                            nearestEnemy = enemy
                features['stop'] = 1
                enemyFood = self.getFood(gameState).asList()
                minDistance = min([self.getMazeDistance(myPos, enemyfood) for enemyfood in enemyFood])
                features['nearestFoodToDefend'] = -minDistance
            else:
                minFoodToEnemy = 1000
                nearestFoodtoEnemy = None
                for food in foodToDefend:
                    if self.getMazeDistance(food, nearestEnemy.getPosition()) < minFoodToEnemy:
                        minFoodToEnemy = self.getMazeDistance(food, nearestEnemy.getPosition())
                        nearestFoodtoEnemy = food
                if nearestFoodtoEnemy is not None:
                    features['nearestFoodToDefend'] = -self.getMazeDistance(myPos, nearestFoodtoEnemy)
                else:
                    features['nearestFoodToDefend'] = 0
        elif self.myState == RETREAT:
            foodList = self.getFoodYouAreDefending(successor).asList()
            features['successorScore'] = -len(foodList)
            myPos = successor.getAgentState(self.index).getPosition()
            features['distanceToFood'] = 1000
            features['distanceToCapsule'] = 1000

            if len(foodList) > 0:
                foodList = removeItemsNearerToEnemy(foodList, myPos)
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

            capsuleList = self.getCapsules(successor)

            if len(capsuleList) > 0:
                capsuleList = removeItemsNearerToEnemy(foodList, myPos)
                minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
                features['distanceToCapsule'] = minDistance


        elif self.myState == ATTACK:
            features['distanceToCapsule'] = 1000
            features['distanceToFood'] = 1000
            foodList = self.getFood(successor).asList()
            features['successorScore'] = -len(foodList)
            capsuleList = self.getCapsules(gameState)
            
            # Compute distance to the nearest food
            myPos = successor.getAgentState(self.index).getPosition()

            if len(foodList) > 0:  # This should always be True, but better safe than sorry
                foodList = removeItemsNearerToEnemy(foodList, myPos)
    
            if len(foodList) > 0:
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

            if len(capsuleList) > 0:
                capsuleList = removeItemsNearerToEnemy(capsuleList, myPos)

            if len(capsuleList) > 0:
                features['distanceToCapsule'] = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])

            if features['distanceToCapsule'] == 1000 and features['distanceToFood'] == 1000:
                self.myState = RETREAT

        return features


    def getWeights(self, gameState, action):
        if self.myState == DEFEND:            
            return {
                'numInvaders': 0, 
                'onDefense': 0, 
                'invaderDistance': 10, 
                'stop': 0, 
                'reverse': 0,
                'nearestFoodToDefend': 1000, 
                'isPacman': -10000
            }

        if self.myState == ATTACK:
            return {'successorScore': 100, 'distanceToFood': -1, 'distanceToCapsule': -1}

        return {'successorScore': 100, 'distanceToFood': -1, 'distanceToCapsule': -1}

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
        
        # You can profile your evaluation time by uncommenting these lines        
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        return random.choice(bestActions)

class DefensiveReflexAgent(ReflexCaptureAgent):
    
    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)
        
    def getFeatures(self, gameState, action):
        
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman:
            features['onDefense'] = 0
        
        
        
        # Computes distance to invaders we can see
        enemies = self.getEnemies(gameState)
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)
        features['enemyDistance'] = 1000
        enemyIsUnknown = True
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
            enemyIsUnknown = False
        else:
            minDist = 1000
            currentEnemies = self.getEnemies(gameState)
            for enemy in currentEnemies:
                enemyPos = enemy.getPosition()
                if enemyPos is not None:
                    enemyIsUnknown = False
                    newDist = self.getMazeDistance(myPos, enemyPos)
                    if newDist < minDist:
                        minDist = newDist
            features['enemyDistance'] = minDist

        if enemyIsUnknown is True:
            myPos = successor.getAgentState(self.index).getPosition()
            capsuleList = self.getCapsulesYouAreDefending(successor)
            foodList = self.getFoodYouAreDefending(successor).asList()
            minDist = 0
            if len(capsuleList) > 0:
                for capsule in capsuleList:
                    dist = self.getMazeDistance(capsule, myPos)
                    minDist += dist
                minDist /= len(capsuleList)
            else:
                for food in foodList:
                    dist = self.getMazeDistance(food, myPos)
                    minDist += dist
                minDist /= len(foodList)
                
            features['enemyDistance'] = minDist


        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 0

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 100,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2,
            'enemyDistance': -10
        }