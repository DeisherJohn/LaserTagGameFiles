# send new game to all guns
from xbee import XBee
import serial,time,sys,os

def newGame(gunList=[]):
	"""list of gun numbers (integers); if this is empty, then new game all guns"""

	ser = serial.Serial('/dev/ttyUSB0',19200)
	xbee = XBee(ser)

	if len(gunList) == 0: 
		dest=['\xff\xff']
		# dest=['\x00'+str(unichr(kk)) for kk in range(1,27) ]
	else:
		dest=[]
		for ii in gunList:
			dest.append('\x00'+str(unichr(int(ii)))) # append gun number

	pref='\x40\x03\x05' # new game code

	for ii in range(3):
		for gun in dest:
			x = xbee.send('tx', dest_addr=gun, data=pref)
		time.sleep(0.8)

def endGame(gunList=[]):
	"""list of gun numbers (integers); if this is empty, then new game all guns"""

	ser = serial.Serial('/dev/ttyUSB0',19200)
	xbee = XBee(ser)

	if len(gunList) == 0: 
		dest=['\xff\xff']
		# dest=['\x00'+str(unichr(kk)) for kk in range(1,27) ]
	else:
		dest=[]
		for ii in gunList:
			dest.append('\x00'+str(unichr(int(ii)))) # append gun number

	pref='\x40\x03\x07' # end game code

	for ii in range(3):
		for gun in dest:
			x = xbee.send('tx', dest_addr=gun, data=pref)
		time.sleep(0.8)

def programGun(gunList,code,ng=False):
	"""send code string to list of guns; code can be a list -- if so, send all strings
	gunList is a list of guns to send code to; if gunList is empty, send to all guns
	ng = false; if true, send new game"""

	ser = serial.Serial('/dev/tty.usbserial-DA01MHIK',19200)
	xbee = XBee(ser)

	pref='\x40\x06\x00'

	if len(gunList) == 0: gunList=range(1,27)
	dest=['\x00'+str(unichr(int(ii))) for ii in gunList]

	if type(code) != list: code=[code]

	for ii in range(3):
		for c1 in code:
			for gun in dest:
				x = xbee.send('tx', dest_addr=gun, data=pref)
				x = xbee.send('tx', dest_addr=gun, data=c1)
			time.sleep(0.5)
		print 'sent: %i' % (ii+1)

	if ng: 
		time.sleep(0.3)
		newGame(gunList) 

def machineGun(gunList = []):
	"""Machine gun setting: automatic, 15 round clip, 10 Damage, 1 fire rate"""
	command = ['\x07\xFF\x1C\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x98\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xC8\x02\x03\x00\x04\x01\x14\x01\x00\x00\x00\x00\x00']
	
	programGun(gunList,command, False)

