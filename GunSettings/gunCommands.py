# send new game to all guns
from xbee import XBee
import serial,time,sys,os

def newGame(gunList=[]):
	"""list of gun numbers (integers); if this is empty, then new game all guns"""

	ser = serial.Serial('/dev/tty.usbserial-DA01MHIK',19200)
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

	ser = serial.Serial('/dev/tty.usbserial-DA01MHIK',19200)
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
		time.sleep(0.6)
		newGame(gunList) 

def vanilla(gunList=[],ng=False):
	"""set guns to vanilla; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x07\xFF\x1C\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x98\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xA6\x02\x03\x00\x04\x00\x14\x01\xDD\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def vanilla50(gunList=[],ng=False):
	"""set guns to vanilla-50 points; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x07\xFF\x1A\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x96\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xA6\x02\x03\x00\x04\x00\x14\x01\xDD\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def vanilla70(gunList=[],ng=False):
	"""set guns to vanilla-70 points; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x07\xFF\x1e\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x9a\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xA6\x02\x03\x00\x04\x00\x14\x01\xDD\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def vanilla90(gunList=[],ng=False):
	"""set guns to vanilla-90 points; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x07\xFF\x22\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x9E\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xA6\x02\x03\x00\x04\x00\x14\x01\xDD\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def sniper(gunList=[],ng=False):
	"""set guns to sniper; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x06\xFF\x00\x02\x04\x00\x0F\x00\xA6\x02\x03\x00\x04\x00\x14\x00\xD7\x00\x00\x00\x00',\
		'\x07\xFF\x0A\x00\x00\x14\x00\x45\x01\x00\x00\x00\x1A\x02\x03\x05\x87\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def sniperHungerGames(gunList=[],ng=False):
	"""set guns to sniper w/ friendly fire on; gunList is a list of guns to send code to; if empty, 
	send to all guns 
	ng = false; if true, send new game"""

	code=['\x06\xFF\x00\x02\x04\x00\x0F\x00\xA6\x02\x03\x00\x04\x00\x14\x00\xD7\x00\x00\x00\x00',\
		'\x07\xFF\x0A\x00\x00\x14\x04\x45\x01\x00\x00\x00\x1A\x02\x03\x05\x8B\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def machineGun(gunList=[],ng=False):
	"""set guns to machine gun; gunList is a list of guns to send code to; if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x06\xFF\x00\x02\x04\x00\x05\x19\xA6\x02\x03\x0B\x04\x00\x14\x01\xF2\x00\x00\x00\x00',\
		'\x07\xFF\x22\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x9E\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def machineGunHungerGames(gunList=[],ng=False):
	"""set guns to machine gun with friendly fire on; gunList is a list of guns to send code to; 
	if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x06\xFF\x00\x02\x04\x00\x05\x19\xA6\x02\x03\x0B\x04\x00\x14\x01\xF2\x00\x00\x00\x00',\
		'\x07\xFF\x22\x00\x00\x14\x04\x45\x00\x00\x00\x00\x1A\x02\x03\x05\xA2\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def HungerGames(gunList=[],ng=False):
	"""set guns to vanilla with friendly fire on; gunList is a list of guns to send code to; 
	if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x07\xFF\x1C\x00\x00\x14\x04\x45\x00\x00\x00\x00\x1A\x02\x03\x05\x9C\x00\x00\x00\x00',\
		'\x06\xFF\x00\x02\x04\x00\x05\x0F\xA6\x02\x03\x00\x04\x00\x14\x01\xDD\x00\x00\x00\x00']

	programGun(gunList,code,ng)

def VIPjuggernaut(gunList=[],ng=False):
	"""set guns to vanilla with friendly fire on; gunList is a list of guns to send code to; 
	if empty, send to all guns
	ng = false; if true, send new game"""

	code=['\x06\xFF\x00\x02\x04\x00\x03\x19\xA6\x02\x03\x0B\x04\x00\x14\x01\xF0\x00\x00\x00\x00',\
		'\x07\xFF\x2E\x00\x00\x14\x00\x45\x00\x00\x00\x00\x1A\x02\x03\x05\xAA\x00\x00\x00\x00']

	programGun(gunList,code,ng)