
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

baseKill = False
winner = -1
gameType = 'NULL'

def startGame(packetHandler, gunList = []):
	
	global baseKill
	global winner

	print 'Start game:'

	print 'How many minutes?'
	print '[To back out type \'q\']'	
	t = raw_input('-->')
	if t == 'q' or t == 'Q':
		return

	t = int(t)
	sc = t * 60
	zoomzGun.newGame()
	packetHandler.captures = []
	os.system('clear')
	print 'Game Start!'

	start = time.time()
	stop = True
	baseKill = False
	winner = -1

	try:
		while stop:
			print baseKill
			end = time.time()
			os.system('clear')

			secleft = sc - (end - start)
			minx = int(secleft / 60)
			secx = int(secleft - (minx * 60))

			if secleft < sc and secleft > 0:
				
				print '\n\ntime left: %i:%02i' % (minx,secx)
				
				analyzePackets(packetHandler)

				print 'Press ctrl+C to exit before timer\n'
				time.sleep(1)
			else: 
				stop = False

			if baseKill == True:
				break


	except (KeyboardInterrupt, SystemExit):
		zoomzGun.endGame()
		stop = False
    
	zoomzGun.endGame()

	os.system('clear')
	print '~~~~~~~~~~~~~~~~~FINAL SCORE~~~~~~~~~~~~~~~~~'
	if baseKill == True:
		if winner == 0:
			print '~~~~~~~~~~~~~~~~~ Blue Team Wins ~~~~~~~~~~~~~~~~~'
		else:
			print '~~~~~~~~~~~~~~~~~ Red Team Wins ~~~~~~~~~~~~~~~~~'

	analyzePackets(packetHandler)

	print '\nPress [enter] to return to main menu'
	a = raw_input('')

	if a == 'd':

		analyzePackets(packetHandler, 'a')
		print '\nPress [enter] to return to main menu'
		a = raw_input('')



def analyzePackets(packetHandler, prntMatrix = ''):
	"""analyze packet captures and print out kills"""
	global baseKill
	global winner

	blue=0
	red=0
	results=np.zeros(50)

	totalMatrix = np.zeros((30,30))
	blueMatrix = np.zeros((14,14))
	redMatrix = np.zeros((14,14))

	for x in range(14):
		blueMatrix[0,x] = (x * 2) - 1
		blueMatrix[x,0] = x * 2
		
		redMatrix[x,0] = (x * 2) - 1
		redMatrix[0,x] = x * 2

	for gunNumber in range(50):
		morgue=[]
		for packet in packetHandler.captures:
			if len(packet.frame.msdu) < 5: 
				print(packet)
				continue
			if (packet.frame.msdu[2] == 32 or packet.frame.msdu[2] == 37) and gunNumber == packet.frame.msdu[4]:
                # append time and gun killed to list
				morgue.append([packet.frame.msdu[3], packet.frame.msdu[4], packet.frame.timestamp])
        
		if len(morgue) == 0: 
			continue # gun not in
		
		morgue.sort() # kills sorted by gun
		print(morgue)

		timeDeath = np.diff(np.array(morgue)[:,2]) # time between kills
		gunKiller = np.array(morgue)[:,1]
		gunKilled = np.array(morgue)[:,0] # array of guns killed

		print(timeDeath)

    	## look at list of guns killed and see if timestamps are less than 0.1 sec. apart
        ## if so, then they're the same kill, so don't double count
		confirmedKills=1
		for kill in range(len(gunKiller)):	
			add = True

			if gunKilled[kill] == gunKilled[kill+1] and timeDeath[kill] < 100000:
				#double kill found
				print('found double')
				add = False
				continue
			else:
				confirmedKills += 1
				results[gunNumber]=confirmedKills

			print(add)
			print(kill)
			if (add == True) or (kill == 0):
				if gunKilled[kill] < 30:
					
					if gunKiller[kill] % 2 == 0:
						#blue killer
						killed = int((gunKiller[kill] // 2)+1)
						killer = int(gunKilled[kill] // 2)
						blueMatrix[killer, killed] += 1
					else:
						killer = int((gunKiller[kill] // 2)+1)
						killed = int(gunKilled[kill] // 2)

						redMatrix[killer, killed] += 1

					print('killed:'),
					print(int(gunKilled[kill]))
					print('killer:'),
					print(int(gunKiller[kill]))
					totalMatrix[int(gunKilled[kill]), int(gunKiller[kill])] += 1
				else:
					baseKill = True

					if gunKilled[kill] % 2 == 0:
						#blue team wins
						winner = 0
					else:
						#Red team wins
						winner = 1

		if gunNumber % 2 == 0:
			blue += confirmedKills
		else:
			red += confirmedKills

		if len(prntMatrix) > 0:
			print '~~~~~~~~ Blue Kill Matrix ~~~~~~~~~~~'
			print blueMatrix

			print '~~~~~~~~ Red Kill Matrix ~~~~~~~~~~~'
			print redMatrix

	print '\nred kills: %i ' % red
	print 'blue kills: %i ' % blue

	print(totalMatrix)

    # print out high score    
	ind=np.where(results == np.max(results))[0]
	if len(ind) < 10:
		for ii in ind:
			print 'best score by gun %i with %i kills' % (ii,results[ii])
	else: 
		print 'too many best scores!'

	
def main():
	
	args = arg_parser()
	args.channel=int(12)
	#log_init()

	#logger.info('Starting Logger')
	start_datetime = datetime.now()

	packetHandler = PacketHandler()
	packetHandler.enable()

	if args.annotation is not None:
		packetHandler.setAnnotation(args.annotation)

	handlers = [packetHandler]

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
			startGame(packetHandler, gunList)
		elif MM == 'a' or MM == 'A':
			#do gamemode select here
			gameType = zoomzGun.setupGame(gunList)
		elif MM == 'b' or MM == 'B':
			#Do gun options here
			zoomzGun.setupGun(gunList)
		elif MM == 'c' or MM == 'C':
			#Do gun options here
			startGame(packetHandler,  gunList)
		elif MM == 'd' or MM == 'D':
			#Do gun options here
			zoomzGun.endGame(gunList)
		elif MM == 'e' or MM == 'E':
			#Do gun options here
			os.system('clear')
			return 0
		else: 
			startGame(packetHandler,  gunList)


if __name__ == '__main__': 
	main()

#['\x07', '\xff', '\x14', '\x00', '\x01', '\x00', '\x00', 'E', '\x01', '\x00', '\x00', '\x00', '\x1a', '\x00', '\x03', '\x05', 'x', '\x00', '\x00', '\x00', '\x00']
#['\x07', '\xff', '\x1c', '\x00', '\x01', '\x14', '\x00', 'E', '\x01', '\x00', '\x00', '\x00', '\x1a', '\x00', '\x03', '\x05', '\x94', '\x00', '\x00', '\x00', '\x00']
#['\x07', '\xff', '$', '\x00', '\x0f', '\x14', '\x00', 'E', '\x01', '\x00', '\x00', '\x00', '\x1a', '\x01', '\x03', '\x05', '\xab', '\x00', '\x00', '\x00', '\x00']
