#!/usr/bin/env python

"""
   based on pyCCSniffer - a python module to connect to the CC2531emk USB dongle, decode
                 the received frames and provide a quick way to get to your
                 bytes!

    modified by A.E. Dessler // 7/15

    this code is for the VIP laser tag game.  
"""

"""
   Functionality
   -------------
   Read IEEE802.15.4 frames from the default CC2531 EMK sniffer firmware, 
   decode them and store them in memory (and maybe print them yeah!).
   In interactive mode, the user can also input commands from stdin.
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
import sys
import threading
import time
import types
import usb.core
import usb.util
import pdb
import os
import numpy as np

import ieee15dot4 as ieee


__version__ = '0.0.1'

defaults = {
    'debug_level': 'WARN',
    'log_level': 'INFO',
    'log_file': 'pyCCSniffer.log',
    'channel': 11,
}

logger = logging.getLogger(__name__)
stats = {}

class SniffedPacket(object):
    def __init__(self, macPDUByteArray, timestampBy32):
        self.__macPDUByteArray = macPDUByteArray
        self.timestampBy32 = timestampBy32
        self.timestampUsec = timestampBy32 / 32.0
        self.len = len(self.__macPDUByteArray)

    def get_timestamp(self):
        return self.timestampUsec

    def get_macPDU(self):
        return self.__macPDUByteArray

class CapturedFrame(object):
    def __init__(self, frame, rssiSniff, annotation):
        self.frame = frame
        self.rssiSniff = rssiSniff
        self.annotation = annotation

    def __repr__(self, *args, **kwargs):
        if len(self.annotation) > 0:
            return "{} RssiSniff[{}] Annotation[{}]".format(self.frame, 
                                                            self.rssiSniff,
                                                            self.annotation)
        
        return "{} RssiSniff[{}]".format(self.frame, self.rssiSniff)

class CustomAssertFrame(object):
    def __init__(self, date, code, line, file, **kwargs):
        self.date = date
        self.code = code
        self.line = line
        self.file = file
        self.time = datetime.now()

    def __repr__(self, *args, **kwargs):
        return "AssertFrame Time[{}] Code[{}] Line[{}] File[{}] Compiled[{}]".format(self.time, self.code, self.line, self.file, self.date)
    
class PacketHandler(object):
    def __init__(self):
        stats['Dissected'] = 0
        stats["Dissection errors"]  = 0
        stats["CRC Errors"] = 0
        stats["Beacon"] = 0
        stats["Data"] = 0
        stats["Acknowledgment"] = 0
        stats["MAC Command"] = 0
        stats["LLDN"] = 0
        stats["Multipurpose"] = 0
        stats["Unknown"] = 0
        stats["Custom frames"] = 0
        self.__annotation = ''
        self.__samples = 0
        self.__beaconPrintingEnabled = True
        self.__dataFramePrintingEnabled = True
        self.__ackPrintingEnabled = True
        self.__commandPrintingEnabled = True
        self.captures = []
        self.enable()

    def enable(self):
        logger.info("Dissector enabled")
        self.__enabled = True
    def disable(self):
        logger.info("Dissector disabled")
        self.__enabled = False
    def isEnabled(self):
        return self.__enabled
    
    def setAnnotation(self, annotation):
        self.__annotation = annotation

        
    def printAllFrames(self):
        print "Printing all captures"
        print "-"*40
        for capture in self.captures:
            print  capture
    
        print "-"*40
        sys.stdout.flush()
        
    @staticmethod
    def handleCustomFrames(sniffedPacket):
        pdu = sniffedPacket.get_macPDU()
        (debugString,) = struct.unpack_from("<5s", pdu, 0)

        # For example, I have implemented a generic debug packet that gets sent
        # whenever there is an assert in my code. It takes control of the 
        # radio, builds a frame with info about the assert, sends it and then
        # resets the chip.
        if ("Debug" == debugString):
            (payloadVersion, ) = struct.unpack_from("<B", pdu, 5)

            if payloadVersion is 0:
                stats["Custom frames"] += 1
                (date, lineNum, code) = struct.unpack_from("<6sHB", pdu, 6)
                #                'Debug', version,  'date12', Line num, code, fcs
                #                 12345 ,  6     ,   789012 , 34      , 5
                nameLength = len(pdu) - 5 - 1 - 6 - 2 - 1 - 2
                (fileName,) = struct.unpack_from("<%ds" % nameLength, pdu, 15)
                
                return CustomAssertFrame(date, code, lineNum, fileName)

        return None # the frame was NOT consumed
          
    def handleSniffedPacket(self, sniffedPacket):
        if self.__enabled is False:
            return

        try:
            if (None == sniffedPacket) or (len(sniffedPacket.get_macPDU()) < 2):
                return


            (rssiSniff, corr, crc_ok) = self.checkPacket(sniffedPacket.get_macPDU())

            if crc_ok is False:
                stats["CRC Errors"] += 1
                return

            customFrame = self.handleCustomFrames(sniffedPacket)
            if customFrame is not None:
                # A custom, non-802.15.4 frame was received and processed
                capture = CapturedFrame(customFrame, rssiSniff, self.__annotation)
                self.captures.append(capture)
                print capture
                sys.stdout.flush()
                
            else:
                frame = ieee.IEEE15dot4FrameFactory.parse(sniffedPacket)
                capture = CapturedFrame(frame, rssiSniff, self.__annotation)
                
                if capture is not None:
                    self.captures.append(capture)
                    # print capture
                    # hack here!
                    sys.stdout.flush()
    
                stats[ieee.FrameType.toString(frame.fcf.frametype)] += 1
                stats['Dissected'] += 1
            
        except Exception as e:
            logger.warn("Error dissecting frame.")
            logger.warn("The error was: %s" % (e.args))
            stats["Dissection errors"] += 1

    @staticmethod
    def checkPacket(packet):
        # used to derive other values
        fcs1, fcs2 = packet[-2:]

        # rssi is the signed value at fcs1
        rssi    = (fcs1 + 2**7) % 2**8 - 2**7  - 73

        # crc ok is the 7th bit in fcs2
        crc_ok  = fcs2 & (1 << 7) > 0

        # correlation value is the unsigned 0th-6th bit in fcs2
        corr    = fcs2 & 0x7f

        return (rssi, corr, crc_ok)



class CC2531EMK:
    """CC2531EMK is used to manage the USB device.
    """
    DEFAULT_CHANNEL = 11

    DATA_EP = 0x83
    DATA_TIMEOUT = 2500

    DIR_OUT = 0x40
    DIR_IN = 0xc0

    GET_IDENT = 0xc0
    SET_POWER = 0xc5
    GET_POWER = 0xc6

    SET_START = 0xd0  # bulk in starts
    SET_STOP = 0xd1  # bulk in stops
    SET_CHAN = 0xd2  # 0x0d (idx 0) + data)0x00 (idx 1)

    COMMAND_FRAME = 0x00
#     COMMAND_CHANNEL = ??

    def __init__(self, callback, channel=DEFAULT_CHANNEL):
        """Create a new CC2531EMK manager object
        
        This constructor consumes the first sniffer available on the USB bus.
            
        Args:
            callback(func): A function that will handle any received packets, 
                            with a signature (timestamp, frame).
            channel(int): The channel to sniff on.
        """
        
        self.dev = None
        self.channel = channel
        self.callback = callback
        self.thread = None
        self.running = False

        stats['Captured'] = 0
        stats['Non-Frame'] = 0
        
        if self.callback is None:
            raise ValueError("A valid callback must be provided")
        if len(inspect.getargspec(self.callback)[0]) < 2:
            raise ValueError("Callback must have at least 2 arguments")
        
        try:
            self.dev = usb.core.find(idVendor=0x0451, idProduct=0x16ae)
        except usb.core.USBError:
            raise OSError("Permission denied, you need to add an udev rule for this device", errno=errno.EACCES)

        if self.dev is None:
            raise IOError("Device not found")

        self.dev.set_configuration() # must call this to establish the USB's "Config"
        self.name = usb.util.get_string(self.dev, 256, 2) # get name from USB descriptor
        self.ident = self.dev.ctrl_transfer(CC2531EMK.DIR_IN, CC2531EMK.GET_IDENT, 0, 0, 256) # get identity from Firmware command

        # power on radio, wIndex = 4
        self.dev.ctrl_transfer(CC2531EMK.DIR_OUT, CC2531EMK.SET_POWER, wIndex=4)

        while True:
            # check if powered up
            power_status = self.dev.ctrl_transfer(CC2531EMK.DIR_IN, CC2531EMK.GET_POWER, 0, 0, 1)
            if power_status[0] == 4: break
            time.sleep(0.1)

        self.set_channel(channel)

    def __del__(self):
        if self.dev:
            # power off radio, wIndex = 0
            self.dev.ctrl_transfer(self.DIR_OUT, self.SET_POWER, wIndex=0)

    def start(self):
        # start sniffing
        self.running = True
        self.dev.ctrl_transfer(CC2531EMK.DIR_OUT, CC2531EMK.SET_START)
        self.thread = threading.Thread(target=self.recv)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        # end sniffing
        self.running = False
        self.thread.join()
        self.dev.ctrl_transfer(CC2531EMK.DIR_OUT, CC2531EMK.SET_STOP)

    def isRunning(self):
        return self.running

    def recv(self):

        # While the running flag is set, continue to read from the USB device
        while self.running:
            bytesteam = self.dev.read(CC2531EMK.DATA_EP, 4096, timeout=CC2531EMK.DATA_TIMEOUT)
#             print "RECV>> %s" % binascii.hexlify(bytesteam)

            if len(bytesteam) >= 3:
                (cmd, cmdLen) = struct.unpack_from("<BH", bytesteam)
                bytesteam = bytesteam[3:]
                if len(bytesteam) == cmdLen:
                    # buffer contains the correct number of bytes
                    if CC2531EMK.COMMAND_FRAME == cmd:
                        logger.info('Read a frame of size %d' % (cmdLen,))
                        stats['Captured'] += 1
                        (timestamp, pktLen) = struct.unpack_from("<IB", bytesteam)
                        frame = bytesteam[5:]

                        if len(frame) == pktLen:
                            self.callback(timestamp, frame)
                        else:
                            logger.warn("Received a frame with incorrect length, pkgLen:%d, len(frame):%d" %(pktLen, len(frame)))
                            stats['Non-Frame'] += 1

#                     elif cmd == CC2531EMK.COMMAND_CHANNEL:
#                         logger.info('Received a command response: [%02x %02x]' % (cmd, bytesteam[0]))
#                         # We'll only ever see this if the user asked for it, so we are
#                         # running interactive. Print away
#                         print 'Sniffing in channel: %d' % (bytesteam[0],)
#                     else:
#                         logger.warn("Received a command response with unknown code - CMD:%02x byte:%02x]" % (cmd, bytesteam[0]))


    def set_channel(self, channel):
        was_running = self.running

        if 11 <= channel <= 26:
            if self.running:
                self.stop()

            self.channel = channel

            # set channel command
            self.dev.ctrl_transfer(CC2531EMK.DIR_OUT, CC2531EMK.SET_CHAN, 0, 0, [channel])
            self.dev.ctrl_transfer(CC2531EMK.DIR_OUT, CC2531EMK.SET_CHAN, 0, 1, [0x00])

            self.get_channel()

            if was_running:
                self.start()

        else:
            raise ValueError("Channel must be between 11 and 26")

    def get_channel(self):
        return self.channel

    def __repr__(self):
        if self.dev:
            return "%s <Channel: %d>" % (self.name, self.channel)
        else:
            return "Not connected"

def arg_parser():
    debug_choices = ('DEBUG', 'INFO', 'WARN', 'ERROR')

    parser = argparse.ArgumentParser(add_help = False,
                                     description = 'Read IEEE802.15.4 frames \
    from a CC2531EMK packet sniffer device, parse them and dispay them in text.')

    in_group = parser.add_argument_group('Input Options')
    in_group.add_argument('-c', '--channel', type = int, action = 'store',
                          choices = range(11, 27),
                          default = defaults['channel'],
                          help = 'Set the sniffer\'s CHANNEL. Valid range: 11-26. \
                                  (Default: %s)' % (defaults['channel'],))
    in_group.add_argument('-a', '--annotation', type = types.StringType,
                          help = 'Include a free-form annotation on every capture.')

    log_group = parser.add_argument_group('Verbosity and Logging')
    log_group.add_argument('-r', '--rude',
                           action = 'store_true',
                           default = False,
                           help = 'Run in non-interactive mode, without \
                                   accepting user input. (Default Disabled)')
    log_group.add_argument('-D', '--debug-level',
                           action = 'store',
                           choices = debug_choices,
                           default = defaults['debug_level'],
                           help = 'Print messages of severity DEBUG_LEVEL \
                                   or higher (Default %s)'
                                   % (defaults['debug_level'],))
    log_group.add_argument('-L', '--log-file',
                           action = 'store',
                           nargs = '?',
                           const = defaults['log_file'],
                           default = False,
                           help = 'Log output in LOG_FILE. If -L is specified \
                                   but LOG_FILE is omitted, %s will be used. \
                                   If the argument is omitted altogether, \
                                   logging will not take place at all.'
                                   % (defaults['log_file'],))
    log_group.add_argument('-l', '--log-level',
                           action = 'store',
                           choices = debug_choices,
                           default = defaults['log_level'],
                           help = 'Log messages of severity LOG_LEVEL or \
                                   higher. Only makes sense if -L is also \
                                   specified (Default %s)'
                                   % (defaults['log_level'],))

    gen_group = parser.add_argument_group('General Options')
    gen_group.add_argument('-v', '--version', action = 'version',
                           version = 'pyCCSniffer v%s' % (__version__))
    gen_group.add_argument('-h', '--help', action = 'help',
                           help = 'Shows this message and exits')

    return parser.parse_args()

def dump_stats():
    s = StringIO.StringIO()

    s.write('Frame Stats:\n')
    for k, v in stats.items():
        s.write('%20s: %d\n' % (k, v))

    print(s.getvalue())

def log_init():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, args.debug_level))
    cf = logging.Formatter('%(message)s')
    ch.setFormatter(cf)
    logger.addHandler(ch)

    if args.log_file is not False:
        fh = logging.handlers.RotatingFileHandler(filename = args.log_file,
                                                  maxBytes = 5000000)
        fh.setLevel(getattr(logging, args.log_level))
        ff = logging.Formatter(
            '%(asctime)s - %(levelname)8s - %(message)s')
        fh.setFormatter(ff)
        logger.addHandler(fh)

if __name__ == '__main__':
    args = arg_parser()
    args.channel=int(12)
    log_init()

    logger.info('Started logging')
    start_datetime = datetime.now()

    packetHandler = PacketHandler()
    packetHandler.enable()

    if args.annotation is not None:
        packetHandler.setAnnotation(args.annotation)

    print('target game')
        
    # Create a list of handlers to dispatch to, NB: handlers must have a "handleSniffedPacket" method
    handlers = [packetHandler]
    def handlerDispatcher(timestamp, macPDU):
        """ Dispatches any received packets to all registered handlers
        Args:
            timestamp: The timestamp the packet was received, as reported by 
                       the sniffer device, in microseconds.
            macPDU: The 802.15.4 MAC-layer PDU, starting with the Frame Control 
                    Field (FCF).
        """
        if len(macPDU) > 0:
            packet = SniffedPacket(macPDU, timestamp)
            for handler in handlers:
                handler.handleSniffedPacket(packet)

    snifferDev = CC2531EMK(handlerDispatcher, args.channel)
    snifferDev.start()

    print 'Target guns:'
    print 'enter VIP 1:'
    gun1 = raw_input('')
    if '' == gun1: sys.exit(0)
    gun1=int(gun1)
    print 'enter VIP 2:'
    gun2 = raw_input('')
    if '' == gun2: gun2=999
    gun2=int(gun2)
    print

    redGun=gun1
    blueGun=gun2

    os.system('ipython GunSettings/vanilla1.py')
    os.system('ipython GunSettings/HungerGames.py %i %i' % (gun1,gun2))

    # execute NEW GAME
    os.system('ipython GunSettings/newGame.py')

    if np.random.random(1) > 0.5:
        os.system('ipython GunSettings/endGame.py %i' % gun1)
        gunOn=gun2;gunOff=gun1
    else:
        os.system('ipython GunSettings/endGame.py %i' % gun2)
        gunOn=gun1;gunOff=gun2

    lastSwitchRed=0;lastSwitchBlue=0

    try:
        while 1: 
            time.sleep(0.1)
            blueHits=0
            redHits=0

            for ii in packetHandler.captures:
                if len(ii.frame.msdu) < 5: continue

                if (ii.frame.msdu[2] == 20 or ii.frame.msdu[2] == 17 or 
                    ii.frame.msdu[2] == 16 or ii.frame.msdu[2] == 21) and \
                    (ii.frame.msdu[3] == redGun or ii.frame.msdu[3] == blueGun) \
                    and ii.frame.msdu[4] % 2 == 1:
                        redHits += 1

                if (ii.frame.msdu[2] == 20 or ii.frame.msdu[2] == 17 or 
                    ii.frame.msdu[2] == 16 or ii.frame.msdu[2] == 21) and \
                    (ii.frame.msdu[3] == redGun or ii.frame.msdu[3] == blueGun) \
                    and ii.frame.msdu[4] % 2 == 0:
                        blueHits += 1
                   
            if redHits > 99:
                print 'Red Wins! (%i to %i)' % (blueHits,redHits)
                break
            if blueHits > 99:
                print 'Blue Wins! (%i to %i)' % (blueHits,redHits)
                break

            
            if redHits > lastSwitchRed + 15 or blueHits > lastSwitchBlue + 15:
                gunOn,gunOff = gunOff,gunOn
                os.system('ipython GunSettings/endGame.py %i' % gunOff)
                os.system('ipython GunSettings/newGame.py %i' % gunOn)
                lastSwitchBlue = blueHits
                lastSwitchRed = redHits
                print 'redHits, blueHits = %i, %i' %(redHits,blueHits)

            if (redHits > lastSwitchRed + 9 or blueHits > lastSwitchBlue + 9) and \
                np.random.random(1) < 0.01:
                    gunOn,gunOff = gunOff,gunOn
                    os.system('ipython GunSettings/endGame.py %i' % gunOff)
                    os.system('ipython GunSettings/newGame.py %i' % gunOn)
                    lastSwitchBlue = blueHits
                    lastSwitchRed = redHits
                    print 'redHits, blueHits = %i, %i' %(redHits,blueHits)

    except (KeyboardInterrupt, SystemExit):
        pass

    logger.info('Shutting down')
    if snifferDev.isRunning():
        snifferDev.stop()
        
    os.system('ipython GunSettings/endGame.py')
