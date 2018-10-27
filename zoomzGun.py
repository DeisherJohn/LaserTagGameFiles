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

	ser = serial.Serial('/dev/ttyUSB0',19200)
	xbee = XBee(ser)

	pref='\x40\x06\x00'

	if len(gunList) == 0: 
		gunList=range(1,27)
		print 'empty list'
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

def setupGun(gunList = []):

	#do gamemode select here
	os.system('clear')
	print 'Gun Options:'
	print 'Please Select a Starting Option: (NULL is AR)'
	print 'A: Standard AR'
	print 'B: Submachine Gun'
	print 'C: Sniper'
	print 'D: LMG'
	print 'E: Custom'

	if len(gunList) == 1:
		print 'F: Rocket Launcher'

	GM = raw_input('')

		#do gamemode select here
	os.system('clear')
	print 'Use Silencer: (y/[n])'

	SO = raw_input('')
	if SO == 'y' or SO == 'Y':
		SO = 'y'
	else: 
		SO = 'n'


	if len(GM) == 0 or GM == 'a' or GM == 'A':
		#AR here
		AR(SO, gunList)
	elif GM == 'b' or GM == 'B':
		#Do Sub here
		submachineGun(SO, gunList)
	elif GM == 'e' or GM == 'E':
		#Do Sub here
		customGun(gunList)
	elif GM == 'c' or GM == 'C':
		#Do Sub here
		sniperGun(SO, gunList)
	elif GM == 'd' or GM == 'D':
		#Do Sub here
		LMG(SO, gunList)
	elif GM == 'f' or GM == 'F':
		rocketLauncher(gunList)

def AR(SO, gunList = []):
	#default rifle for laser tag
	os.system('clear')
	print gunList
	print 'AR'

	#need to change to default values
	#command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x15', '\xC8', '\x02', '\x03', '\x00', '\x04', '\x01', '\x14', '\x01', '\x01', '\x00', '\x00', '\x00', '\x00']
	
	if SO == 'n':
		command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x0F', '\xC8', '\x01', '\x03', '\x02', '\x04', '\x01', '\x14', '\x01', '\x01', '\x00', '\x00', '\x00', '\x00']
	else: 
		command = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x05', '\x0F', '\xC8', '\x01', '\x03', '\x02', '\x04', '\x01', '\x14', '\x00', '\x02', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)



def submachineGun(SO, gunList = []):
	"""Machine gun setting: automatic, 15 round clip, 10 Damage, 1 fire rate"""
	os.system('clear')
	print gunList
	print 'Sub Machine Gun'

	if SO == 'n':
		command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x14', '\xC8', '\x02', '\x03', '\x06', '\x03', '\x01', '\x14', '\x01', '\x0A', '\x00', '\x00', '\x00', '\x00']
	else: 
		command = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x05', '\x14', '\xC8', '\x02', '\x03', '\x06', '\x03', '\x01', '\x14', '\x00', '\x0B', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def sniperGun(SO, gunList = []):
	#	Sniper
	if SO == 'n':
		command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x0A', '\x05', '\xC8', '\x00', '\x03', '\x00', '\x05', '\x01', '\x14', '\x01', '\xFA', '\x00', '\x00', '\x00', '\x00']
	else: 
		command = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x0A', '\x05', '\xC8', '\x00', '\x03', '\x00', '\x05', '\x01', '\x14', '\x00', '\xFB', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)


