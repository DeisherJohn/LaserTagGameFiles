# set guns for machine guns (800 RPM ...) + friendly fire
import time,sys
import gunCommands

# check command line
newGameFlag=False;dest=[]
if len(sys.argv) > 1: 
	for ii in sys.argv[1:]:
		if ii[0] != '+':
			dest.append(ii) # append gun number
		else: # handle flag
			if ii == '+n': newGameFlag=True
			if ii == '+b': dest=range(2,27,2)
			if ii == '+r': dest=range(1,27,2)

if len(dest) == 0: dest=range(1,27)

gunCommands.machineGunHungerGames(dest,newGameFlag)
