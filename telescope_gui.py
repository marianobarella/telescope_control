#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nov 25 2020

Telescope control GUI
Right-ascension and declination remote control
Instructions are sent/received to an Arduino MEGA/Uno board
An L293D motor shield powered with a 12 V supply controls 2 DC motors, one for 
each axis

@author: Mariano Barella
marianobarella@gmail.com

"""

#import sys
#from datetime import datetime

import ArduinoCommunication as ardcom
#
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

def checkSpeed(speed):
    checkedSpeed = 0
    if speed < -255:
        print("\nSpeed can't be LOWER than -255")
        print("Forcing speed to -255")
        checkedSpeed = -255
    elif speed > 255:
        print("\nSpeed can't be HIGHER than +255")
        print("Forcing speed to +255")
        checkedSpeed = 255
    else:
        checkedSpeed = speed
    return checkedSpeed

def setDarkTheme():
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15,15,15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142,45,197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    return(palette)

class Frontend(QtGui.QFrame):

    setDoSignal = pyqtSignal(list)
    initSerialSignal = pyqtSignal(list)
    closeSerialSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Frontend, self).__init__(*args, **kwargs)

        self.setWindowTitle("Telescope control")

        self.currentSpeed = [0, 0]
        self.degSpeed = [0,0]        
        
        self.setUpGUI()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateSpeedLabels)
    
    # Signal of serial comm buttons -------------------------------------------
    
    def initSerialAction(self):
        serialParams = [self.cBoxPort.currentText(), int(self.cBoxBaud.currentText())]
        if self.initSerialButton.isChecked:
           self.initSerialSignal.emit(serialParams)
           updateInterval = 100 # in milliseconds
           self.timer.start(updateInterval) # upodate every 100 milliseconds
           print('\nTimer on. Updating speed every %d ms.' % updateInterval)

    def closeSerialAction(self):
        if self.closeSerialButton.isChecked:
           self.closeSerialSignal.emit()
           self.timer.stop()
           print('\nTimer has been stopped.')
        
    # Set speed signals

    def setRADoAction(self):
        setDo = ['RA', int(self.raLabel.text())]
        if self.setRADoButton.isChecked:
           self.setDoSignal.emit(setDo)
           self.currentSpeed[0] = setDo[1]
           
    def setDECDoAction(self):
        setDo = ['DEC', int(self.decLabel.text())]
        if self.setDECDoButton.isChecked:
           self.setDoSignal.emit(setDo)
           self.currentSpeed[1] = setDo[1]
   
    def stopRAAction(self):
        setDo = ['RA', int(0)]
        if self.stopRAButton.isChecked:
           self.setDoSignal.emit(setDo)
           self.currentSpeed[0] = setDo[1]
           
    def stopDECAction(self):
        setDo = ['DEC', int(0)]
        if self.stopDECButton.isChecked:
           self.setDoSignal.emit(setDo)
           self.currentSpeed[1] = setDo[1]
           
    # Incremental and decremental signals       
           
    def add1RASpeed(self):
        newSpeed = int(self.currentSpeed[0] + 1)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['RA', checkedSpeed]
        if self.add1RAButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[0] = setDo[1]

    def add10RASpeed(self):
        newSpeed = int(self.currentSpeed[0] + 10)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['RA', checkedSpeed]
        if self.add10RAButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[0] = setDo[1]

    def sub1RASpeed(self):
        newSpeed = int(self.currentSpeed[0] - 1)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['RA', checkedSpeed]
        if self.sub1RAButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[0] = setDo[1]
            
    def sub10RASpeed(self):
        newSpeed = int(self.currentSpeed[0] - 10)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['RA', checkedSpeed]
        if self.sub10RAButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[0] = setDo[1]
            
    def add1DECSpeed(self):
        newSpeed = int(self.currentSpeed[1] + 1)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['DEC', checkedSpeed]
        if self.add1DECButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[1] = setDo[1]

    def add10DECSpeed(self):
        newSpeed = int(self.currentSpeed[1] + 10)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['DEC', checkedSpeed]
        if self.add10DECButton.isChecked:   
            self.setDoSignal.emit(setDo)
            self.currentSpeed[1] = setDo[1]

    def sub1DECSpeed(self):
        newSpeed = int(self.currentSpeed[1] - 1)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['DEC', checkedSpeed]
        if self.sub1DECButton.isChecked:   
            self.setDoSignal.emit(setDo)   
            self.currentSpeed[1] = setDo[1]
            
    def sub10DECSpeed(self):
        newSpeed = int(self.currentSpeed[1] - 10)
        checkedSpeed = checkSpeed(newSpeed)
        setDo = ['DEC', checkedSpeed]
        if self.sub10DECButton.isChecked:   
            self.setDoSignal.emit(setDo) 
            self.currentSpeed[1] = setDo[1]
    
    # Define Graphical User Interface       

    def updateSpeedLabels(self):
        self.degSpeed[0] = self.currentSpeed[0]*float(self.raCal.text())*1000 # to account for prefix in self.RAcurrentSpeedDegLabel
        self.degSpeed[1] = self.currentSpeed[1]*float(self.raCal.text())*1000 # to account for prefix in self.DECcurrentSpeedDegLabel
        self.RAcurrentSpeedLabel.setText("<strong>%d" % self.currentSpeed[0])
        self.DECcurrentSpeedLabel.setText("<strong>%d" % self.currentSpeed[1])
        self.RAcurrentSpeedDegLabel.setText("<strong>%.2f" % self.degSpeed[0])
        self.DECcurrentSpeedDegLabel.setText("<strong>%.2f" % self.degSpeed[1])

    def setUpGUI(self):
        
        # Current speed and calibration ---------------------------------------
        
        self.currentSpeedWidget = QtGui.QWidget()
        layoutGrid3 = QtGui.QGridLayout()
        self.currentSpeedWidget.setLayout(layoutGrid3)
        layoutGrid3.addWidget(QtGui.QLabel("<strong>Current speed"), 1, 1)
        #.......
        layoutGrid3.addWidget(QtGui.QLabel("R.A."), 2, 1)
        self.RAcurrentSpeedLabel = QtGui.QLabel("<strong>%d" % self.currentSpeed[0])
        self.RAcurrentSpeedLabel.setStyleSheet('font-size: 30px')
        layoutGrid3.addWidget(self.RAcurrentSpeedLabel, 2, 2)
        layoutGrid3.addWidget(QtGui.QLabel("R.A. in mrad/min"), 3, 1)
        self.RAcurrentSpeedDegLabel = QtGui.QLabel("<strong>%.2f" % self.degSpeed[0])
        self.RAcurrentSpeedDegLabel.setStyleSheet('font-size: 30px')
        layoutGrid3.addWidget(self.RAcurrentSpeedDegLabel, 3, 2)
        layoutGrid3.addWidget(QtGui.QLabel("R.A. cal"), 4, 1)
        self.raCal = QtGui.QLineEdit("0.000136")
        layoutGrid3.addWidget(self.raCal, 4, 2)
        
        # Right-ascension
        self.raLabel = QtGui.QLineEdit("0")
        self.decLabel = QtGui.QLineEdit("0")
        #.......
        layoutGrid3.addWidget(QtGui.QLabel("Dec"), 2, 3)
        self.DECcurrentSpeedLabel = QtGui.QLabel("<strong>%d" % self.currentSpeed[1])
        self.DECcurrentSpeedLabel.setStyleSheet('font-size: 30px')
        layoutGrid3.addWidget(self.DECcurrentSpeedLabel, 2, 4)
        layoutGrid3.addWidget(QtGui.QLabel("Dec in mrad/min"), 3, 3)
        self.DECcurrentSpeedDegLabel = QtGui.QLabel("<strong>%.2f" % self.degSpeed[1])
        self.DECcurrentSpeedDegLabel.setStyleSheet('font-size: 30px')
        layoutGrid3.addWidget(self.DECcurrentSpeedDegLabel, 3, 4)
        layoutGrid3.addWidget(QtGui.QLabel("Dec cal"), 4, 3)
        self.decCal = QtGui.QLineEdit("0")
        layoutGrid3.addWidget(self.decCal, 4, 4)
        
        # Set speed - Interface and buttons -----------------------------------

        self.setSpeedWidget = QtGui.QWidget()
        
        layoutGrid1 = QtGui.QGridLayout()
        self.setSpeedWidget.setLayout(layoutGrid1)
        
        layoutGrid1.addWidget(QtGui.QLabel("R.A."), 1, 1)
        layoutGrid1.addWidget(QtGui.QLabel("Dec"), 2, 1)
        
        # Right-ascension
        self.raLabel = QtGui.QLineEdit("0")
        self.decLabel = QtGui.QLineEdit("0")
        self.setRADoButton = QtGui.QPushButton("Set R.A.")
        # IMPORTANT: connection here!
        self.setRADoButton.pressed.connect(self.setRADoAction)
        self.stopRAButton = QtGui.QPushButton("Stop R.A.")
        self.stopRAButton.setStyleSheet("QPushButton\
                             {background-color : firebrick;\
                             color: white}"
                             ) 
        self.stopRAButton.pressed.connect(self.stopRAAction)

        # Declination
        self.setDECDoButton = QtGui.QPushButton("Set Dec")
        # IMPORTANT: connection here!
        self.setDECDoButton.pressed.connect(self.setDECDoAction)
        
        self.stopDECButton = QtGui.QPushButton("Stop Dec")
        self.stopDECButton.setStyleSheet("QPushButton\
                             {background-color : firebrick;\
                             color: white}"
                             ) 
        self.stopDECButton.pressed.connect(self.stopDECAction)
        
        layoutGrid1.addWidget(self.raLabel, 1, 2)
        layoutGrid1.addWidget(self.decLabel, 2, 2)
        layoutGrid1.addWidget(self.setRADoButton, 1, 3)
        layoutGrid1.addWidget(self.setDECDoButton, 2, 3)
        layoutGrid1.addWidget(self.stopRAButton, 1, 4)
        layoutGrid1.addWidget(self.stopDECButton, 2, 4)
        
        # Easy set speed buttons ----------------------------------------------

        self.RALabel = QtGui.QLabel('R.A.')
        self.DECLabel = QtGui.QLabel('Dec')
        self.add1RAButton = QtGui.QPushButton("+1 ▲")
        self.add10RAButton = QtGui.QPushButton("+10 ▲▲")
        self.sub1RAButton = QtGui.QPushButton("-1 ▼")
        self.sub10RAButton = QtGui.QPushButton("-10 ▼▼")
        self.add1DECButton = QtGui.QPushButton("+1 ▲")
        self.add10DECButton = QtGui.QPushButton("+10 ▲▲")
        self.sub1DECButton = QtGui.QPushButton("-1 ▼")
        self.sub10DECButton = QtGui.QPushButton("-10 ▼▼")
        # IMPORTANT: connections here!
        self.add1RAButton.pressed.connect(self.add1RASpeed)
        self.add10RAButton.pressed.connect(self.add10RASpeed)
        self.sub1RAButton.pressed.connect(self.sub1RASpeed)
        self.sub10RAButton.pressed.connect(self.sub10RASpeed)
        self.add1DECButton.pressed.connect(self.add1DECSpeed)
        self.add10DECButton.pressed.connect(self.add10DECSpeed)
        self.sub1DECButton.pressed.connect(self.sub1DECSpeed)
        self.sub10DECButton.pressed.connect(self.sub10DECSpeed)

        self.easySpeedWidget = QtGui.QWidget()
        layoutGrid0 = QtGui.QGridLayout()
        self.easySpeedWidget.setLayout(layoutGrid0)
        
        layoutGrid0.addWidget(self.RALabel,        1, 1)
        layoutGrid0.addWidget(self.add1RAButton,    1, 2)
        layoutGrid0.addWidget(self.add10RAButton,  1, 3)
        layoutGrid0.addWidget(self.sub1RAButton,    2, 2)
        layoutGrid0.addWidget(self.sub10RAButton,  2, 3)
        layoutGrid0.addWidget(self.DECLabel,        3, 1)
        layoutGrid0.addWidget(self.add1DECButton,    3, 2)
        layoutGrid0.addWidget(self.add10DECButton,  3, 3)
        layoutGrid0.addWidget(self.sub1DECButton,    4, 2)
        layoutGrid0.addWidget(self.sub10DECButton,  4, 3)

        # Serial - Interface and buttons -------------------------------------
        
        self.serialWidget = QtGui.QWidget()
        layoutGrid2 = QtGui.QGridLayout()
        self.serialWidget.setLayout(layoutGrid2)
        
        self.cBoxPort = QtGui.QComboBox()
        listOfAvailablePorts = ardcom.serial_ports()
        self.cBoxPort.addItems(listOfAvailablePorts)
        layoutGrid2.addWidget(QtGui.QLabel("Port:"), 1, 1)
        layoutGrid2.addWidget(self.cBoxPort, 1, 2)
        
        self.cBoxBaud = QtGui.QComboBox()
        self.cBoxBaud.addItems(ardcom.baudRateList)
        self.cBoxBaud.setCurrentIndex(4)
        layoutGrid2.addWidget(QtGui.QLabel("Baud rate:"), 2, 1)
        layoutGrid2.addWidget(self.cBoxBaud, 2, 2)
        
        self.initSerialButton = QtGui.QPushButton("Connect")
        # IMPORTANT: connection here!
        self.initSerialButton.pressed.connect(self.initSerialAction)
        self.closeSerialButton = QtGui.QPushButton("Close")
        # IMPORTANT: connection here!
        self.closeSerialButton.pressed.connect(self.closeSerialAction)
        layoutGrid2.addWidget(self.initSerialButton, 1, 3)
        layoutGrid2.addWidget(self.closeSerialButton, 2, 3)

        # Make docks ----------------------------------------------------------
        
        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()

        # Serial dock
        serialDock = Dock('Serial com', size=(1, 1))
        serialDock.addWidget(self.serialWidget)
        dockArea.addDock(serialDock)

        # Speed dock
        setSpeedDock = Dock('Speed', size=(1, 1))
        setSpeedDock.addWidget(self.currentSpeedWidget)
        setSpeedDock.addWidget(self.setSpeedWidget)
        setSpeedDock.addWidget(self.easySpeedWidget)
        dockArea.addDock(setSpeedDock)
        
        hbox.addWidget(dockArea)
        self.setLayout(hbox)

class Backend(QtCore.QObject):

#    read_pos_signal = pyqtSignal(list)
#    reference_signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)
     
    @pyqtSlot(list)
    def initSerialComm(self, serialInfo):
        ser = ardcom.initSerial(serialInfo[0], serialInfo[1])
        return ser
        
#    @pyqtSlot()
#    def set_reference(self): 
#        
#        x_pos, y_pos, z_pos = self.read_pos()
#        self.reference_signal.emit([x_pos, y_pos, z_pos])
        
    @pyqtSlot(list)
    def connectSerial(self, serialParams):
        # serialParams is a list containing
        # port (string) at serialParams[0]
        # baud rate (int) at serialParams[1]
        self.ser = ardcom.initSerial(serialParams[0], serialParams[1])
        print('\nSerial port opened:', self.ser.isOpen(), '\n')
        ardcom.waitForArduino(self.ser)
        
    @pyqtSlot()
    def closeSerial(self):
        # serialParams is a list containing
        # port (string) at serialParams[0]
        # baud rate (int) at serialParams[1]
        self.ser.close()
        print('\nSerial port opened:', self.ser.isOpen(), '\n')            

    @pyqtSlot(list)
    def setDo(self, axisAndSpeed):
        # axisAndSpeed is a list containing
        # axis at axisAndSpeed[0]
        # speeed at axisAndSpeed[1]
        checkedSpeed = checkSpeed(axisAndSpeed[1])
        axisAndSpeed[1] = checkedSpeed
        self.setSpeed(axisAndSpeed)
        print("Speed set OK")

    def setSpeed(self, axisAndSpeed):
        """Set the speed of a given axis to the specified value"""

        command = "<%s,%d>" % (axisAndSpeed[0], axisAndSpeed[1])
        ardcom.sendCommand(command, self.ser)
#
#    @pyqtSlot()
#    def close(self, ser):
#        ardcom.closeSerial(ser)
#        self.close() 

    def make_connection(self, frontend):
#        frontend.read_pos_button_signal.connect(self.read_pos)
#        frontend.move_signal.connect(self.move)
        frontend.setDoSignal.connect(self.setDo)
        frontend.initSerialSignal.connect(self.connectSerial)
#        frontend.set_reference_signal.connect(self.set_reference)
        frontend.closeSerialSignal.connect(self.closeSerial)

# Define main

if __name__ == '__main__':

    app = QtGui.QApplication([])
    
    # dark theme
    app.setStyle('Fusion')
    darkPalette = setDarkTheme()
    app.setPalette(darkPalette)
    
    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)

    telescopeControlThread = QtCore.QThread()
    worker.moveToThread(telescopeControlThread)
    telescopeControlThread.start()

    gui.show()
    app.exec_()
    
#    sys.exit(app.exec_())