def LMG(SO, gunList = []):
	#LMG
	if SO == 'n':
		command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x04', '\x32', '\xC8', '\x02', '\x03', '\x03', '\x08', '\x01', '\x14', '\x01', '\x29', '\x00', '\x00', '\x00', '\x00']
	else: 
		command = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x04', '\x32', '\xC8', '\x02', '\x03', '\x03', '\x08', '\x01', '\x14', '\x00', '\x2A', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def rocketLauncher(gunList):
	#LMG
	command = ['\x06', '\xFF', '\x01', '\x02', '\x04', '\x00', '\x0F', '\x00', '\x06', '\x00', '\x03', '\x00', '\x0F', '\x01', '\x14', '\x01', '\x43', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def customGun(gunList = []):
	#Do gun options here
	command = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x0F', '\xC8', '\x02', '\x03', '\x00', '\x04', '\x01', '\x14', '\x01', '\x00', '\x00', '\x00', '\x00', '\x00']
	os.system('clear')
	op = 1
	print 'Sound Mode:'
	print '[1]: Mil-Sim'
	print ' 2 : Sci-Fi'
	print ' 3 : Silencer'
	op = raw_input('-->')

	if len(op) == 0:
		command[2] = '\x00'
	else:
		op = int(op)

	if op == 1:
		command[2] = '\x00'
	elif op == 2:
		command[2] = '\x01'
	elif op == 3:
		command[2] = '\x02'

	os.system('clear')
	op = 15
	print 'Clip Size:'
	print '0   : Infinite'
	print '[15]: Default'
	print '{between 1 and 254}'
	op = raw_input('-->')

	if len(op) == 0:
		command[7] = '\xFF'
	else:
		op = int(op)

	if op == 0:
		command[7] = '\xFF'
	elif op > 0 and op < 254:
		command[7] = chr(op)
	elif op < 0:
		op = 1
	else:
		command[7] = '\x0F'

	os.system('clear')
	op = 200
	print 'Clip Number:'
	print '[200]: Default'
	print '{between 1 and 254}'
	op = raw_input('-->')

	if len(op) == 0:
		command[8] = chr(200)
		op = -1
	else:
		op = int(op)

	if op > 0 and op < 255:
		command[8] = chr(op)
	else:
		command[8] = chr(200)

	os.system('clear')
	op = 3
	print 'Fire Mode:'
	print '1  : Simi-Auto'
	print '2  : Burst'
	print '[3]: Full-Auto'

	op = raw_input('-->')

	if len(op) == 0:
		command[9] = '\x02'
	else:
		op = int(op) - 1
		print op

	if op >= 0 and op < 4:
		command[9] = chr(op)
	else:
		command[9] = '\x01'


	os.system('clear')
	op = 15
	print 'Damage:'
	print '1   : 1'
	print '2   : 2'
	print '3   : 4'
	print '4   : 5'
	print '5   : 7'
	print '[6] : 10'
	print '7   : 15'
	print '8   : 17'
	print '9   : 20'
	print '10  : 25'
	print '11  : 30'
	print '12  : 35'
	print '13  : 40'
	print '14  : 50'
	print '15  : 75'
	print '16  : 100'
	op = raw_input('-->')

	if len(op) == 0:
		command[6] = '\x05'
	else:
		op = int(op) - 1

	if op >= 0 and op < 17:
		command[6] = chr(op)
	else:
		command[6] = '\x05'

	os.system('clear')
	op = 15
	print 'Rate of Fire <RPM>:'
	print '[1] : 250'
	print '2   : 300'
	print '3   : 350'
	print '4   : 400'
	print '5   : 450'
	print '6   : 500'
	print '7   : 550'
	print '8   : 600'
	print '9   : 650'
	print '10  : 700'
	print '11  : 750'
	print '12  : 800'

	op = raw_input('-->')

	if len(op) == 0:
		command[11] = '\x00'
	else:
		op = int(op) - 1

	print "Gun RPM Value: "
	print op

	if op >= 0 and op < 17:
		print op
		command[11] = chr(op)
		print command[11]	
	else:
		command[11] = '\x00'

	os.system('clear')
	op = 15
	print 'Reload (seconds):'
	print 'Enter number between 1 and 255'
	print '[4] : 4 seconds'

	op = raw_input('-->')

	if len(op) == 0:
		command[12] = '\x04'
	else:
		op = int(op)

	if op > 0 and op < 256:
		command[12] = chr(op)
	else:
		command[12] = '\x04'


	checkSum = 0;
	bitNumber = 0
	for i in range(13):
		checkSum += ord(command[i+2])

	minCheck = checkSum
	minCheck -= ord(command[15])

	checkSum = checkSum % 255
	minCheck = minCheck % 255

	newCheck = chr(checkSum)
	lowCheck = chr(minCheck)

	#set checksum

	command[16] = newCheck
	print command
	cmd = ''.join(command)

	command[16] = lowCheck
	print command
	nCommand = ''.join(command)

	programGun(gunList, cmd, True)
	print 'Gun clone successful? y/[n]'
	op = raw_input('-->')

	if len(op) > 0:
		programGun(gunList, nCommand, True)
	else:
		op = int(op)

		if op == 'n' or op == 'N':
			programGun(gunList, nCommand, True)

def TDM(gunList = []):
	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x00', '\x00', '\x45', '\x00', '\x00', '\x00', '\x00', '\x1A', '\x00', '\x03', '\x05', '\x82', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def FFA(gunList = []):
	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x00', '\x04', '\x45', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x03', '\x05', '\x6C', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def Shields(gunList = []):
	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x14', '\x00', '\x47', '\x01', '\x00', '\x00', '\x00', '\x1A', '\x01', '\x03', '\x05', '\x9A', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	programGun(gunList, cmd, True)

def customGame(gunList = []):
	#Do gun options here
	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x00', '\x00', '\x45', '\x01', '\x00', '\x00', '\x00', '\x1A', '\x00', '\x03', '\x05', '\x83', '\x00', '\x00', '\x00', '\x00']
	os.system('clear')
	op = 1
	print 'Life Points:'
	print '[0]: 60'
	print ' 1 : 10'
	print ' 2 : 20'
	print ' 3 : 30'
	print ' 4 : 40'
	print ' 5 : 50'
	print ' 6 : 60'
	print ' 7 : 70'
	print ' 8 : 80'
	print ' 9 : 90'
	print ' 10: 100'
	op = raw_input('-->')

	if len(op) == 0 or op == 0:
		command[2] = '\x1C'
	else:
		op = int(op)

	if op == 1:
		command[2] = '\x0A'
	elif op == 2:
		command[2] = '\x14'
	elif op == 3:
		command[2] = '\x16'
	elif op == 4:
		command[2] = '\x18'
	elif op == 5:
		command[2] = '\x1A'
	elif op == 6:
		command[2] = '\x1C'
	elif op == 7:
		command[2] = '\x1E'
	elif op == 8:
		command[2] = '\x20'
	elif op == 9:
		command[2] = '\x22'
	elif op == 10:
		command[2] = chr(36)
	else:
		command[2] = '\x1C'


	os.system('clear')
	op = 15
	print 'Auto Respawn Timer:'
	print '0   	: Manual'
	print '1-180: Seconds'

	op = raw_input('-->')

	if len(op) == 0:
		command[4] = '\x00'
	else:
		op = int(op)

	if op >= 0 and op <= 180:
		command[4] = chr(op)
	else:
		command[4] = '\x00'

	os.system('clear')
	op = 200
	print 'Shields:'
	print '[0]: No'
	print '1  : Yes'
	op = raw_input('-->')

	if len(op) == 0:
		command[7] = '\x45'
	else:
		op = int(op)


	if op == 1:
		command[7] = '\x47'

		os.system('clear')
		op = 1
		print 'Shield Level:'
		print '[0]: 20'
		print ' 1 : 10'
		print ' 2 : 20'
		print ' 3 : 30'
		print ' 4 : 40'
		print ' 5 : 50'
		print ' 6 : 60'
		print ' 7 : 70'
		print ' 8 : 80'
		print ' 9 : 90'
		print ' 10: 100'
		op = raw_input('-->')

		if len(op) == 0 or op == 0:
			command[5] = '\x14'
		else:
			op = int(op)

		if op == 1:
			command[5] = '\x0A'
		elif op == 2:
			command[5] = '\x14'
		elif op == 3:
			command[5] = '\x16'
		elif op == 4:
			command[5] = '\x18'
		elif op == 5:
			command[5] = '\x1A'
		elif op == 6:
			command[5] = '\x1C'
		elif op == 7:
			command[5] = '\x1E'
		elif op == 8:
			command[5] = '\x20'
		elif op == 9:
			command[5] = '\x22'
		elif op == 10:
			command[5] = '\x24'
		else:
			command[5] = '\x14'

		os.system('clear')
		op = 15
		print 'Shield Respawn Timer:'
		print '0   	: Off'
		print '1-20: Seconds'
		print 'Shields/Second'

		op = raw_input('-->')

		if len(op) == 0:
			command[13] = '\x00'
		else:
			op = int(op)

		if op >= 0 and op <= 20:
			command[13] = chr(op)
		else:
			command[13] = '\x01'
	else:
		command[6] = '\x45'

	os.system('clear')
	op = 1
	print 'Friendly Fire:'
	print '[0]: Off'
	print '1  : On'

	op = raw_input('-->')

	if len(op) == 0:
		command[6] = '\x00'
	else:
		op = int(op)

	if op == 1:
		command[6] = '\x04'
	else:
		command[6] = '\x00'

	os.system('clear')
	op = 1
	print 'Unlimited Ammo:'
	print '[0]: Off'
	print '1  : On'

	op = raw_input('-->')

	if len(op) == 0:
		a = 0
	else:
		op = int(op)

	if op == 1 and command[6] == '\x04':
		command[6] = '\x0C'
	elif op == 1 and command[6] == '\x00':
		command[6] = '\x08'

	os.system('clear')
	op = 15
	print 'Hit delay TODO STILL:'
	print '1   : 1'
	print '2   : 2'
	print '3   : 4'
	print '4   : 5'
	print '5   : 7'
	print '[6] : 10'
	print '7   : 15'
	print '8   : 17'
	print '9   : 20'
	print '10  : 25'
	print '11  : 30'
	print '12  : 35'
	print '13  : 40'
	print '14  : 50'
	print '15  : 75'
	print '16  : 100'
#	op = raw_input('-->')
#
#	if len(op) == 0:
#		command[6] = '\x05'
#	else:
#		op = int(op) - 1
#
#	if op >= 0 and op < 17:
#		command[6] = chr(op)
#	else:
#		command[6] = '\x05'


	checkSum = 0;
	bitNumber = 0
	for i in range(13):
		checkSum += ord(command[i+2])

	checkSum = checkSum % 255

	newCheck = chr(checkSum)

	#set checksum

	command[16] = newCheck
	print command
	cmd = ''.join(command)

	programGun(gunList, cmd, True)

def setupGame(gunList = []):

	#do gamemode select here
	os.system('clear')
	print 'Game Options:'
	print 'Please Select a Starting Option: (NULL is TDM)'
	print 'A: TDM'
	print 'B: FFA'
	print 'C: Shields'
	print 'D: Custom'

	GM = raw_input('')

	if len(GM) == 0 or GM == 'a' or GM == 'A':
		#AR here
		TDM(gunList)
		return 'TDM'
	elif GM == 'b' or GM == 'B':
		#Do Sub here
		FFA(gunList)
		return 'FFA'
	elif GM == 'c' or GM == 'C':
		#Do Sub here
		Shields(gunList)
		return 'SHIELD'
	elif GM == 'd' or GM == 'D':
		#Do Sub here
		customGame(gunList)
		return 'CG'




#['\x07', '\xff', '\x1c', '\x00', '\x00', '\x00', '\x00', 'E', '\x01', '\x00', '\x00', '\x00', '\x1a', '\x00', '\x03', '\x05', '\x7f', '\x00', '\x00', '\x00', '\x00']



