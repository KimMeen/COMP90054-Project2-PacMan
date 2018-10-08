# # myTeam.py
# # ---------
# # Licensing Information:  You are free to use or extend these projects for
# # educational purposes provided that (1) you do not distribute or publish
# # solutions, (2) you retain this notice, and (3) you provide clear
# # attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# #
# # Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# # The core projects and autograders were primarily created by John DeNero
# # (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# # Student side autograding was added by Brad Miller, Nick Hay, and
# # Pieter Abbeel (pabbeel@cs.berkeley.edu).

#Team:Farseer
#Author : Ziling Zhou 802414
#         Yuqing He 744973
#         Kuailun Zhang 743669
from captureAgents import CaptureAgent
from baselineTeam import ReflexCaptureAgent
import random, time, util
from game import Directions
from util import nearestPoint
import copy



#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='Defender', second='AStarAgent'):
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



class Defender(CaptureAgent):


    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.distancer.getMazeDistances()
        self.targetPosition = None
        self.lastObservedFood = None
        self.probDict = {}
        self.mapwidth = gameState.data.layout.width
        self.mapheight = gameState.data.layout.height



        if self.red:
            midX = (self.mapwidth - 2)/2
        else:
            midX = ((self.mapwidth - 2)/2) + 1
        self.noWall = []
        for i in range(0, self.mapheight):
            if not gameState.hasWall(midX, i):
                self.noWall.append((midX, i))

        while len(self.noWall) > (self.mapheight -2)/2:
            self.noWall.pop(0)
            self.noWall.pop(len(self.noWall)-1)

        self.pacmanrun(gameState)


    def chooseAction(self, gameState):

        isEaten = False

        mypos = gameState.getAgentPosition(self.index)
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]

        enemy_Pos = []
        distoenemy = 99999
        for enemy in enemies:
            if enemy.isPacman and enemy.getPosition() != None:
                enemy_Pos.append(enemy)
                if distoenemy > self.getMazeDistance(mypos, enemy.getPosition()):
                    distoenemy = self.getMazeDistance(mypos, enemy.getPosition())

        if self.lastObservedFood and len(self.lastObservedFood) != len(self.getFoodYouAreDefending(gameState).asList()):
            self.pacmanrun(gameState)

        if mypos == self.targetPosition:
            self.targetPosition = None

        if len(enemy_Pos) > 0:
            positions = [agent.getPosition() for agent in enemy_Pos]
            self.targetPosition = min(positions, key = lambda x: self.getMazeDistance(mypos, x))

        elif self.lastObservedFood != None:
            eaten = set(self.lastObservedFood) - set(self.getFoodYouAreDefending(gameState).asList())
            if len(eaten) > 0:
                self.targetPosition = eaten.pop()
                isEaten = True

        self.lastObservedFood = self.getFoodYouAreDefending(gameState).asList()

        if self.targetPosition == None and len(self.getFoodYouAreDefending(gameState).asList()) <= 4:
            food = self.getFoodYouAreDefending(gameState).asList() + self.getCapsulesYouAreDefending(gameState)
            if food == []:
                self.targetPosition = random.choice(self.noWall)
            else:
                self.targetPosition = random.choice(food)

        elif self.targetPosition == None:
            randnum = random.random()
            sum = 0.0
            for x in self.probDict.keys():
                sum += self.probDict[x]
                if randnum < sum:
                    self.targetPosition = x

        actions = gameState.getLegalActions(self.index)
        actions.remove('Stop')
        electActions = []
        values = []
        for a in actions:
            new_state = gameState.generateSuccessor(self.index, a)
            if not new_state.getAgentState(self.index).isPacman:
                if isEaten:
                  laststate = self.getPreviousObservation()
                  lastpos = laststate.getAgentPosition(self.index)
                  newpos = new_state.getAgentPosition(self.index)
                  # print "The position is " +str(lastpos) + "  "+ str(newpos)
                  if lastpos != newpos:
                    electActions.append(a)
                    values.append(self.getMazeDistance(newpos, self.targetPosition))
                  else:
                    mustReverse = a
                else:
                    newpos = new_state.getAgentPosition(self.index)
                    electActions.append(a)
                    values.append(self.getMazeDistance(newpos, self.targetPosition))
        if len(electActions)==0:
            electActions.append(mustReverse)
            values.append("0")

        best = min(values)
        newAction = filter(lambda x: x[0] == best, zip(values, electActions))
        choiceaction = random.choice(newAction)[1]

        return choiceaction


    def getSuccessor(self, gameState, action):

        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def pacmanrun(self, gameState):

        food = self.getFoodYouAreDefending(gameState).asList()
        total = 0

        for position in self.noWall:
            closestFoodDist = 999999
            for foodPos in food:
                distancetofood = self.getMazeDistance(position, foodPos)
                if distancetofood < closestFoodDist:
                    closestFoodDist = distancetofood
            if closestFoodDist == 0:
                closestFoodDist = 1
            self.probDict[position] = 1.0 / float(closestFoodDist)
            total += self.probDict[position]
        if total == 0:
            total = 1
        for x in self.probDict.keys():
            self.probDict[x] = float(self.probDict[x]) / float(total)


