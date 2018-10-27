# send new game to all guns
import gunCommands
import sys,time

dest = []
if len(sys.argv) > 1: 
	dest=[ii for ii in sys.argv[1:]]

gunCommands.endGame(dest)
