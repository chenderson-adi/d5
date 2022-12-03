#HMI PII code designed for 800X480
import sys
import os
import time
import serial
import math
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import Qt,pyqtSignal,QTime,QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget,QTreeWidget,QTreeWidgetItem
from configparser import ConfigParser
from PyQt5.uic import loadUi
from threading import Thread
import queue as Queue
from datetime import datetime
#https://iosoft.blog/2019/04/30/pyqt-serial-terminal/


SER_TIMEOUT = 0.1                   # Timeout for serial Rx
RETURN_CHAR = "\n"                  # Char to be sent when Enter key pressed
PASTE_CHAR  = "\x16"                # Ctrl code for clipboard paste
baudrate    = 9600                # Default baud rate
winportname    = "COM3"                # Default port name
linuxportname    = "/dev/ttyUSB0"                # Default port name
hexmode     = False                 # Flag to enable hex display


#*******************************************************************************Main Window*******************************************************************************
class clsMainWindow(QWidget):
    def __init__(self):
        #super(clsMainWindow, self).__init__()
        super().__init__()
        self.SetupUI()
    def SetupUI(self):
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'MainWindow.ui'),self)
        #self.lblElapsedTime.setText("")
        self.cmdLogin.clicked.connect(self.gotoLogin)
        self.cmdSetup.clicked.connect(self.gotoSetupWindow)
        self.cmdAdvanced.clicked.connect(self.gotoAdvancedWindow)
        self.cmdMKeyPadDelete.clicked.connect(lambda: self.gotoDataDelete(self.lblNewpos.text(),self.lblNewpos))
        self.cmdMKeyPadGo.clicked.connect(lambda: self.gotoDataEntry(self.lblNewpos.text(),self.lblPos,self.lblNewpos,self.lblMKeyPadError,self.lblPosu.text()))
        self.cmdHome.clicked.connect(lambda: self.gotoXRHome(self.lblPos))
        self.cmdLight.clicked.connect(self.gotoLightToggle)
        self.cmd1.clicked.connect(lambda: self.gotoEnterDigit("1",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd2.clicked.connect(lambda: self.gotoEnterDigit("2",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd3.clicked.connect(lambda: self.gotoEnterDigit("3",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd4.clicked.connect(lambda: self.gotoEnterDigit("4",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd5.clicked.connect(lambda: self.gotoEnterDigit("5",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd6.clicked.connect(lambda: self.gotoEnterDigit("6",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd7.clicked.connect(lambda: self.gotoEnterDigit("7",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd8.clicked.connect(lambda: self.gotoEnterDigit("8",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd9.clicked.connect(lambda: self.gotoEnterDigit("9",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        self.cmd0.clicked.connect(lambda: self.gotoEnterDigit("0",self.lblNewpos.text(),self.lblNewpos,self.lblMKeyPadError))
        #self.cmdUnit.clicked.connect(lambda: self.gotoChangeMeasurement(self.lblPosu,self.lblPosu_2))
        self.cmdUnit.clicked.connect(self.gotoChangeMeasurement1)
    def gotoLightToggle(self):
        if GlobalVars.LightStatus == True:#if Light is on, turn it off
            GlobalVars.LightStatus = False
            MainWindow.cmdLight.setStyleSheet("background-color: grey")
            serth.ser_out("<0000LO0000>") #Off
        else:
            MainWindow.cmdLight.setStyleSheet("background-color: yellow")
            if not Settings.LBToRed and not Settings.LBToGreen and Settings.LBToBlue:serth.ser_out("<0000LB0000>") # Blue
            if not Settings.LBToRed and Settings.LBToGreen and not Settings.LBToBlue:serth.ser_out("<0000LG0000>") #Green
            if not Settings.LBToRed and Settings.LBToGreen and Settings.LBToBlue:serth.ser_out("<0000LA0000>") #Aqua
            if Settings.LBToRed and not Settings.LBToGreen and not Settings.LBToBlue:serth.ser_out("<0000LR0000>") #red
            if Settings.LBToRed and not Settings.LBToGreen and Settings.LBToBlue:serth.ser_out("<0000LP0000>") #Purple
            if Settings.LBToRed and Settings.LBToGreen and not Settings.LBToBlue:serth.ser_out("<0000LE0000>") #Orange
            if Settings.LBToRed and Settings.LBToGreen and Settings.LBToBlue:serth.ser_out("<0000LW0000>") #white
            GlobalVars.LightStatus = True

    def gotoXRHome(self,lblCurPOS):
        serth.ser_out("<9999XH9999>")
        lblCurPOS.setText("0")
        GlobalVars.CurrentDistance = 0
    def gotoLogin(self):
        #keypadwindow.cmdCancelPassword.show()
        SetKeypadType("Password")
        KeypadWindow.show()

    #---------------------------------------------------------Convert measurements in the existing main screen-------------------------
    def gotoChangeMeasurement1(self):
        if int(GlobalVars.PrevXValue) == 0:
            self.gotoChangeMeasurement2()
            self.gotoChangeMeasurement3()
        else: 
            MainWindow.lblMKeyPadError.setText("Cannot change unless Home")
            MainWindow.lblMKeyPadError.show()

    def gotoChangeMeasurement2(self):
        PreviousUnit = GlobalVars.Dunit
        PreviousValue = MainWindow.lblPos.text()
        print(PreviousValue)
        match GlobalVars.Dunit:
            case "Feet":
                if Settings.EnableYards:
                    GlobalVars.Dunit = ("Yards")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return
                if Settings.EnableMeters:
                    GlobalVars.Dunit = ("Meters")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return
            case "Yards":
                if Settings.EnableMeters:
                    GlobalVars.Dunit = ("Meters")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return
                if Settings.EnableFeet:
                    GlobalVars.Dunit = ("Feet")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return
            case "Meters":
                if Settings.EnableFeet:
                    GlobalVars.Dunit = ("Feet")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return
                if Settings.EnableYards:
                    GlobalVars.Dunit = ("Yards")
                    MainWindow.lblPos.setText(str(ConvertUnit(PreviousValue,GlobalVars.Dunit,"REAL",PreviousUnit)))
                    return

    def gotoChangeMeasurement3(self):
        MainWindow.lblPosu.setText(GlobalVars.Dunit)
        MainWindow.lblPosu_2.setText(GlobalVars.Dunit)
        AdvancedWindow.lblPosu.setText(GlobalVars.Dunit)
    #---------------------------------------------------------Convert measurements in the existing main screen----------------------

    def gotoAdvancedWindow(self):
        AdvancedWindow.EditTreeHeader()
        self.hide()
        AdvancedWindow.show()
    def gotoSetupWindow(self):
        self.hide()
        GetSettings()
        LoadSettingstoWindow()
        setupwindow.show()
    def gotoEnterDigit(self,DigitValue,CurrentValue,POSLabel,lblMKeyPadError):
        lblMKeyPadError.hide()
        if CurrentValue == "0":
            CurrentValue = ""
        if len(CurrentValue) < 3:
            CurrentValue = CurrentValue + DigitValue
            print(CurrentValue)
            POSLabel.setText(CurrentValue)
    def gotoDataDelete(self,CurrentValue,POSLabel):
        if len(CurrentValue) > 1:
            CurrentValue = CurrentValue[:- 1]
            POSLabel.setText(CurrentValue)
        else:
            POSLabel.clear()
    def gotoDataEntry(self,NewXValue,lblCurPOS,lblNewPOS,lblMKeyPadError,lblPosu):
        intMinimumDistance = 0
        intMaximumDistance = 0
        PrevXPulseCount = 0
        NewXPulseCount = 0
        MoveXDistance = 0
        if NewXValue == "": NewXValue = 0
        NewXValue = int(NewXValue)
        if GlobalVars.Dunit != "Feet":#Retrieve and convert min/Max distances Yards or Meters
            intMinimumDistance = ConvertUnit(GlobalVars.MinFeet,GlobalVars.Dunit,"MIN","Feet")
            intMaximumDistance = ConvertUnit(GlobalVars.MaxFeet,GlobalVars.Dunit,"MAX","Feet")
        if GlobalVars.Dunit == "Feet":#Retrieve Min/Max Distances
            intMinimumDistance = int(GlobalVars.MinFeet)
            intMaximumDistance = int(GlobalVars.MaxFeet)
        #evaluate Min/Max with user input
        if (NewXValue >= intMinimumDistance) and (NewXValue <= intMaximumDistance and (NewXValue != GlobalVars.PrevXValue)):TooClose = False
        else: TooClose=True
        if TooClose == True :
            lblMKeyPadError.show()
            lblMKeyPadError.setText("Value not allowed")
            lblNewPOS.setText("")
        else:#Calculate and transmit new values.  All values a using XAxit pulse counts in relation to zero to prevent additive move errors
            #GlobalVars.PrevXValue = NewXValue
            GlobalVars.ElapsedTimeStart = QTime.currentTime()
            lblNewPOS.setText("")
            lblCurPOS.setText(str(NewXValue))#Set user typed entry into the new distance box
            #Need to Grey out changes until acknowledge pulse is returned
            GlobalVars.XMoveLockedIn = True
            MainWindow.lblPos.setText("MOVING")
            MainWindow.cmdMKeyPadGo.setEnabled(False)







            #Where are we currently - reference to zero
            print("Previous X Value")
            print(GlobalVars.PrevXValue)
            PrevXPulseCount = ConvertToXAxisPulse(abs(GlobalVars.PrevXValue),lblPosu)
            print("Previous Pulse Count")
            print(PrevXPulseCount)
            #Where we want to go - reference to zero
            print("New X Value")
            print(NewXValue)
            NewXPulseCount = ConvertToXAxisPulse(abs(NewXValue),lblPosu)
            print("New Pulse Count")
            print(NewXPulseCount)
            MoveXDistance = NewXPulseCount - PrevXPulseCount


            #TEMPORARY set previous to current to record changed distance
            GlobalVars.PrevXValue   =  NewXValue





            #MoveXDistance = NewXValue - int(GlobalVars.CurrentDistance) #Difference between where we are now and where we want to be
            #GlobalVars.CurrentDistance = NewXValue
            #CurrentDistancePulseCount = ConvertToXAxisPulse(abs(MoveXDistance),lblPosu,9)




            lblMKeyPadError.hide()
            lblMKeyPadError.setText("")
            print("Data Entered")
            #Convert Number of pulses to feet or meters
            #intXPulses = ConvertToXAxisPulse(abs(MoveXDistance),lblPosu,9)#Need unsigned Value
            strXPulses = str(MoveXDistance)
            strXPulses = strXPulses.zfill(8)
            #Need split routine
            if MoveXDistance < 0:
                #strXMove = ("<0000XC"+strXPulses+">")#move backward Auto
                strXMove = ("<" + strXPulses[0:4]+"XC"+strXPulses[4:8] + ">")#move backward Auto
                print("Moving XC(Backward) pulses: -",strXPulses)
                print (strXMove)
            else:
                strXMove = ("<" + strXPulses[0:4]+"XA"+strXPulses[4:8] + ">")#Move forward Auto
                #strXMove = ("<0000XA"+strXPulses+">")#Move forward Auto
                print("Moving XA(Forward) pulses: ",strXPulses)
                print (strXMove)
            serth.ser_out(strXMove)
            







#*******************************************************************************Keypad entry*******************************************************************************
def SetKeypadType(KeypadType):
        if KeypadType == "KeypadX": 
            KeypadWindow.lblTitle.setText("Move X Distance")
            KeypadWindow.lblKeyPadType.setText("KeypadX")
        if KeypadType == "KeypadRCW": 
            KeypadWindow.lblTitle.setText("Rotate Degrees CW")
            KeypadWindow.lblKeyPadType.setText("KeypadRCW")
        if KeypadType == "KeypadRCCW": 
            KeypadWindow.lblTitle.setText("Rotate Degrees CCW")
            KeypadWindow.lblKeyPadType.setText("KeypadRCCW")
        if KeypadType == "Password": 
            KeypadWindow.lblTitle.setText("Password Entry")
            KeypadWindow.lblKeyPadType.setText("Password")
        if KeypadType == "DelaySeconds": 
            KeypadWindow.lblTitle.setText("Delay Seconds")
            KeypadWindow.lblKeyPadType.setText("DelaySeconds")
        if KeypadType == "Repeat": 
            KeypadWindow.lblTitle.setText("Repeat # Times")
            KeypadWindow.lblKeyPadType.setText("Repeat")


class clsKeyPadWindow(QWidget):
    def __init__(self):
        super(clsKeyPadWindow, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'KeyPad.ui'),self)
        global KeyPadEntry
        GlobalVars.SecondEntryFlag = False
        KeyPadEntry = self.lblOut
        self.lblKeyPadType.hide()
        self.lblError.hide()
        self.lblTitle.show()
        #self.cmdCancelPassword.hide()
        self.cmdEnter.clicked.connect(lambda: self.gotoDataEntry(self.lblOut,self.lblError))
        self.cmdDelete.clicked.connect(self.gotoDataDelete)
        self.cmd1.clicked.connect(lambda: self.gotoEnterDigit("1",self.lblError))
        self.cmd2.clicked.connect(lambda: (self.gotoEnterDigit("2",self.lblError)))
        self.cmd3.clicked.connect(lambda: (self.gotoEnterDigit("3",self.lblError)))
        self.cmd4.clicked.connect(lambda: (self.gotoEnterDigit("4",self.lblError)))
        self.cmd5.clicked.connect(lambda: (self.gotoEnterDigit("5",self.lblError)))
        self.cmd6.clicked.connect(lambda: (self.gotoEnterDigit("6",self.lblError)))
        self.cmd7.clicked.connect(lambda: (self.gotoEnterDigit("7",self.lblError)))
        self.cmd8.clicked.connect(lambda: (self.gotoEnterDigit("8",self.lblError)))
        self.cmd9.clicked.connect(lambda: (self.gotoEnterDigit("9",self.lblError)))
        self.cmd0.clicked.connect(lambda: (self.gotoEnterDigit("0",self.lblError)))
        self.cmdCancelKeypad.clicked.connect(lambda: (self.gotoCancelKeypad()))

    def gotoCancelKeypad(self):
        self.lblOut.setText("")
        self.lblError.setText("")
        self.lblError.hide()
        self.hide()

    def gotoDataEntry(self,lblOut,lblError):#Enter key is pressed
        FinishExit = False
        FinishPassword = False
        intMinimumDistance = 0
        intMaximumDistance = 0
        try:
            intKeyPadValue = int(GlobalVars.KeypadValue)
        except Exception:
            intKeyPadValue = 0

        if self.lblKeyPadType.text() =="KeypadX":
            if GlobalVars.Dunit != "Feet":#Convert Min max from setup-feet to Yards.Round up for min, round down for Max
                intMinimumDistance = ConvertUnit(GlobalVars.MinFeet,"Feet","MIN",GlobalVars.Dunit)
                intMaximumDistance = ConvertUnit(GlobalVars.MaxFeet,"Feet","MAX",GlobalVars.Dunit)
            if GlobalVars.Dunit == "Feet":
                intMinimumDistance = int(GlobalVars.MinFeet)
                intMaximumDistance = int(GlobalVars.MaxFeet)
            if (intKeyPadValue >= intMinimumDistance) and (intKeyPadValue <= intMaximumDistance):FinishExit = True
            else:
                lblError.show()
                lblError.setText("Value too Small or Large")
                lblOut.setText("")
        #*******************************************************************
        if self.lblKeyPadType.text() =="Repeat":
            if (intKeyPadValue >= 60) or (intKeyPadValue == 0):
                lblError.show()
                lblError.setText("Value too Small (0) or Large (>60)")
                lblOut.setText("")
            else: FinishExit = True
        #*******************************************************************
        if self.lblKeyPadType.text() =="KeypadRCW":#Max degrees, cannot exceed 360
            if intKeyPadValue >= 361: GlobalVars.KeypadValue = "360"
            FinishExit = True
        if self.lblKeyPadType.text() =="KeypadRCCW":#Max degrees, cannot exceed 360
            if intKeyPadValue >= 361: GlobalVars.KeypadValue = "360"
            FinishExit = True
        #Password***********************************************************
        if self.lblKeyPadType.text() =="Password":
            ReturnSecurity = AuthenticateUser(self,intKeyPadValue)
            if ReturnSecurity != "FAIL":
                MainWindow.lblSecurity.setText(ReturnSecurity)
                GlobalVars.LoginType = int(ReturnSecurity)
                ApplySecurity(self,int(ReturnSecurity))
                FinishPassword = True
            else:
                lblError.setText("Password Incorrect")
                lblOut.setText("")
                lblError.show()
        #********************************************************************
        if self.lblKeyPadType.text() =="DelaySeconds":
            if intKeyPadValue >= 3601: GlobalVars.KeypadValue = "3600"#Max seconds, cannot exceed 3600 (1 hour)
            FinishExit = True
        #********************************************************************
        if FinishExit == True:
            self.ExitKeypadToAdvanced(self.lblTitle.text())#Set entry in list and clean up
            lblError.setText("")
            lblError.hide()
            self.hide()
            if GlobalVars.SecondEntryFlag == True:
                GlobalVars.SecondEntryFlag = False
                SetKeypadType("DelaySeconds")
                KeypadWindow.show()
            
        #********************************************************************
        if FinishPassword == True:
            lblError.setText("")
            lblError.hide()
            KeyPadEntry.setText("")
            self.hide()

    def ExitKeypadToAdvanced(self,LineEntry):#Set entry in list and clean up
        if LineEntry != "Delay Seconds": 
            GlobalVars.SecondEntryFlag = True
            AdvancedWindow.AddMacro(LineEntry,GlobalVars.KeypadValue)
        if LineEntry == "Delay Seconds": 
            AdvancedWindow.AddMacroDelay(GlobalVars.KeypadValue)
        KeyPadEntry.setText("")
        
    def gotoEnterDigit(self,DigitValue,lblError):
        GlobalVars.KeypadValue = KeyPadEntry.text()
        lblError.hide()
        if GlobalVars.KeypadValue == "0":
            GlobalVars.KeypadValue = ""
        if self.lblKeyPadType.text() !="DelaySeconds" and self.lblKeyPadType.text() !="Password" :#If entering distance or rotation, allow only 3 digits
            if len(GlobalVars.KeypadValue) < 3:
                GlobalVars.KeypadValue = GlobalVars.KeypadValue + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(GlobalVars.KeypadValue)
        if self.lblKeyPadType.text() =="DelaySeconds":#If entering seconds, allow 4 digits
            if len(GlobalVars.KeypadValue) < 4:
                GlobalVars.KeypadValue = GlobalVars.KeypadValue + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(GlobalVars.KeypadValue)
        if self.lblKeyPadType.text() =="Password":#If entering Password, allow 8 digits
            if len(GlobalVars.KeypadValue) < 8:
                GlobalVars.KeypadValue = GlobalVars.KeypadValue + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(GlobalVars.KeypadValue)
    def gotoDataDelete(self):
        GlobalVars.KeypadValue = KeyPadEntry.text()
        if len(GlobalVars.KeypadValue) > 1:
            GlobalVars.KeypadValue = GlobalVars.KeypadValue[:- 1]
            KeyPadEntry.clear()
            KeyPadEntry.setText(GlobalVars.KeypadValue)
        else:
            KeyPadEntry.clear()

#*******************************************************************************Setup Window*******************************************************************************
class SetupWindow(QWidget):
    trigger = pyqtSignal()
    def __init__(self):
        super(SetupWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        loadUi(os.path.join(GlobalVars.Home, 'SetupWindow.ui'),self)
        self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)
        self.cmdExit.clicked.connect(self.gotoMainWindow)
        self.cmdRestart.clicked.connect(self.gotoRestart)
        self.cmdBasicApply.clicked.connect(self.gotoBasicApply)
        self.cmdMotorApply.clicked.connect(self.gotoMotorApply)
        #self.cmdDeviceApply.clicked.connect(self.gotoDeviceApply)
        self.cmdSendSerialString.clicked.connect(lambda: self.gotoSendSerialString(self.lblButtonCounter))
        self.cmdSendSerialChar1.clicked.connect(lambda: self.gotoSendSerialChar1(self.lblButtonCounter))#<
        self.cmdSendSerialChar2.clicked.connect(self.gotoSendSerialChar2)#x
        self.cmdSendSerialChar3.clicked.connect(self.gotoSendSerialChar3)#>
        self.cmdSendMQTTString.clicked.connect(self.gotoSendMQTTString)
        self.trigger.connect(lambda: self.gotoPopulateSerialData(self.lblSerOut,self.lblSerOut2))#trigger serial data recieved
            
    def gotoPopulateSerialData(self,SerOut,SerOut2):
            SerOut.setText(GlobalVars.RawSerialString)
            SerOut2.setText(GlobalVars.SerialString)
            setupwindow.lblSerOut2.setText(GlobalVars.SerialString)
    def gotoSendSerialString(self,lblCounter):
        setupwindow.lblSerOut2.setText("null")
        GlobalVars.SerialString = "" #Clear serial data
        print("gotoSendSerialString")
        serth.ser_out("<9999BS9999>")#Test out string(((((((((((((((((((((((((((((((((((((((())))))))))))))))))))))))))))))))))))))))
        GlobalVars.TCounter = GlobalVars.TCounter + 1
        lblCounter.setText(str(GlobalVars.TCounter))
    def gotoSendSerialChar1(self,lblCounter):
        print("gotoSendSerialChar1")
        GlobalVars.TCounter = GlobalVars.TCounter + 1
        lblCounter.setText(str(GlobalVars.TCounter))
        serth.ser_out("<")
    def gotoSendSerialChar2(self):
        print("gotoSendSerialChar2")
        serth.ser_out("1")
    def gotoSendSerialChar3(self):
        print("gotoSendSerialChar3")
        serth.ser_out(">")
    def gotoSendMQTTString(self):
        print("SendMQTTString")
        MQTT_Out()#Test out string(((((((((((((((((((((((((((((((((((((((())))))))))))))))))))))))))))))))))))))))
    def handle_tabbar_clicked(self, index):
        print(index)
        GetSettings()
        LoadSettingstoWindow()
    def gotoMainWindow(self):
        self.hide()
        MainWindow.show()
    def gotoRestart(self):
        try:
            os.system('sudo restart')
        except Exception:
            print("Could Not Restart")

    def gotoMotorApply(self):#-----------------------------------------------------------------------------------------
        C_XPPF = ""#X Pulses per Foot
        C_ZPP360 = ""#Z Pulses per 360 Degrees
        C_XPPM = ""#X Pulses per Meter
        print("MotorApply")
        #Reset errors and colors On Setup Page - Motor Tab
        setupwindow.lblMotorError.hide()
        setupwindow.lblMotorError.setStyleSheet("background-color: white")
        setupwindow.txt_XPPF.setStyleSheet("background-color: white")
        setupwindow.txt_XPPM.setStyleSheet("background-color: white")
        setupwindow.txt_ZPP360.setStyleSheet("background-color: white")
        setupwindow.txt_ComWindows.setStyleSheet("background-color: white")
        setupwindow.txt_ComLinux.setStyleSheet("background-color: white")
        #-------------------------check Values---------------------------

        C_XPPF = Convert_Number(self.txt_XPPF.toPlainText())#check if number is integer, decimal, or invalid
        C_ZPP360 = Convert_Number(self.txt_ZPP360.toPlainText())#check if number is integer, decimal, or invalid
        C_XPPM = Convert_Number(self.txt_XPPM.toPlainText())#check if number is integer, decimal, or invalid
        if C_XPPF == "0":
            setupwindow.lblMotorError.show()
            setupwindow.txt_XPPF.setStyleSheet("background-color: yellow")
            return
        if C_ZPP360 == "0":
            setupwindow.lblMotorError.show()
            setupwindow.txt_ZPP360.setStyleSheet("background-color: yellow")
            return
        if C_XPPM == "0":
            setupwindow.lblMotorError.show()
            setupwindow.txt_XPPM.setStyleSheet("background-color: yellow")
            return
        #Get the configparser object
        config_object = ConfigParser()
        #Write 1 section in the config file
        config_object["MOTORSETTINGS"] = {
        "xppf": C_XPPF
        ,"xppm" : C_XPPM
        ,"zpp360": C_ZPP360
        ,"comwin": self.txt_ComWindows.toPlainText()
        ,"comlinux": self.txt_ComLinux.toPlainText()
        }
        #Write the above sections to device.ini file
        outfile = os.path.join(os.path.dirname(__file__), 'motor.ini')
        with open(outfile, 'w') as conf:
            config_object.write(conf)
        GetSettings()

    def gotoBasicApply(self):#-----------------------------------------------------------------------------------------
        print("BasicApply")
        #Reset errors and colors
        setupwindow.lblError.hide()
        setupwindow.txtLane.setStyleSheet("background-color: white")
        setupwindow.txtMinFeet.setStyleSheet("background-color: white")
        setupwindow.txtMaxFeet.setStyleSheet("background-color: white")
        setupwindow.txtAutoHome.setStyleSheet("background-color: white")
        setupwindow.txtSleep.setStyleSheet("background-color: white")
        setupwindow.txtError.setStyleSheet("background-color: white")
        #-------------------------check Values---------------------------
        TooFar = False
        if len(self.txtLane.toPlainText()) > 4: TooFar = True #Check Lane to 4 digits
        if TooFar:
            setupwindow.txtLane.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtLane.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtMaxFeet.toPlainText()) == False: TooFar = True #Check Max Feet
        else: TooFar = MaxValue(self.txtMaxFeet.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtMaxFeet.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtMaxFeet.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtMinFeet.toPlainText()) == False: TooFar = True #Check Min Feet
        else: TooFar = MaxValue(self.txtMaxFeet.toPlainText(),0,"MIN")
        if TooFar:
            setupwindow.txtMinFeet.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtMinFeet.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtAutoHome.toPlainText()) == False: TooFar = True  #Check Auto Return
        else: TooFar = MaxValue(self.txtAutoHome.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtAutoHome.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtAutoHome.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtSleep.toPlainText()) == False: TooFar = True  #Check Sleep value
        else: TooFar = MaxValue(self.txtSleep.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtSleep.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtSleep.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtError.toPlainText()) == False: TooFar = True  #Check error timeout value
        else: TooFar = MaxValue(self.txtError.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtError.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtError.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtDefaultUser.toPlainText()) == False: TooFar = True  #Check error Default Login Level
        else: TooFar = MaxValue(self.txtDefaultUser.toPlainText(),4,"MAX")
        if TooFar:
            setupwindow.txtDefaultUser.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtDefaultUser.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if self.chkEnableFeet.isChecked() : EnableFeet = True
        else: EnableFeet = False
        if self.chkEnableYards.isChecked() : EnableYards = True
        else: EnableYards= False
        if self.chkEnableMeters.isChecked() : EnableMeters = True
        else: EnableMeters = False
        DefaultUnits = "Feet"

        if EnableFeet == False and EnableYards == False and EnableMeters == False:
            setupwindow.lblError.show()
            setupwindow.lblError.setText("Must select unit of Measure - CHANGES ARE NOT SAVED")
            setupwindow.lblMeasureSection.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file
        else: setupwindow.lblMeasureSection.setStyleSheet("background-color: white")

        if self.rdoFeet.isChecked() : DefaultUnits = "Feet"
        if self.rdoYards.isChecked() : DefaultUnits = "Yards"
        if self.rdoMeters.isChecked() : DefaultUnits = "Meters"

        if (DefaultUnits == "Feet" and EnableFeet == False) or (DefaultUnits == "Yards" and EnableYards == False) or (DefaultUnits == "Meters" and EnableMeters == False):
            setupwindow.lblError.show()
            setupwindow.lblError.setText("Default unit of measure must be included in available measurements - CHANGES ARE NOT SAVED")
            setupwindow.lblDefaultMeasure.setStyleSheet("background-color: yellow")
            setupwindow.lblMeasureSection.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file
        else: 
            setupwindow.lblDefaultMeasure.setStyleSheet("background-color: white")
            setupwindow.lblMeasureSection.setStyleSheet("background-color: white")

        if self.chkLightRed.isChecked() : TLightRed = True
        else: TLightRed = False
        if self.chkLightGreen.isChecked() : TLightGreen = True
        else: TLightGreen = False
        if self.chkLightBlue.isChecked() : TLightBlue = True
        else: TLightBlue = False
        if self.chkACC1.isChecked() : TACC1 = True
        else: TACC1 = False

        #Get the configparser object
        config_object = ConfigParser()
        #Write 1 section in the config file
        config_object["BASICSETTINGS"] = {
        "lane": self.txtLane.toPlainText()
        ,"minfeet": self.txtMinFeet.toPlainText()
        ,"maxfeet": self.txtMaxFeet.toPlainText()
        ,"autohome": self.txtAutoHome.toPlainText()
        ,"sleep": self.txtSleep.toPlainText()
        ,"error": self.txtError.toPlainText()
        ,"defaultlogin" : self.txtDefaultUser.toPlainText()
        ,"enablefeet" : EnableFeet
        ,"enableyards" : EnableYards
        ,"enablemeters" : EnableMeters
        ,"defaultunits" : DefaultUnits
        ,"slowtoend" : self.txtSlowEnd.toPlainText()
        ,"slowtofront" : self.txtSlowFront.toPlainText()
        ,"lbtored" : TLightRed
        ,"lbtogreen" : TLightGreen
        ,"lbtoblue" : TLightBlue
        ,"lbtoacc1" : TACC1
        }
        #Write the above sections to device.ini file
        outfile = os.path.join(os.path.dirname(__file__), 'basic.ini')
        with open(outfile, 'w') as conf:
            config_object.write(conf)
        GetSettings()

        #Write the above sections to device.ini file
        outfile = os.path.join(os.path.dirname(__file__), 'device.ini')
        with open(outfile, 'w') as conf:
            config_object.write(conf)
        GetSettings()
#*******************************************************************************Advanced Window*******************************************************************************
class clsAdvancedWindow(QWidget):
    def __init__(self):
        super(clsAdvancedWindow, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'AdvancedWindow.ui'),self)
        self.cmdExit.clicked.connect(self.gotoMainWindow)
        self.cmdTargetCW.clicked.connect(self.gotoTargetRCW)
        self.cmdTargetCCW.clicked.connect(self.gotoTargetRCCW)
        self.cmdLighton.clicked.connect(self.gotoLightOn)
        self.cmdLightoff.clicked.connect(self.gotoLightOff)
        self.cmdRepeat.clicked.connect(self.gotoRepeat)
        self.cmdRemovelast.clicked.connect(self.gotoRemoveLast)
        self.cmdAdvTest.clicked.connect(self.gotoAdvTest)
        #*******************Initialize QTree Widet with top level items
        print(GlobalVars.Dunit)
        global MacroCommand
        MacroCommand = self.treeMacro
        self.treeMacro.setHeaderLabels(["Action", str(GlobalVars.Dunit),"Wait"])
        self.treeMacro.setColumnWidth(0, 280)
        self.treeMacro.setColumnWidth(1, 4)
        self.treeMacro.setColumnWidth(2, 4)
        self.cmdX.clicked.connect(self.gotoEnterX)
        #*************************************************************
    def gotoAdvTest(self):
        rowcount = MacroCommand.topLevelItemCount()
        MacroCommand.addTopLevelItem(QTreeWidgetItem(rowcount))
    def EditTreeHeader(self):
        MacroCommand.setHeaderLabels(["Action", str(GlobalVars.Dunit),"Wait"])
    def AddMacro(self,strInput,strUnit):#Add Top item and Unit value to Tree
        rowcount = MacroCommand.topLevelItemCount()
        MacroCommand.addTopLevelItem(QTreeWidgetItem(rowcount))
        MacroCommand.topLevelItem(rowcount).setText(0, str(strInput))
        MacroCommand.topLevelItem(rowcount).setText(1, str(strUnit))
    def AddMacroDelay(self,strDelay):#Edit top item column Wait - add value
        rowcount = MacroCommand.topLevelItemCount()
        MacroCommand.topLevelItem(rowcount-1).setText(2, str(strDelay))
    def RemoveMacro(self):#Remove last top tree item
        rowcount = MacroCommand.topLevelItemCount()
        MacroCommand.takeTopLevelItem(rowcount-1)
    def ClearMacro(self):#Wipe QTree
        MacroCommand.clear
    def gotoEnterX(self):
        SetKeypadType("KeypadX")
        KeypadWindow.show()
    def gotoTargetRCCW(self):
        SetKeypadType("KeypadRCCW")
        KeypadWindow.show()
    def gotoTargetRCW(self):
        SetKeypadType("KeypadRCW")
        KeypadWindow.show()
    def gotoDelay(self):
        SetKeypadType("DelaySeconds")
        KeypadWindow.show()
    def gotoLightOn(self):
        AdvancedWindow.AddMacro("Target Light:","ON")
        SetKeypadType("DelaySeconds")
        KeypadWindow.show()
    def gotoLightOff(self):
        AdvancedWindow.AddMacro("Target Light:","OFF")
        SetKeypadType("DelaySeconds")
        KeypadWindow.show()
    def gotoRepeat(self):
        SetKeypadType("Repeat")
        KeypadWindow.show()
    def gotoRemoveLast(self):
        AdvancedWindow.RemoveMacro()
    def gotoMainWindow(self):
        AdvancedWindow.ClearMacro()
        self.hide()
        MainWindow.show()

#*******************************************************************************Settings class*******************************************************************************
class clsSettings:
    LBToRed = None
    LBToGreen = None
    LBToBlue = None
    EnableYards = False
    EnableMeters = False
    EnableFeet = False
    XPPF = ""
    XPPM = ""
    ZPP360 = ""
    DefaultUnits = ""
    Lane = ""
    MaxFeet = ""
    MinFeet = ""
    Lane = ""
    COMWIN = ""
    COMLINUX = ""
    SlowToEnd = ""
    SlowToFront = ""
    LBToACC1 = False
    LBToRed = False
    LBToGreen = False
    LBToBlue = False
    AutoHome = ""
    Sleep = ""
    Error = ""
    TempLogin = 0
#*******************************************************************************GlobalVars class*******************************************************************************
class clsGlobalVars:
    Home = os.path.dirname(__file__)
    LightStatus = False
    Dunit = ""
    CurrentDistance = 0
    PrevXValue = 0.0
    MinFeet = ""
    MaxFeet = ""
    ElapsedTimeStart = (QTime.currentTime())
    XMoveLockedIn = False
    SecondEntryFlag = False
    LoginType = 0
    TCounter = 0
    RawSerialString = ""
    SerialString = ""
    Arduino_CurrentCommType = ""
    OSType = ""
    PortName = ""
    BaudRate = ""
    MakeBold = QtGui.QFont('Arial', 12)
    MakeNormal = QtGui.QFont('Arial', 9)
    RawSerialString = ""
    SerialString = ""
    SerialStatus = False
    ElapsedTimeStart = (QTime.currentTime())
    CurrentDistance = ""
    Arduino_CurrentXPulseCount = 0
    TCounter = 0
    HB = datetime(1900,1,1,1,1,1,1)
    KeypadValue = ""
#*******************************************************************************MQTT status class*******************************************************************************
class clsMQTT:
    def __init__(self,Status,Client):
        self.Status = Status


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$General Purpose functions$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#*******************************************************************************Measurement conversion *******************************************************************************
def ConvertUnit(InVal,ConvertTo,MinMax,ConvertFrom):#Convert Min max from setup-feet to Yards.Round up for min, round down for Max
    OutUnit = 0
    print("convertto")
    print(ConvertTo)
    print("convertfrom")
    print(ConvertFrom)

    print("minmax")
    print(MinMax)
    print("inval")
    print(InVal)
    match ConvertFrom:
        case "Feet":
            try:
                intInVal = int(InVal)
                if MinMax == "MIN":
                    if ConvertTo == "Yards": OutUnit = (int(math.ceil(intInVal/3)))
                    if ConvertTo == "Meters": OutUnit = (int(math.ceil(intInVal/3.2808)))
                if MinMax == "MAX":
                    if ConvertTo == "Yards": OutUnit = (int(math.floor(intInVal/3)))
                    if ConvertTo == "Meters": OutUnit = (int(math.floor(intInVal/3.2808)))
                if MinMax == "REAL":
                    if ConvertTo == "Yards": OutUnit = ((math.floor(intInVal/3)))
                    if ConvertTo == "Meters": OutUnit = ((math.floor(intInVal/3.2808)))
            except Exception:
                return 0
        case "Yards":
            try:
                intInVal = int(InVal)
                if MinMax == "MIN":
                    if ConvertTo == "Feet": OutUnit = (int(math.ceil(intInVal*3)))
                    if ConvertTo == "Meters": OutUnit = (int(math.ceil(intInVal*.9144)))
                if MinMax == "MAX":
                    if ConvertTo == "Feet": OutUnit = (int(math.floor(intInVal*3)))
                    if ConvertTo == "Meters": OutUnit = (int(math.floor(intInVal*.9144)))
                if MinMax == "REAL":
                    if ConvertTo == "Feet": OutUnit = ((math.floor(intInVal*3)))
                    if ConvertTo == "Meters": OutUnit = ((math.floor(intInVal*.9144)))
            except Exception:
                return 0
        case "Meters":
            try:
                intInVal = int(InVal)
                if MinMax == "MIN":
                    if ConvertTo == "Feet": OutUnit = (int(math.ceil(intInVal*3.28084)))
                    if ConvertTo == "Yards": OutUnit = (int(math.ceil(intInVal*1.09361)))
                if MinMax == "MAX":
                    if ConvertTo == "Feet": OutUnit = (int(math.floor(intInVal*3.28084)))
                    if ConvertTo == "Yards": OutUnit = (int(math.floor(intInVal*1.09361)))
                if MinMax == "REAL":
                    if ConvertTo == "Feet": OutUnit = ((math.floor(intInVal*3.28084)))
                    if ConvertTo == "Yards": OutUnit = ((math.floor(intInVal*1.09361)))
            except Exception:
                return 0
    return OutUnit
#*******************************************************************************XAxis Pulse conversion *******************************************************************************
def ConvertToXAxisPulse(XDistanceRequest,CurrentUnit):#Convert Distance into number of motor pulses required
    OutUnit = 0.00000
    intDistance = 0
    floatXPPF = float(Settings.XPPF)
    floatXPPM = float(Settings.XPPM)
    try:
        intDistance = int(XDistanceRequest)
        if CurrentUnit == "Yards": OutUnit = ((intDistance * floatXPPF)*3)
        if CurrentUnit == "Meters": OutUnit = (intDistance * floatXPPM)
        if CurrentUnit == "Feet": OutUnit = (intDistance * floatXPPF)
        OutUnit = math.floor(OutUnit)
        print("-----------------")
        print("Outunit")
        print(OutUnit)
        print("-----------------")
    except Exception:
        print("-----------------")
        print("Error Conversion ConvertToXAxisPulse")
        print("-----------------")
        return 0
    return OutUnit

#*******************************************************************************Maximum Value*******************************************************************************
def MaxValue(InvalRaw,CompareValueRaw,MaxMin):
    BinOut = False
    Inval = 0
    CompareValue = 0
    try:
        Inval=int(InvalRaw)
        CompareValue = int(CompareValueRaw)
    except Exception:
        InvalRaw = 0
        CompareValueRaw = 0
    if MaxMin == "MAX":
        if Inval > CompareValue:
            BinOut = True
            print("True")
    if MaxMin == "MIN":
        if Inval < CompareValue:
            BinOut = True
            print("True")
    if BinOut == True: return True
    if BinOut == False: return False
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$General Purpose functions$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


#*******************************************************************************Get settings from config file(s)*******************************************************************************
def GetSettings():
    #try:
    config_object = ConfigParser()
    infile = os.path.join(GlobalVars.Home, 'basic.ini')
    config_object.read(infile)
    #Get a key
    deviceinfo = config_object["BASICSETTINGS"]
    #-----------
    config_object = ConfigParser()
    infile = os.path.join(GlobalVars.Home, 'motor.ini')
    config_object.read(infile)
    #Get a key
    motorfileinfo = config_object["MOTORSETTINGS"]
    
    try:
        Settings.XPPF = motorfileinfo["xppf"]
    except Exception: Settings.XPPF = "1"
    try:
        Settings.XPPM = motorfileinfo["xppm"]
    except Exception: Settings.XPPM = "1"
    try:
        Settings.ZPP360 = motorfileinfo["zpp360"]
    except Exception: Settings.ZPP360 = "1"
    try:
        Settings.COMWIN = motorfileinfo["comwin"]
    except Exception: Settings.COMWIN = "COM3"
    try:
        Settings.COMLINUX = motorfileinfo["comlinux"]
    except Exception: Settings.COMLINUX = "/dev/ttyUSB0"
    try:
        Settings.Lane = deviceinfo["lane"]
        MainWindow.lblLane.setText(deviceinfo["lane"])
    except Exception: Settings.Lane = "Default"
    Settings.MaxFeet = deviceinfo["maxfeet"]
    GlobalVars.MaxFeet = Settings.MaxFeet
    Settings.MinFeet = deviceinfo["minfeet"]
    GlobalVars.MinFeet = Settings.MinFeet
    try: Settings.SlowToEnd = deviceinfo["slowtoend"]
    except Exception: Settings.SlowToEnd = "0"
    try: Settings.SlowToFront = deviceinfo["slowtofront"]
    except Exception: Settings.SlowToFront = "0"
    try: TLBToRed = deviceinfo["lbtored"]
    except Exception: TLBToRed = "0"
    if TLBToRed == "True" :Settings.LBToRed = True
    else: Settings.LBToRed = False
    try: TLBToGreen = deviceinfo["lbtogreen"]
    except Exception: TLBToGreen = "0"
    if TLBToGreen == "True" :Settings.LBToGreen = True
    else: Settings.LBToGreen = False
    try: TLBToBlue = deviceinfo["lbtoblue"]
    except Exception: TLBToBlue = "0"
    if TLBToBlue == "True" :Settings.LBToBlue = True
    else: Settings.LBToBlue = False
    try: TLBToACC1 = deviceinfo["lbtoacc1"]
    except Exception: TLBToACC1 = "0"
    if TLBToACC1 == "True" :Settings.LBToACC1 = True
    else: Settings.LBToACC1 = False
    Settings.AutoHome = deviceinfo["autohome"]
    Settings.Sleep = deviceinfo["sleep"]
    Settings.Error = deviceinfo["error"]
    try: Settings.TempLogin = int(deviceinfo["defaultlogin"])
    except Exception: Settings.TempLogin = 0
    try: TEnableFeet = (deviceinfo["enablefeet"])
    except Exception: TEnableFeet = "True"
    if TEnableFeet == "True" :Settings.EnableFeet = True
    else: Settings.EnableFeet = False
    try: TEnableYards = (deviceinfo["enableyards"])
    except Exception: TEnableYards = "True"
    if TEnableYards == "True" :Settings.EnableYards = True
    else: Settings.EnableYards = False
    try: TEnableMeters = (deviceinfo["enablemeters"])
    except Exception: TEnableMeters = "True"
    if TEnableMeters == "True" :Settings.EnableMeters = True
    else: Settings.EnableMeters = False
    TLBLUnit = "NULL"
    MainWindow.cmdUnit.hide()
    if Settings.EnableFeet == True and Settings.EnableYards == False and Settings.EnableMeters == False: MainWindow.cmdUnit.hide()
    if Settings.EnableFeet == False and Settings.EnableYards == True and Settings.EnableMeters == False: MainWindow.cmdUnit.hide()
    if Settings.EnableFeet == False and Settings.EnableYards == False and Settings.EnableMeters == True: MainWindow.cmdUnit.hide()
    if Settings.EnableFeet == True and Settings.EnableYards == True and Settings.EnableMeters == False: 
        TLBLUnit = "Feet/Yard"
        MainWindow.cmdUnit.show()
    if Settings.EnableFeet == True and Settings.EnableYards == False and Settings.EnableMeters == True: 
        TLBLUnit = "Feet/Meter"
        MainWindow.cmdUnit.show()
    if Settings.EnableFeet == False and Settings.EnableYards == True and Settings.EnableMeters == True: 
        TLBLUnit = "Yard/Meter"
        MainWindow.cmdUnit.show()
    if Settings.EnableFeet == True and Settings.EnableYards == True and Settings.EnableMeters == True: 
        TLBLUnit = "FT/YD/Meter"
        MainWindow.cmdUnit.show()
    MainWindow.cmdUnit.setText(TLBLUnit)

    #Set default unit of measurement
    try: TDefaultUnits = (deviceinfo["defaultunits"])
    except Exception: TDefaultUnits = "Feet"
    #if TDefaultUnits != "Feet" and TDefaultUnits != "Yards" and TDefaultUnits != "Meters":TDefaultUnits = "Feet"#set default unit if not recognized

    Settings.DefaultUnits = str(TDefaultUnits)
    MainWindow.lblPosu.setText(Settings.DefaultUnits)
    MainWindow.lblPosu_2.setText(Settings.DefaultUnits)
    AdvancedWindow.lblPosu.setText(Settings.DefaultUnits)
    GlobalVars.Dunit = Settings.DefaultUnits

    if Settings.LBToRed == True or Settings.LBToGreen == True or Settings.LBToBlue == True: #or Settings.LBToACC1 == True: 
        MainWindow.cmdLight.setStyleSheet("background-color: grey")
        MainWindow.cmdLight.show()
        MainWindow.cmdLight.setText("Light")
    if Settings.LBToRed == False and Settings.LBToGreen == False and Settings.LBToBlue == False: # and Settings.LBToACC1 == False: 
        MainWindow.cmdLight.hide()
        MainWindow.cmdLight.setText("NULL")
    #except Exception:
        #print("Config file ERROR! Config file is missing or corrupt.  Loading defaults")
        #print(str(Settings.EnableFeet))
        #Settings.TempLogin = 0
def LoadSettingstoWindow():
        try:
            setupwindow.txtLane.setPlainText(Settings.Lane)
            setupwindow.txtMaxFeet.setPlainText(Settings.MaxFeet)
            setupwindow.txtMinFeet.setPlainText(Settings.MinFeet)
            setupwindow.txtAutoHome.setPlainText(Settings.AutoHome)
            setupwindow.txtSleep.setPlainText(Settings.Sleep)
            setupwindow.txtError.setPlainText(Settings.Error)
            setupwindow.txtDefaultUser.setPlainText(str(Settings.TempLogin))
            setupwindow.chkEnableFeet.setChecked(Settings.EnableFeet)
            setupwindow.chkEnableYards.setChecked(Settings.EnableYards)
            setupwindow.chkEnableMeters.setChecked(Settings.EnableMeters)
            setupwindow.txtSlowEnd.setPlainText(Settings.SlowToEnd)
            setupwindow.txtSlowFront.setPlainText(Settings.SlowToFront)
            setupwindow.chkLightRed.setChecked(Settings.LBToRed)
            setupwindow.chkLightGreen.setChecked(Settings.LBToGreen)
            setupwindow.chkLightBlue.setChecked(Settings.LBToBlue)
            setupwindow.chkACC1.setChecked(Settings.LBToACC1)
            match Settings.DefaultUnits:
                case "Feet":
                    setupwindow.rdoFeet.setChecked(True)
                case "Yards":
                    setupwindow.rdoYards.setChecked(True)
                case "Meters":
                    setupwindow.rdoMeters.setChecked(True)
                case _:
                    setupwindow.rdoFeet.setChecked(True)
        #Motor Tab
            setupwindow.txt_XPPF.setPlainText(Settings.XPPF)
            setupwindow.txt_XPPM.setPlainText(Settings.XPPM)
            setupwindow.txt_ZPP360.setPlainText(Settings.ZPP360)
            setupwindow.txt_ComWindows.setPlainText(Settings.COMWIN)
            setupwindow.txt_ComLinux.setPlainText(Settings.COMLINUX)
        except Exception as e:
            print("Config file ERROR! Config file is missing or corrupt.  Loading defaults")
            print(e)
            print(str(Settings.EnableFeet))
#*******************************************************************************MQTT Shit*******************************************************************************
#When MQTT recieved, execute this
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg

#https://www.digi.com/resources/documentation/Digidocs/90001541/reference/r_example_subscribe_mqtt.htm
def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected MQTT with result code {0}".format(str(rc)))  # Print result of connection attempt
    MQTTclient.subscribe("balls")  # Subscribe to the topic “digitest/test1”, receive any messages published on it
def MQTT_Out():
    try:
        MQTTclient.publish("balls","Setup Pressed")#publish
    except Exception:
        print("Error publishing to MQTT topic")
#*******************************************************************************Serial Port Shit*******************************************************************************
# Thread to handle incoming & outgoing serial data
class SerialThread(QtCore.QThread):
    def __init__(self, portname, baudrate): # Initialise with serial port details
        QtCore.QThread.__init__(self)
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.running = True
 
    def ser_out(self, XmitData):                   # Write outgoing data to serial port if open
        try:
            print("Serial Data to be Transmitted:")
            print(XmitData)
            self.txq.put(XmitData) 
        except Exception:
                                # ..using a queue to sync with reader thread
            print("Serial Error, not transmitted.")
         
    def ser_in(self, SerialDataRecieved):                       #Write incoming serial data to screen
        if SerialDataRecieved == "<":                           #Reset data if begin char recieved
            GlobalVars.SerialString = ""
            GlobalVars.RawSerialString = ""
        GlobalVars.RawSerialString = SerialDataRecieved
        if len(GlobalVars.SerialString) < 12:                   #Store serial data for later use
            GlobalVars.SerialString = GlobalVars.SerialString + SerialDataRecieved
            SerialDataRecieved = ""
        if len(GlobalVars.SerialString) >= 12:                  #Full data recieved, send to globals, trigger object to update screen
            #print("Serial Len OK. Send to Screen")
            
            print(GlobalVars.SerialString)
            ParseArduinoMessage(GlobalVars.SerialString)
            #*************************************************Update Screens
            if GlobalVars.Arduino_CurrentCommType == "AX" and not GlobalVars.XMoveLockedIn:
                GlobalVars.PrevXValue = Convert_Pulse_to_Measurement(GlobalVars.Arduino_CurrentXPulseCount)
                MainWindow.lblPos.setText(str(GlobalVars.PrevXValue))



            if GlobalVars.Arduino_CurrentCommType == "XD":
                GlobalVars.PrevXValue = Convert_Pulse_to_Measurement(GlobalVars.Arduino_CurrentXPulseCount)
                MainWindow.lblPos.setText(str(GlobalVars.PrevXValue))
                MainWindow.cmdMKeyPadGo.setEnabled(True)
                GlobalVars.XMoveLockedIn = False



























            GlobalVars.HB = datetime.now()
            setupwindow.trigger.emit() #send a global trigger signal so that PYQT windows can update with data
            SerialDataRecieved = ""
         
    def run(self):                          # Run serial reader thread
        print("Opening %s at %u baud %s" % (self.portname, self.baudrate,
              "(hex display)" if hexmode else ""))
        SerialResetCount = 0
        while SerialResetCount < 6:  #Windows seems to have port owership issues, retry port comms up to 6 times
            try:
                time.sleep(.5)
                self.ser = serial.Serial(self.portname, self.baudrate, timeout=SER_TIMEOUT)
                time.sleep(SER_TIMEOUT*1.2)
                self.ser.flushInput()
                if SerialResetCount > 0 :print("Reset/Retry Success, port opened")
                SerialResetCount = 6
            except:
                if SerialResetCount > 0 :print("Reset/Retry Failure")
                else:print("Port open Failure")
                GlobalVars.SerialStatus = False
                self.running = False
            try:
                if not self.ser :
                    time.sleep(.5)
                    serial.Serial(self.portname, self.baudrate, timeout=SER_TIMEOUT).close
            except:
                print ("Error Closing Port")
            SerialResetCount = SerialResetCount +1
        while self.running:
            GlobalVars.SerialStatus = True
            s = self.ser.read(self.ser.in_waiting or 1)
            if s:                                       # Get data from serial port
                self.ser_in(bytes_str(s))               # ..and convert to string
            if not self.txq.empty():
                txd = str(self.txq.get())               # If Tx data in queue, write to serial port
                self.ser.write(str_bytes(txd))
        try:#Don't kill the program; may need to change serial port.
            if self.ser:                                    # Close serial port when thread finished
                self.ser.close()
                self.ser = None
        except:
            print("No port to close...zombie mode activated.")


# Convert a string to bytes
def str_bytes(s):
    return s.encode('latin-1')
     
# Convert bytes to string
def bytes_str(d):
    return d if type(d) is str else "".join([chr(b) for b in d])
     
# Return hexadecimal values of data
def hexdump(data):
    return " ".join(["%02X" % ord(b) for b in data])
 
# Return a string with high-bit chars replaced by hex values
def textdump(data):
    return "".join(["[%02X]" % ord(b) if b>'\x7e' else b for b in data])
     
# Display incoming serial data
def display(s):
    if not hexmode:
        sys.stdout.write(textdump(str(s)))
    else:
        sys.stdout.write(hexdump(s) + ' ')

def write(self, text):                      # Handle sys.stdout.write: update display
    self.text_update.emit(text)             # Send signal to synchronise call with main thread
         
def flush(self):                            # Handle sys.stdout.flush: do nothing
    pass

#****************************************************************************Authenticate Security****************************************************************
def AuthenticateUser(self,PasswordEntry):
    LoginReturn = "FAIL"
    if PasswordEntry == "" : return "0"
    if PasswordEntry == 00000 : return "0"
    if PasswordEntry == 11111 : return "1"
    if PasswordEntry == 22222 : return "2"
    if PasswordEntry == 33333 : return "3"
    if PasswordEntry == 44444 : return "4"
    return "FAIL"
#****************************************************************************Apply Security****************************************************************

def ApplySecurity(self,UserLevel):#Show/Hide Buttons and featurs based on security
    MainWindow.lblSecurity.setText(str(UserLevel))
    if UserLevel == 0:
        MainWindow.cmdSetup.hide() 
        MainWindow.cmdAdvanced.hide() 
        MainWindow.cmdUnit.hide()
        MainWindow.cmdLight.hide()
    if UserLevel == 1:
        MainWindow.cmdSetup.hide()
        MainWindow.cmdAdvanced.hide()
        if MainWindow.cmdUnit.text() != "NULL": MainWindow.cmdUnit.show()
        if MainWindow.cmdLight.text() != "NULL": MainWindow.cmdLight.show()
    if UserLevel == 2:
        MainWindow.cmdSetup.hide()
        MainWindow.cmdAdvanced.show()
        if MainWindow.cmdUnit.text() != "NULL": MainWindow.cmdUnit.show()
        if MainWindow.cmdLight.text() != "NULL": MainWindow.cmdLight.show()
    if UserLevel == 3:
        MainWindow.cmdSetup.show()
        MainWindow.cmdAdvanced.show()
        if MainWindow.cmdUnit.text() != "NULL": MainWindow.cmdUnit.show()
        if MainWindow.cmdLight.text() != "NULL": MainWindow.cmdLight.show()
    if UserLevel == 4:
        MainWindow.cmdSetup.show()
        MainWindow.cmdAdvanced.show()
        if MainWindow.cmdUnit.text() != "NULL": MainWindow.cmdUnit.show()
        if MainWindow.cmdLight.text() != "NULL": MainWindow.cmdLight.show()
    

#****************************************************************************Timer Functions****************************************************************
class clsElapsedtimer:
    def Heartbeat(self):
        TempTime = datetime.now()
        TotalTime = TempTime - GlobalVars.HB
        Total_Seconds = TotalTime.total_seconds()
        #print(GlobalVars.HB)
        #print(TempTime)
        #print(Total_Seconds)
        if Total_Seconds > 10:
            print("Missing Heartbeats")
            MainWindow.lblStatus.setFont(GlobalVars.MakeBold)
            MainWindow.lblStatus.setText("ERROR")
            MainWindow.lblStatus.setStyleSheet("background-color: red")
        else:
            #print("Remote Alive")
            MainWindow.lblStatus.setFont(GlobalVars.MakeNormal)
            MainWindow.lblStatus.setText("Connected")
            MainWindow.lblStatus.setStyleSheet("background-color: lightgreen")

    def CalcDisplayTimeDifference(self):
        if (GlobalVars.CurrentDistance != 0) :
            TotalSeconds = (GlobalVars.ElapsedTimeStart.secsTo(QTime.currentTime()))
            Minutes = math.trunc(TotalSeconds/60)
            Seconds = (TotalSeconds-(Minutes*60))
            if Minutes == 0 : 
                Seconds = TotalSeconds
                MainWindow.lblElapsedTime.setText(str(Seconds))
            else:
                MainWindow.lblElapsedTime.setText(str(Minutes) + ":" + str(Seconds))
#**********************************************************Misc Functions***********************************************************#
def Convert_Number(InputVar):
    CVar1 = 0.0
    CVar2 = "0"
    try:
        CVar1 = float(InputVar)
        CVar2 = str(CVar1)
    except Exception:
        CVar2 = "0"
        return "0"
    return CVar2

def Convert_Pulse_to_Measurement(InVar):
    Tvar = 0.0
    if GlobalVars.Dunit == "Feet":
        Tvar = math.ceil(int(InVar)/float(Settings.XPPF))
    if GlobalVars.Dunit == "Yards":
        Tvar = (math.ceil(int(InVar)/float(Settings.XPPF)))/3
    if GlobalVars.Dunit == "Meters":
        Tvar = math.ceil(int(InVar)/float(Settings.XPPM))
    return Tvar


def ParseArduinoMessage(InputString):
    TVar1 = ""
    TVar3 = ""
    GlobalVars.Arduino_CurrentCommType = (InputString[5:7])
    TVar1 = (InputString[1:5])
    TVar3 = (InputString[7:11])
    TVar1 = TVar1 + TVar3
    if GlobalVars.Arduino_CurrentCommType == "XD":
        try:GlobalVars.Arduino_CurrentXPulseCount = int(TVar1)
        except Exception as errout: print(errout)
    if GlobalVars.Arduino_CurrentCommType == "AX":
        try:GlobalVars.Arduino_CurrentXPulseCount = int(TVar1)
        except Exception as errout: print(errout)


#GlobalVars.Arduino_CurrentXPulseCount
#GlobalVars.Arduino_CurrentCommType
#GlobalVars.Arduino_CurrentYPulseCount
#GlobalVars.Arduino_CurrentStatus




#*******************************************************************************Main********************************************************************
app = QApplication(sys.argv)
Settings = clsSettings
GlobalVars = clsGlobalVars
KeypadWindow = clsKeyPadWindow()
GlobalVars.OSType = os.name#check os to determine what com port to use
print("OS Type:")
print(GlobalVars.OSType)
#Set globals here before any windows are defined------------------------------
GlobalVars.Home = os.path.dirname(__file__) #Get OS default path of python stript start
print("Measurement Unit Type:")
GlobalVars.Dunit = "Yards"                  #Default to yards
GlobalVars.SerialString = ""                #Set Object
GlobalVars.TCounter = 0
GlobalVars.CurrentDistance = 0
GlobalVars.LoginType = 0
GlobalVars.SerialStatus = False
GlobalVars.HB = datetime(1900,1,1,1,1,1,1)  #Heartbeat
GlobalVars.PrevXValue = 0

GlobalVars.MakeBold=QtGui.QFont('Arial', 12)
GlobalVars.MakeBold.setBold(True)
GlobalVars.MakeNormal=QtGui.QFont('Arial', 9)
GlobalVars.MakeNormal.setBold(True)
GlobalVars.LightStatus = False
GlobalVars.Arduino_CurrentXPulseCount = 0
GlobalVars.Arduino_CurrentCommType = ""
GlobalVars.XMoveLockedIn = False

widget=QtWidgets.QStackedWidget()

setupwindow = SetupWindow()
AdvancedWindow = clsAdvancedWindow()
MainWindow = clsMainWindow()
ElapsedTimer = clsElapsedtimer()
MainWindow.lblNewpos.setText("")
MainWindow.lblNewpos.show()
MainWindow.lblMKeyPadError.setText("")
MainWindow.lblMKeyPadError.hide()


#-----------------------------------------------------------------Get Startup settings-----------------------------------------------------------------
GetSettings()
print("Getting Settings")
print (GlobalVars.Home)
print (Settings.Lane)
print(Settings.TempLogin)
GlobalVars.LoginType = Settings.TempLogin
#mainwindow.lblPosu.setText(GlobalVars.Dunit)
#mainwindow.lblPosu_2.setText(GlobalVars.Dunit)
#advancedwindow.lblPosu.setText(GlobalVars.Dunit)

if GlobalVars.OSType == "nt":               #TEST IF WINDOWS OR LINUX TO SET from settings file
    #GlobalVars.PortName = winportname
    GlobalVars.PortName = Settings.COMWIN
else:
    #GlobalVars.PortName = linuxportname
    GlobalVars.PortName = Settings.COMLINUX
#----------------------------------------------------------------Ititialize MQTT Client-------------------------------------------------------
MQTTID = "P1"#-------------------need to get from config
broker_address="10.0.0.1" #-------------------need to get from config
try:
    print("Creating new instance of MQTT")
    MQTTclient = mqtt.Client(MQTTID) #create new instance
    MQTTclient.on_connect = on_connect  # Define callback function for successful connection
    MQTTclient.on_message = on_message  # Define callback function for receipt of a message
    print("Connecting to MQTT broker")
    MQTTclient.connect(broker_address,1883, 17300)
    MQTTclient.publish("balls","ON")
    MQTTStatus = MQTTclient
    MQTTclient.loop_start()
    #client.loop_forever()  # Start networking daemon -------blocking - never use!!!!
    MQTTStatus.Status = True
except Exception:
    #MQTTStatus.Status = False
    print("MQTT Software error")
#----------------------------------------------------------------Initialize Serial Port-------------------------------------------------------
try:
    serth = SerialThread(GlobalVars.PortName, baudrate)   # Start serial thread
    print(GlobalVars.PortName)
    print("Init Serial")
    if GlobalVars.SerialStatus == False:
        serth.start()

except Exception:
    print("Serial connection failure")
    print("Settings Tried, Port:")
    print(GlobalVars.PortName)
    print("Baud:")
    print(baudrate)
#----------------------------------------------------------------Start PYQT Windows-----------------------------------------------------------
GlobalVars.ElapsedTimeStart = (QTime.currentTime())#set time started
MainWindow.show()
ApplySecurity("",Settings.TempLogin)


#Timed execution--------------------------------------------------------------
timer = QTimer()
HeartbeatTimer = QTimer()
#timer.timeout.connect(lambda: print('hi!'))
timer.timeout.connect(ElapsedTimer.CalcDisplayTimeDifference)
HeartbeatTimer.timeout.connect(ElapsedTimer.Heartbeat)
timer.start(1000)
HeartbeatTimer.start(5000)
#Main Loop execution error handling--------------------------------------------------------------


try:
    sys.exit(app.exec_())
except Exception:
    print("Exiting with fatal error")