class AStarAgent(ReflexCaptureAgent):
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

        self.walls = gameState.getWalls()
        self.width = self.walls.width
        self.height = self.walls.height
        # print gameState
        # print self.getFood(gameState)
        # print self.getFood(gameState).asList()
        # print "width", self.width
        # print "heigth", self.height
        # exit(0)
        self.hasFood = 0
        self.lastAction = None
        self.lastState = None
        self.capsules = self.getCapsules(gameState)
        self.isSuper = False
        # print self.capsules
        #record whether the pacman is going back home
        self.isGoingHome = False
        #record whether the pacman is getting the capsule
        self.isGettingCapsule = False

        # Index of enemies and team
        self.enemyIndex = self.getOpponents(gameState)
        self.teamIndex = self.getTeam(gameState)

    def chooseAction(self, gameState):
        #Check the situation
        # print "scare", gameState.getAgentState(self.enemyIndex[0]).scaredTimer
        if not self.isGettingCapsule and not self.isGoingHome:
          hasEnemy = False

          for enemy in self.enemyIndex:

            enemyLoc = gameState.getAgentPosition(enemy)
            if not enemyLoc == None:
                distanceToMe = self.getMazeDistance(enemyLoc,gameState.getAgentPosition(self.index))

                teammate = copy.copy(self.teamIndex)
                teammate.remove(self.index)
                distanceToTeam = self.getMazeDistance(enemyLoc,gameState.getAgentPosition(teammate[0]))

                if not distanceToMe > distanceToTeam:
                   hasEnemy = True
          #when Enemy is founded, decide the go back or get capsule
          if hasEnemy and self.hasFood > 0:
              # print "start to go home"
              self.isGoingHome = True
        
        if not self.lastState == None:
            if gameState.getAgentPosition(self.index) in self.getFood(self.lastState).asList():
                self.hasFood += 1
                # print self.hasFood
            elif self.getMazeDistance(gameState.getAgentPosition(self.index),
                                      self.lastState.getAgentPosition(self.index)) > 5:
                # print "YOU Agent is been eaten!"
                self.isGoingHome = False
                self.hasFood = 0
            else:
                if self.atHome(gameState.getAgentPosition(self.index)):
                  # if not self.atHome(self.lastState.getAgentPosition(self.index)):
                  #   print "Your Agent get back home!"
                  if self.hasFood > 0:
                    # print "your Agent takes food to home"
                    self.hasFood = 0
                  self.isGoingHome = False

        if gameState.getAgentPosition(self.index) in self.capsules:
          # print "Agent get Capsule!"
          self.isGettingCapsule = False
          self.isGettingHome = False
          self.isSuper = True
          self.capsules.remove(gameState.getAgentPosition(self.index))

        if self.isSuper:
            self.isGoingHome = False
            goOn = True
            for enemy in self.enemyIndex:
                if gameState.getAgentState(self.enemyIndex[0]).scaredTimer <8:
                    goOn = False
            if not goOn:
                # print "Stop super, go home"
                self.isSuper =False
                self.isGoingHome = True

        action = self.aStarSearch(gameState)[0]
        self.lastAction = action
        self.lastState = gameState


        # print action
        return action

    def getCost(self,gamestate,location, action):
        if self.red:
          if location[0] < self.width/2-1:
            return 0
        else  :
          if location[0] > self.width/2:
            return 0 
        next_location = self.move(location,action)
        cost = 0
        for enemy in self.enemyIndex:
            if not gamestate.getAgentPosition(enemy) == None:
                enemyLoc = gamestate.getAgentPosition(enemy)
                if self.atHome(location):
                  difference =0
                else:
                  difference = max(self.getMazeDistance(location, enemyLoc)-self.getMazeDistance(next_location, enemyLoc),0)
                # print location, next_location, enemyLoc, self.getMazeDistance(next_location, enemyLoc)
                distance = self.getMazeDistance(next_location, enemyLoc)
                if distance == 0:
                  cost += difference* 200
                else:
                  cost += difference* 200 /distance

                # print "cost", enemyLoc,location,next_location
        return cost

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor


    def getFoodHeuristic(self, location, foodGrid):
        max = 0
        for food in foodGrid.asList():
            distance = self.getMazeDistance(location, food)
            if distance > max:
                max = distance

        return max
    # Huristic function that is used when the Agent is geting home
    def getHomeHeuristic(self,location):
        if self.red:
          midX = int(self.width/2-1)
        else:
          midX = int(self.width/2)

        yaxis = range(0, self.height)

        ywall = []
        # check for walls and record them
        for y in yaxis:
          if self.walls[midX][y]:
            ywall.append(y)
        # remove walls from yaxis
        for y in ywall:
          yaxis.remove(y)

        minDistance = 1000
        for y in yaxis:
          distance = self.getMazeDistance(location, (midX, y))
          if distance < minDistance:
            minDistance = distance

        return minDistance

    def atHome(self,location):
        if self.red:
          if location[0] < self.width/2:
            return True
          else:
            return False
        else  :
          if location[0] > self.width/2-1:
            return True
          else:
            return False   


    def getHeuristic(self,location,foods):
      if self.isGoingHome:
        return self.getHomeHeuristic(location)
      else:
        return self.getFoodHeuristic(location,foods)



    def aStarSearch(self, gameState):
        """Search the node that has the lowest combined cost and heuristic first."""
        "*** YOUR CODE HERE ***"
        foods = self.getFood(gameState)
        actions = ['North','South','West','East']
        # print goal,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        currentLoc = gameState.getAgentPosition(self.index)
        foods = self.getFood(gameState)
        open = util.PriorityQueue()
        """use visited dictionary to re-open"""
        visited = dict()

        n1 = SearchNode(currentLoc, self.getHeuristic(currentLoc, foods), 0, [], None)
        open.push(n1, n1.cost)
        visited[currentLoc] = 0
        while True:
            if open.isEmpty():
                # print "aStar error", gameState.getLegalActions(self.index)
                return [random.choice(gameState.getLegalActions(self.index))]
            
            node = open.pop()
            # print node.state
            # print "check node", node.state
            if (node.state in foods.asList() and not self.isGoingHome) or (
              self.red and node.state[0] < self.width / 2 and currentLoc[0] > self.width / 2-1 and self.hasFood > 0 and self.isGoingHome) or (
              not self.red and node.state[0] > self.width / 2-1 and currentLoc[0] < self.width /2 and self.hasFood > 0 and self.isGoingHome)or(
              node.state in self.capsules):
                # print "Goal!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                # print self.isGoingHome
                return node.actions
            else:
                for action in actions:
                    nextLoc = self.move(node.state,action)
                    x,y = nextLoc
                    if self.walls[x][y]:
                        continue

                    cost = self.getCost(gameState,node.state, action)
                    # print "nestlocation", nextLoc, "action",action,"location",node.state
                    successor = (nextLoc, action, 0.5)
                    origin_cost = visited.get(successor[0])
                    new_cost = node.cost + successor[2]+cost
                    # print "EnemyCost", cost
                    if origin_cost is None or origin_cost > new_cost:
                        action_list = copy.copy(node.actions)
                        action_list.append(successor[1])
                        f_value = self.getHeuristic(nextLoc, foods) + new_cost
                        # print self.getHeuristic(nextLoc,foods), new_cost
                        succ_node = SearchNode(successor[0], f_value, new_cost, action_list, node)
                        # print "suc", succ_node.state
                        open.push(succ_node, f_value)
                        visited[successor[0]] = new_cost
                        # print "cost", cost,"fvalue", f_value,"from",node.state[0],"to",nextLoc

    
    def move(self,location,action):
        x,y = location
        if action == 'North':
            return (int(x),int(y)+1)
        elif action =='South':
            return (int(x),int(y)-1)
        elif action == 'West':
            return (int(x)-1,int(y))
        elif action == 'East':
            return (int(x)+1,int(y))
        else:
            return (int(x),int(y))




    # def getQValue(self, state, action):
    #   actionDict = self.qValues[state]
    #   if actionDict ==0:
    #     return 0
    #   return actionDict[action]
    #   print self.qValues

    # def computeValueFromQValues(self, state):
    #   actionDict = self.qValues[state]
    #   if actionDict ==0:
    #     return 0
    #   maxValue = -1000
    #   for value in actionDict.values():
    #     if value >maxValue:
    #       maxValue = value

    #   return maxValue
  
    # def computeActionFromQValues(self,gameState,state):
    #   legalActions = gameState.getLegalActions(self.index)
    #   print "-------------------------",self.index,self.qValues
    #   actionDict = self.qValues[state]
    #   if actionDict == 0:
    #     return None
    #   maxValue = -1000
    #   maxAction = None 
    #   print actionDict.keys()
    #   for key in actionDict.keys():
    #     if key in legalActions:
    #       value = actionDict[key]
    #       if value>maxValue and not value==0:
    #         maxAction = key
    #         maxValue = value
    #         print "Get larger value: ", maxValue," from action ", maxAction 
    #       elif value==maxValue:
    #         maxAction = random.choice([key,maxAction])
    #         print "Randomly choice action when they have same value"

    #   print "------------------------------"
    #   return maxAction

    # # Method used to calculate reward
    # def getReward(self,state,newState):
    #   idX = int(self.width / 2 - 1)
    #   if (newState.getAgentPosition(self.index)[0]<=idX):
    #     self.hasFood = 0

    #     pos = state.getAgentPosition(self.index)
    #     newPos = newState.getAgentPosition(self.index)
    #     #Difference on score
    #     reward = 5*(state.getScore() - newState.getScore())
    #     distance = self.getMazeDistance(pos,newPos)
    #   # If the agent is eatten
    #   if distance > 5: 
    #     reward -= 2*self.hasFood
    #     print "Agent ", self.index," is eatten "
    #   else:
    #     for enemy in self.enemyIndex:
    #       enemy_pos = state.getAgentPosition(enemy)
    #       enemy_pos2 = newState.getAgentPosition(enemy)
    #       # If the pacman eat enemy
    #       if enemy_pos == newPos and not enemy_pos2 == None:
    #         print "Agent ", self.index,"eat opponent ", enemy
    #         reward +=5

    #   if self.getFood(state)[newPos[0]][newPos[1]]:
    #       self.hasFood +=1;
    #       reward += 3
    #   return reward           


    # def getSuccessor(self, gameState, action):
    #   """
    #   Finds the next successor which is a grid position (location tuple).
    #   """
    #   successor = gameState.generateSuccessor(self.index, action)
    #   pos = successor.getAgentState(self.index).getPosition()
    #   if pos != nearestPoint(pos):
    #     # Only half a grid position was covered
    #     return successor.generateSuccessor(self.index, action)
    #   else:
    #     return successor


    # def breadthFirstSearch(self,gameState):
    #   """Search the shallowest nodes in the search tree first."""
    #   open = util.Queue()
    #   """use visited dictionary to re-open"""
    #   visited = dict()
    #   start_state = gameState
    #   n1 = SearchNode(start_state, None, 0, [], None)
    #   open.push(n1)
    #   visited[start_state.getAgentPosition(self.index)] = 0

    #   while True:
    #     if open.isEmpty():
    #       print "BFS ERROR: Empty openlist"
    #       return random.choice(start_state.getLegalActions(self.index))
    #     node = open.pop()
    #     foods = self.getFood(gameState)
    #     position = node.state.getAgentPosition(self.index)
    #     if foods[(int)(position[0])][(int)(position[1])]:
    #       return node.actions
    #     else:
    #       legalActions = node.state.getLegalActions(self.index)
    #       # Avoid Agent from stop
    #       legalActions.remove('Stop')

    #       for successorAction in legalActions:
    #         nextState = self.getSuccessor(node.state,successorAction)
    #         next_location=nextState.getAgentPosition(self.index)
    #         origin_cost = visited.get(nextState.getAgentPosition(self.index))
    #         new_cost = node.cost + 1
    #         if origin_cost is None or origin_cost > new_cost:
    #           action_list = copy.copy(node.actions)
    #           action_list.append(successorAction)
    #           succ_node = SearchNode(nextState, None, new_cost, action_list, node)
    #           open.push(succ_node)
    #           visited[next_location] = new_cost


class SearchNode:
    def __init__(self, state, f_value, cost, actions, parent):
        self.state = state
        self.f_value = f_value
        self.cost = cost
        self.actions = actions
        self.parent = parent







