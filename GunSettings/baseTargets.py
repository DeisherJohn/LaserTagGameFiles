# set guns for normal operation ("vanilla" settings)
from xbee import XBee
import serial,time,sys,os

ser = serial.Serial('/dev/tty.usbserial-DA01MHIK',19200)
xbee = XBee(ser)

pref='\x40\x06\x00'
vanilla1='\x07\xFF\x3E\x00\x00\x14\x04\x45\x00\x00\x00\x00\x1A\x02\x03\x05\xBE\x00\x00\x00\x00'

# check command line
newGameFlag=False
if len(sys.argv) == 1: 
	dest=['\xff\xff','\xff\xff']
	dest=['\x00'+str(unichr(kk)) for kk in range(1,27) ]
else:
	dest=[];dest2=''
	for ii in sys.argv[1:]:
		if ii[0] != '+':
			dest.append('\x00'+str(unichr(int(ii)))) # append gun number
			dest2=dest2+ii+' '
		else: # handle flag
			if ii == '+n': newGameFlag=True
	if len(dest) == 0: 
		# dest=['\xff\xff']
		dest=['\x00'+str(unichr(kk)) for kk in range(1,27) ]

for ii in range(3):
	for gun in dest:
		x = xbee.send('tx', dest_addr=gun, data=pref)
		x = xbee.send('tx', dest_addr=gun, data=vanilla1)
	time.sleep(0.5)
	print 'one'
	
if newGameFlag: os.system('ipython ~/Desktop/GunSettings/newGame.py '+dest2)