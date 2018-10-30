
""" Zoomz laser tag program

Created by: John Deisher

"""


import argparse
import binascii
from datetime import datetime
import errno
import inspect
import logging.handlers
import select
import StringIO
import struct
import sys,os
import threading
import time
import types
import usb.core
import usb.util
import pdb
import numpy as np
import zoomzGun

import ieee15dot4 as ieee

import pyCCsnifferOriginal

from pyCCsnifferOriginal import PacketHandler
from pyCCsnifferOriginal import arg_parser
from pyCCsnifferOriginal import CC2531EMK
from pyCCsnifferOriginal import SniffedPacket
from pyCCsnifferOriginal import CapturedFrame
from pyCCsnifferOriginal import CustomAssertFrame

#from sniffer import CC2531EMK

class ZoomzLaserTag(object):
	#all datastructures that will be needed. 
	def __init__(self):
		self.killMatrix = np.zeros((30,30))
		self.killList = np.zeros(30)
		self.baseKill = False
		self.winner = -1
		self.gameType = 'NULL'
		self.start = -1
		self.packetBuffer = []
		self.redScore = -1
		self.blueScore = -1
	pass

	#updates the screen with the new time left and calls for an update to score. 
	def updateScreen(_timeLimit):
		current = time.time()
		os.system('clear')

		secleft = _timeLimit - (current - self.start)

		minx = int(secleft // 60)
		secx = int(secleft - (minx * 60))

		if secleft < _timeLimit and secleft > 0:
			print '\n\ntime left: %i:%02i' % (minx,secx)
		else:
			#game is over
			return False

		self.updateScore()

		return True

	#called when the final score is needed to be displayed
	def finalScore():
		os.system('clear')
		print '~~~~~~~~~~~~~~~~~FINAL SCORE~~~~~~~~~~~~~~~~~'
		if self.baseKill == True:
			if self.winner == 'blue':
				print '~~~~~~~~~~~~~~~~~ Blue Team Wins ~~~~~~~~~~~~~~~~~'
			elif self.winner == 'red':
				print '~~~~~~~~~~~~~~~~~ Red Team Wins ~~~~~~~~~~~~~~~~~'

		self.updateScore()

		print('Red Kills:' + self.redScore)
		print('Blue Kills:' + self.blueScore)

		self.displayScore()

		print '\nPress [enter] to return to main menu'
		a = raw_input('')


	#This function is used as the start of all games. 
	def TESTstartGame(gunList = []):
		print 'Start game:'

		print 'How many minutes?'
		print '[To back out type \'q\']'	
		t = raw_input('-->')
		if t == 'q' or t == 'Q':
			return

		#set the time in seconds
		t = int(t)
		sc = t * 60

		zoomzGun.newGame() #send a new game signal
		self.packetBuffer.captures = [] #clear the packets
		os.system('clear') #clear the screen
		print 'Game Start!'

		#ensure that all globals are set properly. 
		self.start = time.time()
		self.stop = True
		self.baseKill = False
		self.winner = -1
		self.redScore = 0
		self.blueScore = 0

		try:
			while self.stop:
				self.stop = self.updateScreen(sc)
				self.displayTopPlayers()

				print 'Press ctrl+C to exit before timer\n'
				time.sleep(1)

				if self.baseKill == True:
					break

		except (KeyboardInterrupt, SystemExit):
			self.stop = False
	    
		zoomzGun.endGame()
		self.finalScore()

	#this function is used to  parse the larger matric and display them as 2 smaller team based matrix	
	def showTeamMatrix():
		blueMatrix = np.zeros((15,15))
			redMatrix = np.zeros((15,15))

			for row in range(30):
				for column in range(30):
					if row % 2 == 0:
						#blue row
						if column % 2 == 1:
							#red column, add this to blue?
							blueMatrix[int(row // 2), int((column //2) + 1)]
						else:
							continue
					else:
						#red row
						if column % 2 == 0:
							redMatrix[int((row // 2)+1), int(column //2)]
						else:
							continue
		pass

	def displayTopPlayers():
		sortedList = []
			for gun in len(self.killList):
				sortedList.append((killList[gun], gun))

			sortedList.sort()

			print('TOP FIVE PLAYERS')
			for x in range(5):
				print(x + ' : ' + sortedList[x])

	def displayScore():
		#display player rankings or team matrix
		print('Display which type: [R]ankings or [M]atrix: ')
		AG = raw_input('-->')

		if len(AG) == 0:
			AG = 'R'
		elif AG[0] == 'm' or AG[0] == 'M' or self.gameType == 'TDM':
			#display kill matrix in team form. 
			self.showTeamMatrix()
		
		self.displayTopPlayers()


	def updateScore():
		#used to sort out any new packets                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
		
		packetData = []

		while self.packetBuffer.captures:
			#sort through all the different incoming packets

			packet = self.packetBuffer.captures[0]
			if (packet.frame.msdu[2] == 32 or packet.frame.msdu[2] == 37) and packet.frame.msdu[4] < 50 and len(packet.frame.msdu) > 4:
				#packet is a kill, add to main list
				packetData.append([packet.frame.msdu[3], packet.frame.msdu[4], packet.frame.timestamp])
			del packet

		if len(packetData) == 0:
			#no kills, move on
			continue

		packetData.sort()

		timeDeath = np.diff(np.array(packetData)[:,2]) # time between kills
		killer = np.array(packetData)[:,1] #array for gun killers
		victim = np.array(packetData)[:,0] # array of guns killed

		for kill in len(victim):

			if kill > 0:
				if victim[kill] == victim[kill - 1] and abs(timeDeath[kill - 1]) < 100000:
					#double kill found
					continue #move to next loop
			
				if victim[kill] > 30:
					#this is a base kill
					self.baseKill = True
					if victim[kill] % 2 == 0:
						#blue base killed
						self.winner = 'red'
					else:
						self.winner = 'blue'
					continue

			#add kill to the passed in data Structs
			self.killMatrix[int(victim[kill]), int(killer[kill])] += 1
			self.killList[int(killer[kill])] += 1

			if killer[kill] % 2 == 0:
				self.blueScore += 1
			else:
				self.redScore += 1
	
def main():
	
	args = arg_parser()
	args.channel=int(12)
	#log_init()

	#logger.info('Starting Logger')
	start_datetime = datetime.now()

	packetHandler = PacketHandler()
	packetHandler.enable()
	gameObj = ZoomzLaserTag()

	if args.annotation is not None:
		packetHandler.setAnnotation(args.annotation)

	handlers = [packetHandler]

	gameObj.packetData = packetHandler

	def handlerDispatcher(timestamp, macPDU):
		if len(macPDU) > 0:
			packet = SniffedPacket(macPDU, timestamp)
			for handler in handlers:
				handler.handleSniffedPacket(packet)

	snifferDev = CC2531EMK(handlerDispatcher, args.channel)
	snifferDev.start()

	gunList = []

	while True:
		os.system('clear')

		
		print('Zoomz Laser Tag Software')

		print 'All Guns? (y/n [keep last list, starts with all])'
		AG = raw_input('')

		if len(AG) == 0:
			gunList = gunList
		elif AG[0] == 'y' or AG[0] == 'Y':
			gunList = []
		else:
			print 'Please enter the gun numbers followed by enter, use 0 to end'
			temp = 1
			while temp > 0 and temp < 30:
				temp = int(raw_input('-->'))
				if temp == 0:
					break
				elif(temp > 0 or temp < 30):
					gunList.append(temp)
					print gunList
		
		os.system('clear')
		print "list of guns"
		print gunList
		print '\nMain Menu'
		print 'Please Select an Option: (enter to Start game)'
		print 'A: Game Type'
		print 'B: Gun Option'
		print 'C: Start Game'
		print 'D: End Game'
		print 'E: Exit'

		MM = raw_input('')

		if len(MM) == 0:
			#do new game here
			gameObj.TESTstartGame(gunList)
		elif MM == 'a' or MM == 'A':
			#do gamemode select here
			gameObj.gameType = zoomzGun.setupGame(gunList)
		elif MM == 'b' or MM == 'B':
			#Do gun options here
			zoomzGun.setupGun(gunList)
		elif MM == 'c' or MM == 'C':
			#Do gun options here
			gameObj.TESTstartGame(gunList)
		elif MM == 'd' or MM == 'D':
			#Do gun options here
			zoomzGun.endGame(gunList)
		elif MM == 'e' or MM == 'E':
			#Do gun options here
			os.system('clear')
			return 0
		else: 
			gameObj.TESTstartGame(gunList)


if __name__ == '__main__': 
	main()
