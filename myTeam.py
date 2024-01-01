# myTeam.py
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
import random, time, util
import distanceCalculator

from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefenseAgent', second = 'OffenseAgent'):
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

class OffenseAgent(CaptureAgent):
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
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.foodGrid = CaptureAgent.getFood(self, gameState)
    self.myFood = CaptureAgent.getFoodYouAreDefending(self, gameState)
    self.distancer.getMazeDistances()
    self.enemies = CaptureAgent.getOpponents(self, gameState)
    self.enemyState = [gameState.getAgentState(self.enemies[0]), gameState.getAgentState(self.enemies[1])]
    self.enemyPos = [self.enemyState[0].getPosition(), self.enemyState[1].getPosition()]
    self.halfwayX = round((gameState.getAgentPosition(self.index)[0] + self.enemyPos[0][0]) / 2)
    self.enemyFood = CaptureAgent.getFood(self, gameState)
    self.powerPellets = self.getCapsules(gameState)
    self.pelletList = []
    self.yummyPelletList = []
    self.friend = 0
    if self.index == 0:
      self.friend = 2
    if self.index == 2:
      self.friend = 0
    if self.index == 1:
      self.friend = 3
    if self.index == 3:
      self.friend = 1

    #constants
    self.GHOST_MULT = 4
    self.MIDDLE_MULT = -0.5
    self.DISTANCE_MULT = -2
    self.PELLET_THRESH = 1
    self.holdingPellets = 0

    self.HOME_MID = (0, 0)
    self.halfwayY = len(self.myFood[0]) / 2


    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """

    if self.getScore(gameState) > 1 and not gameState.getAgentState(self.index).scaredTimer > 0 :
      return DefenseAgent.chooseAction(self, gameState)


    actions = gameState.getLegalActions(self.index)
    self.enemyFood = CaptureAgent.getFood(self, gameState) #update enemy pellets
    self.myFood = CaptureAgent.getFoodYouAreDefending(self, gameState)
    self.powerPellets = self.getCapsules(gameState)
    self.enemyState = [gameState.getAgentState(self.enemies[0]), gameState.getAgentState(self.enemies[1])]
    self.enemyPos = [self.enemyState[0].getPosition(), self.enemyState[1].getPosition()]
    self.enemyType = [self.enemyState[0].isPacman, self.enemyState[1].isPacman]
    self.yummyPelletList.clear()

    choice = "Stop"

    lowest = 500
    myPos = gameState.getAgentPosition(self.index)

    ##GET ENEMY PELLETS IF WE ARE HOME
    if not gameState.getAgentState(self.index).isPacman:
      self.holdingPellets = 0
      for y in enumerate(self.enemyFood):
        for x in enumerate(y[1]):
          if x[1] == True:
            self.yummyPelletList.append((y[0], x[0]))

    '''##UPDATE PELLETS EATEN
    for i in enumerate(self.yummyPelletList):
      if myPos == i[1]:
        self.yummyPelletList.remove(i[1])
        self.holdingPellets = self.holdingPellets + 1
        break'''

    #get YUMMY pellets
    for y in enumerate(self.enemyFood):
      for x in enumerate(y[1]):
        if x[1] == True:
          self.yummyPelletList.append((y[0], x[0]))
    for powerP in self.powerPellets:
      self.yummyPelletList.append(powerP)

    self.PELLET_THRESH = 1

    ##PATH TO CLOSEST ENEMY
    closestEPt = (0,0)
    if self.getMazeDistance(myPos, self.enemyPos[0]) > self.getMazeDistance(myPos, self.enemyPos[1]):
      closestEPt = self.enemyPos[1]
      furthestEPt = self.enemyPos[0]
    else:
      closestEPt = self.enemyPos[0]
      furthestEPt = self.enemyPos[1]

      ##GET PELLETS

    for y in enumerate(self.myFood):
      for x in enumerate(y[1]):
        if x[1] == True:
          self.pelletList.append((y[0], x[0]))

    ##GET MIDDLEMOST FRIENDLY PELLET
    middlemostPellet = self.pelletList[0]
    for pellet in self.pelletList:
      if self.red:
        if middlemostPellet[0] <= pellet[0]:
          middlemostPellet = pellet
      elif not self.red:
        if middlemostPellet[0] >= pellet[0]:
            middlemostPellet = pellet

    if self.HOME_MID == (0 ,0):
      self.HOME_MID = middlemostPellet


    ghostMult = 0
    middleMult = 0
    closeMult = 0
    differenceFactor = 0
    bonusScore = 0
    if gameState.getAgentState(self.index).numCarrying >= self.PELLET_THRESH:
      ghostMult = self.GHOST_MULT * 2
      middleMult = self.MIDDLE_MULT * 7
      closeMult = self.DISTANCE_MULT
    elif self.index == 2 or self.index == 3:
      ghostMult = self.GHOST_MULT
      middleMult = self.MIDDLE_MULT
      closeMult = self.DISTANCE_MULT
    elif self.index == 0 or self.index == 1:
      ghostMult = self.GHOST_MULT * 0.7
      middleMult = self.MIDDLE_MULT * 3
      closeMult = self.DISTANCE_MULT * 2

    noGhosts = False
    if self.enemyType[0] and self.enemyType[0]:
      noGhosts = True

    if self.enemyState[0].scaredTimer > 0 or self.enemyState[1].scaredTimer > 0 or noGhosts:
      self.PELLET_THRESH = 3
      ghostMult = 0
      #closeMult = self.DISTANCE_MULT * 4
      closeMult = -(self.DISTANCE_MULT^2)


    pelletScores = []
    ghostPos = self.enemyPos[0]
    ghost2Pos = self.enemyPos[1]
    bestPelletPos = self.yummyPelletList[0]
    bestPelletScore = -999

    for i in enumerate(self.yummyPelletList):
      closeBonus = 1
      bonusScore = 0
      #add ghost distance score
      distanceFromGhost = 0
      if self.enemyType[0] is False and self.enemyType[1] is False:
        distanceFromGhost = min(self.getMazeDistance(ghostPos, i[1]), self.getMazeDistance(ghost2Pos, i[1]))
      elif self.enemyType[0] is False:
        distanceFromGhost = self.getMazeDistance(ghostPos, i[1])
      elif self.enemyType[1] is False:
        distanceFromGhost = self.getMazeDistance(ghost2Pos, i[1])

      #add middle preference score
      distanceFromMiddle = abs(self.halfwayX - i[1][0])

      #if double attackers, try to split top and bottom
      if gameState.getAgentState(self.friend).isPacman:
        if self.index == 2 or self.index == 3:
          differenceFactor = i[1][1] - self.halfwayY
        elif self.index == 0 or self.index == 1:
          differenceFactor = self.halfwayY - i[1][1]



      #check if power Pellet
      if i[1] in self.powerPellets and self.getMazeDistance(myPos, i[1]) < 6:
        bonusScore += 5
        closeBonus = 20

      varianceFactor = random.random() - 0.5
      #add distance from us score
      distanceFromMe = self.getMazeDistance(myPos, i[1])
      pelletScore = ghostMult * distanceFromGhost + middleMult * distanceFromMiddle + self.DISTANCE_MULT * (distanceFromMe - closeBonus) + 1.5 * differenceFactor + 2*varianceFactor + bonusScore
      pelletScores.append(pelletScore)
      if pelletScore > bestPelletScore:
        bestPelletScore = pelletScore
        bestPelletPos = i[1]


    goalPoint = bestPelletPos
    if self.PELLET_THRESH <= gameState.getAgentState(self.index).numCarrying and abs(myPos[0] - self.halfwayX) < 10:
      #print("COMING HOME")
      if gameState.getAgentState(self.friend).isPacman:
        goalPoint = middlemostPellet
      else:
        goalPoint = gameState.getAgentPosition(self.friend)



    for action in actions:
      if action == "North":
        distance = self.getMazeDistance((myPos[0], myPos[1] + 1), goalPoint)
      if action == "South":
        distance = self.getMazeDistance((myPos[0], myPos[1] - 1), goalPoint)
      if action == "East":
        distance = self.getMazeDistance((myPos[0] + 1, myPos[1]), goalPoint)
      if action == "West":
        distance = self.getMazeDistance((myPos[0] - 1, myPos[1]), goalPoint)
      if distance < lowest:
        lowest = distance
        choice = action

    '''if self.red:
      self.debugDraw(self.HOME_MID, [1,0,0], True)
    elif not self.red:
      self.debugDraw(goalPoint, [0,0,1], True)
      self.debugDraw(self.HOME_MID, [0, 0, 1], True)'''
    return choice


class DefenseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """


  middleX = 0;
  enemies = [];
  enemyState = ["", ""];
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
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.foodGrid = CaptureAgent.getFood(self, gameState)
    self.myFood = CaptureAgent.getFoodYouAreDefending(self, gameState)
    self.distancer.getMazeDistances()
    self.enemies = CaptureAgent.getOpponents(self, gameState)
    self.enemyState = [gameState.getAgentState(self.enemies[0]), gameState.getAgentState(self.enemies[1])]
    self.enemyPos = [self.enemyState[0].getPosition(), self.enemyState[1].getPosition()]
    enemyType = [self.enemyState[0].isPacman, self.enemyState[1].isPacman]
    self.halfwayX = round((gameState.getAgentPosition(self.index)[0] + self.enemyPos[0][0]) / 2)
    self.enemyFood = CaptureAgent.getFood(self, gameState)
    self.pelletList = []
    self.yummyPelletList = []
    self.halfwayY = len(self.myFood[0])/2
    self.powerPellets = self.getCapsules(gameState)
    self.timer = 1200
    # constants
    self.GHOST_MULT = 4
    self.MIDDLE_MULT = -0.5
    self.DISTANCE_MULT = -2
    self.PELLET_THRESH = 3
    self.holdingPellets = 0
    self.friend = 0
    if self.index == 0:
      self.friend = 2
    if self.index == 2:
      self.friend = 0
    if self.index == 1:
      self.friend = 3
    if self.index == 3:
      self.friend = 1


    self.HOME_MID = (0,0)
    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """

    if (self.getScore(gameState) < 0 or gameState.getAgentState(self.index).scaredTimer > 0) or (self.getScore(gameState) == 0 and len(self.observationHistory) > 270):
      return OffenseAgent.chooseAction(self, gameState)

    self.myFood = CaptureAgent.getFoodYouAreDefending(self, gameState) #update food
    actions = gameState.getLegalActions(self.index)

    self.enemyState = [gameState.getAgentState(self.enemies[0]), gameState.getAgentState(self.enemies[1])]
    self.enemyPos = [self.enemyState[0].getPosition(), self.enemyState[1].getPosition()]
    self.enemyType = [self.enemyState[0].isPacman, self.enemyState[1].isPacman]
    self.powerPellets = self.getCapsules(gameState)
    self.pelletList.clear()
    choice = "Stop"

    lowest = 500
    myPos = gameState.getAgentPosition(self.index)

    ##GET CLOSEST ENEMY
    closestEPt = (0,0)
    if self.getMazeDistance(myPos, self.enemyPos[0]) > self.getMazeDistance(myPos, self.enemyPos[1]):
      closestEPt = self.enemyPos[1]
    else:
      closestEPt = self.enemyPos[0]

    ##GET ENEMY CLOSEST TO OUR SIDE
    invader = False
    attackerEPt = (-1,-1)
    if self.enemyType[1]:
      invader = True
      attackerEPt = self.enemyPos[1]
    elif self.enemyType[0]:
      invader = True
      attackerEPt = self.enemyPos[0]



    ##GET PELLETS

    for y in enumerate(self.myFood):
      for x in enumerate(y[1]):
          if x[1] == True:
            self.pelletList.append((y[0], x[0]))


    ##GET MIDDLEMOST PELLET
    middlemostPellet = self.pelletList[0]
    for pellet in self.pelletList:
        if self.red:
          if middlemostPellet[0] <= pellet[0]:
            middlemostPellet = pellet
        elif not self.red:
          if middlemostPellet[0] >= pellet[0]:
            middlemostPellet = pellet

    if self.HOME_MID == (0 ,0):
      self.HOME_MID = middlemostPellet

    if invader:
      goalPoint = attackerEPt
    else:
      goalPoint = middlemostPellet

    if not gameState.getAgentState(self.index).isPacman and (self.index == 2 or self.index == 3):
      if self.enemyState[0].numCarrying < 2 and self.enemyState[1].numCarrying < 2:
        goalPoint = self.HOME_MID


    for action in actions:
      if action == "North":
        distance = self.getMazeDistance((myPos[0], myPos[1] + 1), goalPoint)
      if action == "South":
        distance = self.getMazeDistance((myPos[0], myPos[1] - 1), goalPoint)
      if action == "East":
        if myPos[0] + 1 != self.halfwayX:
          distance = self.getMazeDistance((myPos[0] + 1, myPos[1]), goalPoint)
        else:
          distance = 99999
      if action == "West":
        if myPos[0] - 1 != self.halfwayX:
          distance = self.getMazeDistance((myPos[0] - 1, myPos[1]), goalPoint)
        else:
          distance = 99999
      if distance < lowest:
        lowest = distance
        choice = action

    if goalPoint == myPos:
      choice = "Stop"
    ##print("Position: (", myPos[0], ",", myPos[1], ")    Goal: (" , goalPoint[0] , "," , goalPoint[1] , ")")

    '''
    Idea:
    
    - Try to stay close to center line
    - If both enemies are ghosts, then try to stay around the y position of the closest enemy
    - If enemy is on our side, try to stay on their y position
    - iterative deepening
    - Try to attack quickly after eating an enemy
    
    '''


    '''
    You should change this in your own agent.
    '''
    return choice