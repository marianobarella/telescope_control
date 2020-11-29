#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nov 24 2020

Arduino communication module
Send and receive instructions to an Arduino MEGA/Uno board that has a
L293D motor shield powered with a 12 V supply to control 2 DC motors

The key functions are:
- sendToArduino(str, serialInstance) which sends the given string to the Arduino. 
The string may contain characters with any of the values 0 to 255.

- recvFromArduino(serialInstance)  which returns an array. The first element 
contains the number of bytes that the Arduino said it included in message. This
can be used to check that the full message was received. The second element 
contains the message as a string.

The message to be sent to the Arduino starts with < and ends with >
The message content comprises a string and an integer. 
String = axis ("DEC" or "RA")
Integer = speed (between -255 and +255)
The numbers are sent as their ascii equivalents.
For example, "<DEC,200>" (set declination axis speed to 200)

Receiving a message from the Arduino involves waiting until the startMarker is 
detected and saving all subsequent bytes until the end marker is detected.

NOTES:
- This program does not include any timeouts to deal with delays in communication
- For simplicity the program does NOT search for the comm port (although a 
function that scan serial ports available is included). The user must modify the
code to include the correct reference. Search for the lines:
       serPort = "/dev/ttyACM0"
       baudRate = 9600
       ser = serial.Serial(serPort, baudRate)
- This code was based on Robin2 python script at https://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764
and tfeldmann answer at https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

@author: Mariano Barella
marianobarella@gmail.com

"""

import time
import sys
import glob
import serial

startMarker = 60
endMarker = 62

baudRateIntList = [300, 1200, 2400, 4800, 9600, 19200, 
                   38400, 57600, 74880, 115200, 230400, 
                   250000, 500000, 1000000, 2000000]

baudRateList = [str(i) for i in baudRateIntList]

#=====================================

#  Function Definitions

#=====================================

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

#======================================

def sendToArduino(sendStr, ser):
    ser.write(sendStr.encode('utf-8'))

#======================================

def recvFromArduino(serialInstace):
    global startMarker, endMarker
    
    ck = ""
    x = "z" # any value that is not an endMarker or startMarker
    byteCount = -1 # to allow for the fact that the last increment will be one too many
    
    # wait for the start character
    while  ord(x) != startMarker: 
        x = serialInstace.read()
    
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x.decode("utf-8")
            byteCount += 1
        x = serialInstace.read()
    
    return(ck)


#============================

def waitForArduino(serialInstace):

    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

        while serialInstace.inWaiting() == 0:
            pass
        
        msg = recvFromArduino(serialInstace)

        print (msg)
        print ()
        
#======================================

def sendCommand(command, serialInstace):
    waitingForReply = False

    if waitingForReply == False:
        sendToArduino(command, serialInstace)
        print ("Command sent: " + command)
        waitingForReply = True

    if waitingForReply == True:

        while serialInstace.inWaiting() == 0:
            pass
        
        dataRecvd = recvFromArduino(serialInstace)
        print ("Reply Received: " + dataRecvd)

        waitingForReply = False

        print ("===========\n")
    
#======================================
        
def sendListOfCommand(td, serialInstace):
    numLoops = len(td)
    waitingForReply = False

    n = 0
    while n < numLoops:
        command = td[n]

        if waitingForReply == False:
            sendToArduino(command, serialInstace)
            print ("Command sent: " + command)
            waitingForReply = True

        if waitingForReply == True:

            while serialInstace.inWaiting() == 0:
                pass
            
            dataRecvd = recvFromArduino(serialInstace)
            print ("Reply Received: " + dataRecvd)
            n += 1
            waitingForReply = False

            print ("===========\n")
        
        #TODO remove sleep
        time.sleep(2)

#======================================

def initSerial(port, baudRate):
    ser = serial.Serial(port, baudRate)
    return(ser)

#======================================


def closeSerial(serialInstance):
    serialInstance.close()

#======================================
    
if __name__ == '__main__':
    
    print ()
    
    serPort = "/dev/ttyACM0"
    baudRate = 9600
    ser = initSerial(serPort, baudRate)
    print ("Serial port " + serPort + " opened. Baud rate: " + str(baudRate))
        
    waitForArduino(ser)
       
    testData = []
    #testData.append("<DEC,-100>")
    testData.append("<DEC,-255>")
    #testData.append("<DEC,0>")
    #testData.append("<RA,-100>")
    testData.append("<RA,-255>")
    #
    #
    testData.append("<RA,0>")
    testData.append("<DEC,0>")
    
    sendListOfCommand(testData, ser)
    
#    closeSerial(ser)
