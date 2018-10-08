#myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util, itertools
from game import Directions, Actions
import game
import math
from util import nearestPoint
import copy
from collections import defaultdict, deque
from pathos import multiprocessing as mp
import sys
import numpy as np
import multiprocessing 
from nodes import StateNode, ActionNode
import gc

#from SimulateAgents import SimulateAgent, SimulateAgentV1
from Helper import Distancer, ParallelAgent, SimulateAgent, SimulateAgentV1
from BasicNode import BasicNode, ReplaceNode
global StateRootNode
StateRootNode = None
global AgentBestAction
AgentBestAction = None

#import copy_reg
#import types
#################
# Team creation #
#################
"""
def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):
        cls_name = cls.__name__.lstrip('_')
    if cls_name: 
        func_name = '_' + cls_name + func_name

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    print func_name, obj, cls
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
        return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
"""

def createTeam(firstIndex, secondIndex, isRed,
               first = 'MCTSCaptureAgent', second = 'MCTSCaptureAgent'):
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
    #return [eval(first)(firstIndex), eval(second)(secondIndex)]
    return [eval(first)( firstIndex ), eval(second)( secondIndex ) ]

##########
# Agents #
##########

class MCTSCaptureAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.allies = self.getTeam( gameState )
        #if self.allies[0] != self.index:
        #    self.allies = self.allies[::-1]
        self.enemies = self.getOpponents( gameState )
        print self.allies, self.enemies
        self.MCTS_ITERATION = 10000
        self.ROLLOUT_DEPTH = 25
        self.LastRootNode = None
        self.M = 4
        self.count = 0 
        self.D = Distancer( gameState.data.layout )
        self.PositionDict = self.D.positions_dict
        self.getMazeDistance = self.D.getDistancer
       
        self.mgr = multiprocessing.Manager()
        self.PositionDictManager = self.mgr.dict()
        for k1 in self.PositionDict.keys():
            self.PositionDictManager[k1] = self.PositionDict[k1]
            #for k2 in self.PositionDict[k1].keys():
            #    val = self.PositionDict[k1][k2]
            #    PositionDictManager[k1][k2] = val
        
        #print "set Parallel"
        #print "simulate",self.PositionDict[(1.0,3.0)][(17,6)],self.PositionDictManager[(1.0,3.0)][(17,6)]
        #print type(self.PositionDict), type(self.PositionDictManager)
        #raise Exception
        self.ChildParallelAgent = ParallelAgent( self.allies, self.enemies, self.ROLLOUT_DEPTH,\
                                                 self.PositionDictManager, self.getMazeDistance )

    def TreeReuse( self, GameState):
        global StateRootNode
        if StateRootNode is None:
        #if self.LastRootNode is None:
            print "LastRootNode is None"
            self.leaf = None
            self.novelleaf = None
            self.rootNode = None
        else:
            IndexPositions = dict()
            for index in self.allies + self.enemies:
                IndexPositions[ index ] = GameState.getAgentState( index ).getPosition()

            for Action in StateRootNode.LegalActions:
            #for Action in self.LastRootNode.LegalActions: 
                SuccStateNode = StateRootNode.SuccStateNodeDict.get( Action )
                #SuccStateNode = self.LastRootNode.SuccStateNodeDict.get( Action )
                if SuccStateNode is not None and SuccStateNode.novel and SuccStateNode.IndexPositions == IndexPositions:
                    
                    self.rootNode = SuccStateNode
                    self.rootNode.AlliesActionParent = None
                    self.rootNode.EnemiesActionParent = None
                    self.rootNode.StateParent = None

    ### the following part is used to compute the number of leaf and noveltree in search tree
                    import Queue
                    Depth = 0 
                    CandidateStates = Queue.Queue()
                    root = self.rootNode
                    CandidateStates.put( ( root ) )
                    num = 0
                    novelnum = 0 
                    while not CandidateStates.empty():              
                        CurrentState = CandidateStates.get()
                        CurrentState.depth = CurrentState.depth - 1 
                        try: 
                            if CurrentState.isFullExpand() and CurrentState.depth > Depth:
                                Depth = CurrentState.depth
                        except:
                            pass  
                        num += 1
                        if CurrentState.novel:
                            novelnum += 1
                            #if CurrentState.nVisit == 0:
                            #    print self.rootNode.IndexPositions
                            #    raise Exception( "nVisit of some StateNode is 0")                           
                            for successor in CurrentState.SuccStateNodeDict.values():
                                CandidateStates.put( successor )

                    print "The Last Tree:"
                    print "leaf nodes:",num, ", novel leaf nodes:",novelnum,", depth of root node", self.rootNode.depth,",depth of the search tree:",Depth
                    self.novelleaf = novelnum
                    del StateRootNode
                    gc.collect()
                    return 
                    #print self.rootNode.cacheMemory 
                    #return self.rootNode

                elif SuccStateNode is not None and SuccStateNode.IndexPositions == IndexPositions and not SuccStateNode.novel:

                    AlliesActionNode = SuccStateNode.AlliesActionParent
                    EnemiesActionNode = SuccStateNode.EnemiesActionParent

                    self.rootNode = SuccStateNode
                    self.rootNode.AlliesActionParent = None
                    self.rootNode.EnemiesActionParent = None
                    self.rootNode.StateParent = None
                    self.rootNode.depth = 0
                    
                    #AlliesActions, EnemiesActions = Action
                    #AlliesActionNode = self.LastRootNode.AlliesSuccActionsNodeDict[ AlliesActions ]
                    #EnemiesActionNode = self.LastRootNode.EnemiesSuccActionsNodeDict[ EnemiesActions ]
                 
                    UnNovelAlliesAgentList = []
                    Causes = AlliesActionNode.unnovelCause
                    for index in Causes:
                        UnNovelAlliesAgentList.append( self.allies[index] )
                    for agentIndex in UnNovelAlliesAgentList:
                        # self.rootNode.cacheMemory[ agentIndex ] = list()
                        # UnNovelAgentList = []
                        # Causes = AlliesActionNode.unnovelCause

                        self.rootNode.cacheMemory[agentIndex] = set()

                    if len( UnNovelAlliesAgentList) > 0:
                        print "UnNovelAlliesAgentList", UnNovelAlliesAgentList
                    #   raise Exception( "Tree Reuse, allies agent take unnovel actions " )
 
                    UnNovelEnemiesAgentList = []
                    Causes = EnemiesActionNode.unnovelCause
                    for index in Causes:    
                        UnNovelEnemiesAgentList.append( self.enemies[index] )                    
                    print "UnNovelEnemiesAgentList", UnNovelEnemiesAgentList

                    self.rootNode.cacheMemory = StateRootNode.cacheMemory
                    #self.rootNode.cacheMemory = self.LastRootNode.cacheMemory
                    for agentIndex in UnNovelEnemiesAgentList:
                        #self.rootNode.cacheMemory[ agentIndex ] = list()
                        #UnNovelAgentList = []
                        #Causes = AlliesActionNode.unnovelCause
                        self.rootNode.cacheMemory[ agentIndex ] = set()

                    self.rootNode.novel = True
                    #self.rootNode.FullExpandFunc()
                    print "="*25, "reset cachyMemory of the rootNode","="*25
                    #print self.rootNode.cacheMemory
                    self.rootNode.novelTest = False
                    self.rootNode.AlliesSuccActionsNodeDict = dict()
                    self.rootNode.EnemiesSuccActionsNodeDict = dict()
                    self.rootNode.SuccStateNodeDict = dict()
                    self.novelleaf = 1
                    del StateRootNode
                    gc.collect()
                    return 
                    #return self.rootNode
                
            self.rootNode = None
            self.leaf = None
            self.novelleaf = None   
            return

    def chooseAction( self, GameState):
        self.n = 0
        print "="* 25, "new process", "="*25
        print "self.index",self.index
        global AgentBestAction
        global StateRootNode

        if AgentBestAction is not None:
            action = AgentBestAction
            AgentBestAction = None
            return action

        start = time.time()
        self.TreeReuse( GameState )
        if self.rootNode is None:
            print "The Last Trees is no use!"
            self.rootNode = StateNode(self.allies, self.enemies, GameState,  getDistancer = self.getMazeDistance)
            self.novelleaf = None
               
        else:
            print "The Last Tree is in use!"

        print "=" * 50
        print "Start Position",self.rootNode.IndexPositions
        #print "LegalActions:", self.rootNode.LegalActions
        print "length of LegalActions:",len( self.rootNode.LegalActions )
        print "=" * 50  

        iters = 0
        invalid_iters = 0
        running_time = 0.0
        if self.novelleaf is None or self.novelleaf < 2000 or not self.rootNode.isFullExpand():
            while( iters < 40 and running_time < 60 ):
                node = self.Select()  ######UCB1 appear Unnovel node
                if node == self.rootNode or id(node) == id(self.rootNode):
                    print iters, "this iters choose RootNode"
                #print "iters:", iters, node
                if node is None:
                    invalid_iters += 1
                    if invalid_iters > 100:
                        raise Exception( "Too much invalid iters " )
                    print "Invalid Selections"
                    print "-" * 50
                    continue
                print "iters",iters, "select node position:", node.IndexPositions            
                self.ParallelGenerateSuccNode( node )
                end = time.time()
                running_time = end - start
                iters += 1
                print "-" * 50
             
        print "iters", iters  
        #self.LastRootNode = self.rootNode
        StateRootNode = self.rootNode
        bestActions = self.rootNode.getBestActions()

        bestActionsIndex = self.allies.index( self.index )
        bestAction = bestActions[bestActionsIndex]
        AgentBestAction = bestActions[1-bestActionsIndex]
        print "="*50
        print "="*25,"basic condition of this step","="*25
        print "Positions:", self.rootNode.IndexPositions
        print "index:", self.index, "beseAction:", bestAction, "PlayOut Times:", self.n
        
        for Actions, SuccStateNode in self.rootNode.SuccStateNodeDict.items():
            AlliesActions, EnemiesActions = Actions
            AlliesActionNode = self.rootNode.AlliesSuccActionsNodeDict[AlliesActions]
            EnemiesActionNode = self.rootNode.EnemiesSuccActionsNodeDict[EnemiesActions]     
            if SuccStateNode.novel:
                try:
                    print Actions, SuccStateNode.IndexPositions, SuccStateNode.nVisit, SuccStateNode.totalValue / float(SuccStateNode.nVisit), SuccStateNode.novel
                    print "Allies", AlliesActionNode.nVisit, AlliesActionNode.totalValue / float( AlliesActionNode.nVisit) 
                    print "Enemies", EnemiesActionNode.nVisit, EnemiesActionNode.totalValue / float( EnemiesActionNode.nVisit )
                except:
                    print Actions, SuccStateNode.nVisit, SuccStateNode.totalValue, SuccStateNode.novel
		    
        print "=" * 50
        print "=" * 50
        del self.rootNode
        gc.collect()
        return bestAction

    def Select( self ):
        currentNode = self.rootNode
        i = 0
        while True:
            if not currentNode.isFullExpand():
                return currentNode
            else:
                currentNode = currentNode.UCB1ChooseSuccNode()
                if currentNode is None:
                    #raise Exception( "No StateNode in tree is novel!")
                    return None
            i += 1
            if i > 200:                 
                print "myTeamv4 Select UCB1 take too much turns!"
                raise Exception 

    def WhichAgentFault( self, FirstStateNode ):

        WhichActionNodeDictList = []
        WhichTeamList = []

        alliesUnnovelNum = 0
        for actionNode in FirstStateNode.AlliesSuccActionsNodeDict.values():
            if not actionNode.novel:
                alliesUnnovelNum += 1 
        if alliesUnnovelNum == len(FirstStateNode.AlliesSuccActionsNodeDict):
            WhichActionNodeDictList.append( FirstStateNode.AlliesSuccActionsNodeDict )
            WhichTeamList.append( 0 )  # allies

        enemiesUnnovelNum = 0
        for actionNode in FirstStateNode.EnemiesSuccActionsNodeDict.values():
            if not actionNode.novel:
                enemiesUnnovelNum += 1
        if enemiesUnnovelNum == len(FirstStateNode.EnemiesSuccActionsNodeDict):
            WhichActionNodeDictList.append( FirstStateNode.EnemiesSuccActionsNodeDict )
            WhichTeamList.append( 1 )  # allies

            '''Observe that all unnovel owing to which agent'''

        for WhichTeam, WhichActionNodeDict in zip( WhichTeamList, WhichActionNodeDictList ):

            cause = set([0, 1])
            for actionkey,eachActionNode in WhichActionNodeDict.items():
                #print actionkey,eachActionNode.unnovelCause
                cause = cause & set(eachActionNode.unnovelCause)

            parentStateNode = FirstStateNode.StateParent
            nearResult = parentStateNode.nearToEnemies()
            #print "cause",cause
            
            if cause == {0}:
                if WhichTeam == 0:
                    if parentStateNode.allies[0] in nearResult[1]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.allies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.allies[0]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[0][0]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.AlliesSuccActionsNodeDict.items():
                            if eachActions[0] == action:
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)

                else:
                    if parentStateNode.enemies[0] in nearResult[2]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.enemies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.enemies[0]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[1][0]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.EnemiesSuccActionsNodeDict.items():
                            if eachActions[0] == action:
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)

            elif cause == {1}:
                if WhichTeam == 0:
                    if parentStateNode.allies[1] in nearResult[1]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.allies[1]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.allies[1]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[0][1]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.AlliesSuccActionsNodeDict.items():
                            if eachActions[1] == action:
                                eachActionsNode.novel = False
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)

                else:
                    if parentStateNode.enemies[1] in nearResult[2]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.enemies[1]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.enemies[1]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[1][1]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.EnemiesSuccActionsNodeDict.items():
                            if eachActions[1] == action:
                                eachActionsNode.novel = False
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)

            elif cause == set([0,1]):
                if WhichTeam == 0:
                    if parentStateNode.allies[0] in nearResult[1]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.allies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.allies[0]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[0][0]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.AlliesSuccActionsNodeDict.items():
                            if eachActions[0] == action:
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)

                    if parentStateNode.allies[1] in nearResult[1]:
                        FirstStateNode.novel = False
                    else:
                        parentX2, parentY2 = parentStateNode.IndexPositions[parentStateNode.allies[1]]
                        X2, Y2 = FirstStateNode.IndexPositions[FirstStateNode.allies[1]]
                        vector2 = (X2 - parentX2, Y2 - parentY2)
                        if abs(vector2[0]) > 1 or abs(vector2[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action2 = FourActions[0][1]
                                    break
                        else:
                            action2 = Actions.vectorToDirection(vector2)
                        for eachActions, eachActionsNode in parentStateNode.AlliesSuccActionsNodeDict.items():
                            if eachActions[1] == action2:
                                eachActionsNode.novel = False
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)

                else:
                    if parentStateNode.enemies[0] in nearResult[2]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.enemies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.enemies[0]]
                        vector = (X - parentX, Y - parentY)
                        if abs(vector[0]) > 1 or abs(vector[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action = FourActions[1][0]
                                    break
                        else:
                            action = Actions.vectorToDirection(vector)
                        for eachActions, eachActionsNode in parentStateNode.EnemiesSuccActionsNodeDict.items():
                            if eachActions[0] == action:
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)

                    if parentStateNode.enemies[1] in nearResult[2]:
                        FirstStateNode.novel = False
                    else:
                        parentX2, parentY2 = parentStateNode.IndexPositions[parentStateNode.enemies[1]]
                        X2, Y2 = FirstStateNode.IndexPositions[FirstStateNode.enemies[1]]
                        vector2 = (X2 - parentX2, Y2 - parentY2)
                        if abs(vector2[0]) > 1 or abs(vector2[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action2 = FourActions[1][1]
                                    break
                        else:
                            action2 = Actions.vectorToDirection(vector2)
                        for eachActions, eachActionsNode in parentStateNode.EnemiesSuccActionsNodeDict.items():
                            if eachActions[1] == action2:
                                eachActionsNode.novel = False
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)

            elif cause == set([]):
                if WhichTeam == 0:
                    if parentStateNode.allies[0] in nearResult[1] or parentStateNode.allies[1] in nearResult[1]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.allies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.allies[0]]
                        vector0 = (X - parentX, Y - parentY)
                        if abs(vector0[0]) > 1 or abs(vector0[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action0 = FourActions[0][0]
                                    break
                        else:
                            action0 = Actions.vectorToDirection(vector0)
                        parentX2, parentY2 = parentStateNode.IndexPositions[parentStateNode.allies[1]]
                        X2, Y2 = FirstStateNode.IndexPositions[FirstStateNode.allies[1]]
                        vector2 = (X2 - parentX2, Y2 - parentY2)
                        if abs(vector2[0]) > 1 or abs(vector2[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action2 = FourActions[0][1]
                                    break
                        else:
                            action2 = Actions.vectorToDirection(vector2)
                        for eachActions, eachActionsNode in parentStateNode.AlliesSuccActionsNodeDict.items():
                            if eachActions == (action0, action2):
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)
                else:
                    if parentStateNode.enemies[0] in nearResult[2] or parentStateNode.enemies[1] in nearResult[2]:
                        FirstStateNode.novel = False
                    else:
                        parentX, parentY = parentStateNode.IndexPositions[parentStateNode.enemies[0]]
                        X, Y = FirstStateNode.IndexPositions[FirstStateNode.enemies[0]]
                        vector0 = (X - parentX, Y - parentY)
                        if abs(vector0[0]) > 1 or abs(vector0[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action0 = FourActions[1][0]
                                    break
                        else:
                            action0 = Actions.vectorToDirection(vector0)
                        parentX2, parentY2 = parentStateNode.IndexPositions[parentStateNode.enemies[1]]
                        X2, Y2 = FirstStateNode.IndexPositions[FirstStateNode.enemies[1]]
                        vector2 = (X2 - parentX2, Y2 - parentY2)
                        if abs(vector2[0]) > 1 or abs(vector2[1]) > 1:
                            for FourActions in parentStateNode.SuccStateNodeDict.iterkeys():
                                if FirstStateNode == parentStateNode.SuccStateNodeDict[FourActions]:
                                    action2 = FourActions[1][1]
                                    break
                        else:
                            action2 = Actions.vectorToDirection(vector2)
                        for eachActions, eachActionsNode in parentStateNode.EnemiesSuccActionsNodeDict.items():
                            if eachActions == (action0, action2):
                                eachActionsNode.novel = False
                                if 0 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(0)
                                if 1 not in eachActionsNode.unnovelCause:
                                    eachActionsNode.unnovelCause.append(1)

        for actionKey,eachStateSucc in parentStateNode.SuccStateNodeDict.items():
            if eachStateSucc.novel:
                if not eachStateSucc.AlliesActionParent.novel or not eachStateSucc.EnemiesActionParent.novel:
                    eachStateSucc.novel = False

        FirstStateNode = parentStateNode
        NovelSuccStateNodeList = FirstStateNode.FullExpandFunc()

        return FirstStateNode, NovelSuccStateNodeList

    def Back(self, backNode):
        FirstStateNode = backNode
        NovelSuccStateNodeList = FirstStateNode.FullExpandFunc()

        while( len( NovelSuccStateNodeList ) == 0 ):
            
            try:
                if not FirstStateNode.novel:
                    raise Exception("FirstStateNode should be novel!")
                print "iteration within back begin!"
                #print "try, FirstStateNode", FirstStateNode, "NovelSuccStateNodeList", NovelSuccStateNodeList

                if FirstStateNode.StateParent is None:
                    FirstStateNode.novel = False
                    print "myTeamv4, Bcck: RootNode is unnovel!"
                    return

                result = self.WhichAgentFault( FirstStateNode )
                if result is None:
                    return None
                else:
                    FirstStateNode, NovelSuccStateNodeList = result
                    
            except:
                print "except, FirstStateNode", FirstStateNode, "NovelSuccStateNodeList", NovelSuccStateNodeList
                raise Exception

        return FirstStateNode

    def TopKSuccStateNodeList( self, CurrentStateNode, PreActions = [] ):
        CandidataFTSSNL = list()
        UCB1_depth = CurrentStateNode.depth - 1
        BackStateNode = self.Back(CurrentStateNode)
        if BackStateNode is None:
            return
        if BackStateNode.depth < UCB1_depth:
            return
        elif BackStateNode.depth == UCB1_depth:
            return CandidataFTSSNL
        else:
            SortedSuccStateNodes, LeftNum = BackStateNode.getSortedSuccStateNodes( self.M, PreActions )
            CandidataFTSSNL.extend( SortedSuccStateNodes )
        
        j = 0
        while( len(CandidataFTSSNL) > 0 and len( CandidataFTSSNL ) < self.M ):
            FirstStateNode, PreActions = CandidataFTSSNL.pop()
            LeftNum += 1
            First_depth = FirstStateNode.depth
            BackFirstStateNode = self.Back(FirstStateNode)
            if BackFirstStateNode is None:
                return
            elif BackFirstStateNode.depth == First_depth:
                SortedSuccStateNodes, LeftNum = FirstStateNode.getSortedSuccStateNodes(LeftNum, PreActions)
                CandidataFTSSNL.extend(SortedSuccStateNodes)
            elif BackFirstStateNode.depth < UCB1_depth:
                return
            else:
                i = 0
                while(i < len(CandidataFTSSNL)):
                    if not CandidataFTSSNL[i][0].novel:
                        del CandidataFTSSNL[i]
                        LeftNum += 1
                        i -= 1
                    i += 1
            j += 1 

        if len(CandidataFTSSNL) == 0:
            return []
        else:
            return CandidataFTSSNL[-self.M:]
        
    def ParallelGenerateSuccNode(self, CurrentStateNode):
        NovelSuccActionStateNodeList = CurrentStateNode.FullExpandFunc()
        if len( NovelSuccActionStateNodeList ) == 0:
            if CurrentStateNode.StateParent is None:
                print "rr" * 30
                print "BasicCondition:", CurrentStateNode.isFullExpand, CurrentStateNode.novelTest, CurrentStateNode.novel
                print "Allies"
                for actions, ActionNode in CurrentStateNode.AlliesSuccActionsNodeDict.items():
                    causes = ActionNode.unnovelCause
                    if causes is None or len( causes ) == 0:
                        print actions, ActionNode.unnovelCause
                print "Enemies"
                for actions, ActionNode in CurrentStateNode.EnemiesSuccActionsNodeDict.items():   
                    causes = ActionNode.unnovelCause
                    if causes is None or len( causes ) == 0:
                        print actions, ActionNode.unnovelCause

               # for actions, SuccStateNode in CurrentStateNode.SuccStateNodeDict.items():
               #     print actions
               #     print SuccStateNode.IndexPositions
               #     #print SuccStateNode.cacheMemory
               #     print "="*50
               # for actionKey,succ in CurrentStateNode.EnemiesSuccActionsNodeDict.items():
               #     print "first enemy features",succ.generateTuples(CurrentStateNode.enemies[0])
               #     print "second enemy features",succ.generateTuples(CurrentStateNode.enemies[1])
                print "rr" * 30
            print CurrentStateNode.IndexPositions     
            #print CurrentStateNode.LegalActions
            #print CurrentStateNode.cacheMemory

            print "All children StateNode of the chosed StateNode is not novel"
            # save memory waste computation
            self.Back(CurrentStateNode)
            return
        # print "Prepare Begin"
        MNovelSuccStateNodeList = []
        # i = 0
        t1 = time.time()
        for SuccStateNode, actions in NovelSuccActionStateNodeList:
            # i += 1
            # print i,"begin",actions
            if SuccStateNode.novel:
                topKList = self.TopKSuccStateNodeList( SuccStateNode, [ actions, ] )
                if topKList is None:
                    return
                MNovelSuccStateNodeList.extend( topKList )
            # print i,"finish"
        t2 = time.time()
        # print t2 - t1
        # print "Prepare Finish" 
        # print "The number of branch is:", len(CurrentInfo)

        print "Parallel Begin"
        if len( MNovelSuccStateNodeList ) > 2000:
            t1 = time.time()
            print len(MNovelSuccStateNodeList)
            CurrentInfo = []
            for SuccStateNode, ActionList in MNovelSuccStateNodeList:
                CurrentInfo.append( ( SuccStateNode.GameState, ActionList ) )
            ActionSeriesList = self.ChildParallelAgent.P1( CurrentInfo )
            t2 = time.time()
            print t2 - t1  
            # for ActionSeriesList in ActionSeriesLists:
            for ActionSeries in ActionSeriesList:
                EndStateNode = CurrentStateNode.update( ActionSeries )
                self.BackPropagate(EndStateNode)
        else:
            for info in MNovelSuccStateNodeList:
                _, EndStateNode = self.PlayOut3( info )
                self.BackPropagate( EndStateNode )

    def PlayOut3( self, CurrentStateInfo ): 
        self.n += 1       

        CurrentStateNode, Action = CurrentStateInfo

        n1 = SimulateAgent( self.allies[0], self.allies, self.enemies, CurrentStateNode.GameState, self.getMazeDistance )
        n2 = SimulateAgent( self.allies[1], self.allies, self.enemies, CurrentStateNode.GameState, self.getMazeDistance )

        m1 = SimulateAgent( self.enemies[0], self.enemies, self.allies, CurrentStateNode.GameState, self.getMazeDistance )
        m2 = SimulateAgent( self.enemies[1], self.enemies, self.allies, CurrentStateNode.GameState, self.getMazeDistance )
        
        iters = 0
           
        while iters < ( self.ROLLOUT_DEPTH - len( Action ) ):

            a1 = n1.chooseAction( CurrentStateNode.GameState )
            a2 = n2.chooseAction( CurrentStateNode.GameState )

            b1 = m1.chooseAction( CurrentStateNode.GameState )
            b2 = m2.chooseAction( CurrentStateNode.GameState )

            CurrentStateNode = CurrentStateNode.ChooseSuccNode(((a1, a2), (b1, b2)))

            iters += 1

        return Action, CurrentStateNode

    def BackPropagate( self, endNode):
        """
        In ExploreNode.getSupScore, self.distance_layout is used!
        """
        score = self.getScore( endNode.GameState )
        if score == self.getScore( self.rootNode.GameState ):
            LatentScore = endNode.getLatentScore()
            score += LatentScore
        #else:
        #    print "Oh My God", score
        flag = 0    
        currentNode = endNode
        while currentNode is not None:
            if currentNode.AlliesActionParent is not None:
                currentNode.AlliesActionParent.totalValue += score            
                currentNode.AlliesActionParent.nVisit += 1
                currentNode.EnemiesActionParent.totalValue += score 
                currentNode.EnemiesActionParent.nVisit += 1
            currentNode.totalValue += score
            currentNode.nVisit += 1
            currentNode = currentNode.StateParent
            if currentNode == self.rootNode or id( currentNode ) == id( self.rootNode ):
                flag = 1
                
        if flag == 0:
            print "rootNode", self.rootNode.IndexPositions, endNode.IndexPositions
            raise Exception
       