#HMI PII code designed for 800X480
import sys
import os
import time
import serial
import math
import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import pyqtSignal,QTime,QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget
from configparser import ConfigParser
from PyQt5.uic import loadUi
from threading import Thread
import queue as Queue
#https://iosoft.blog/2019/04/30/pyqt-serial-terminal/


SER_TIMEOUT = 0.1                   # Timeout for serial Rx
RETURN_CHAR = "\n"                  # Char to be sent when Enter key pressed
PASTE_CHAR  = "\x16"                # Ctrl code for clipboard paste
baudrate    = 9600                # Default baud rate
winportname    = "COM3"                # Default port name
linuxportname    = "/dev/ttyUSB0"                # Default port name
hexmode     = False                 # Flag to enable hex display


#*******************************************************************************Main Window*******************************************************************************
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'MainWindow.ui'),self)
        #self.lblElapsedTime.setText("")
        self.cmdLogin.clicked.connect(self.gotoLogin)
        self.cmdSetup.clicked.connect(self.gotoSetupWindow)
        self.cmdAdvanced.clicked.connect(self.gotoAdvancedWindow)
        self.cmdMKeyPadDelete.clicked.connect(lambda: self.gotoDataDelete(self.lblNewpos.text(),self.lblNewpos))
        self.cmdMKeyPadGo.clicked.connect(lambda: self.gotoDataEntry(self.lblNewpos.text(),self.lblPos,self.lblNewpos,self.lblMKeyPadError,self.lblPosu.text()))
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
        self.cmdUnit.clicked.connect(lambda: self.gotoChangeMeasurement(self.lblPosu,self.lblPosu_2))
    def gotoLogin(self):
        #keypadwindow.cmdCancelPassword.show()
        SetKeypadType("Password")
        keypadwindow.show()
    def gotoChangeMeasurement(self,lblPosu,lblPosu_2):
        global DistanceUnit
        if lblPosu.text() == "Yards":
            lblPosu.setText("Feet")
            lblPosu_2.setText("Feet")
            GlobalVars.Dunit = ("Feet")
            advancedwindow.lblPosu.setText("Feet")
        else:
            lblPosu.setText("Yards")
            lblPosu_2.setText("Yards")
            GlobalVars.Dunit = ("Yards")
            advancedwindow.lblPosu.setText("Yards")
    def gotoAdvancedWindow(self):
        self.hide()
        advancedwindow.show()
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
    def gotoDataEntry(self,NewValue,lblCurPOS,lblNewPOS,lblMKeyPadError,lblPosu):
        intMinimumDistance = 0
        intMaximumDistance = 0
        if NewValue == "": NewValue = 0
        if lblPosu != "Feet":#Retrieve and convert min/Max distances Yards or Meters
            intMinimumDistance = ConvertUnit(GlobalVars.MinFeet,GlobalVars.Dunit,"MIN")
            intMaximumDistance = ConvertUnit(GlobalVars.MaxFeet,GlobalVars.Dunit,"MAX")
        if lblPosu == "Feet":#Retrieve Min/Max Distances
            intMinimumDistance = int(GlobalVars.MinFeet)
            intMaximumDistance = int(GlobalVars.MaxFeet)
        #evaluate Min/Max with user input
        if (int(NewValue) >= intMinimumDistance) and (int(NewValue) <= intMaximumDistance):TooClose = False
        else: TooClose=True

        if TooClose == True :
            lblMKeyPadError.show()
            lblMKeyPadError.setText("Value not allowed")
            lblNewPOS.setText("")
        else:
            GlobalVars.ElapsedTimeStart = QTime.currentTime()
            lblNewPOS.setText("")
            lblCurPOS.setText(NewValue)
            GlobalVars.CurrentDistance = int(NewValue)
            lblMKeyPadError.hide()
            lblMKeyPadError.setText("")
            print("Data Entered")

#*******************************************************************************Keypad entry*******************************************************************************
def SetKeypadType(KeypadType):
        if KeypadType == "KeypadX": 
            keypadwindow.lblTitle.setText("Move X Distance")
            keypadwindow.lblKeyPadType.setText("KeypadX")
        if KeypadType == "KeypadRCW": 
            keypadwindow.lblTitle.setText("Rotate Degrees CW")
            keypadwindow.lblKeyPadType.setText("KeypadRCW")
        if KeypadType == "KeypadRCCW": 
            keypadwindow.lblTitle.setText("Rotate Degrees CCW")
            keypadwindow.lblKeyPadType.setText("KeypadRCCW")
        if KeypadType == "Password": 
            keypadwindow.lblTitle.setText("Password Entry")
            keypadwindow.lblKeyPadType.setText("Password")
        if KeypadType == "DelaySeconds": 
            keypadwindow.lblTitle.setText("Delay Seconds")
            keypadwindow.lblKeyPadType.setText("DelaySeconds")


class KeyPad(QWidget):
    def __init__(self):
        super(KeyPad, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'KeyPad.ui'),self)
        global KeyPadEntry
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
        try:
            intKeyPadValue = int(KeyPad.Value)
        except Exception:
            intKeyPadValue = 0

        if self.lblKeyPadType.text() =="KeypadX":
            if GlobalVars.Dunit != "Feet":#Convert Min max from setup-feet to Yards.Round up for min, round down for Max
                intMinimumDistance = ConvertUnit(GlobalVars.MinFeet,GlobalVars.Dunit,"MIN")
                intMaximumDistance = ConvertUnit(GlobalVars.MaxFeet,GlobalVars.Dunit,"MAX")
            if GlobalVars.Dunit == "Feet":
                intMinimumDistance = int(GlobalVars.MinFeet)
                intMaximumDistance = int(GlobalVars.MaxFeet)
            if (intKeyPadValue >= intMinimumDistance) and (intKeyPadValue <= intMaximumDistance):FinishExit = True
            else:
                lblError.show()
                lblError.setText("Value too Small or Large")
                lblOut.setText("")

        if self.lblKeyPadType.text() =="KeypadRCW":#Max degrees, cannot exceed 360
            if intKeyPadValue >= 361: KeyPad.Value = "360"
            FinishExit = True
        if self.lblKeyPadType.text() =="KeypadRCCW":#Max degrees, cannot exceed 360
            if intKeyPadValue >= 361: KeyPad.Value = "360"
            FinishExit = True
        if self.lblKeyPadType.text() =="Password":
            ReturnSecurity = AuthenticateUser(self,intKeyPadValue)
            if ReturnSecurity != "FAIL":
                mainwindow.lblSecurity.setText(ReturnSecurity)
                GlobalVars.LoginType = int(ReturnSecurity)
                ApplySecurity(self,int(ReturnSecurity))
                FinishPassword = True
            else:
                lblError.setText("Password Incorrect")
                lblOut.setText("")
                lblError.show()

        if self.lblKeyPadType.text() =="DelaySeconds":
            if intKeyPadValue >= 3601: KeyPad.Value = "3600"#Max seconds, cannot exceed 3600 (1 hour)
            FinishExit = True
        if FinishExit == True:
            self.ExitKeypadToAdvanced(self.lblTitle.text())#Set entry in list and clean up
            lblError.setText("")
            lblError.hide()
            self.hide()
        if FinishPassword == True:
            lblError.setText("")
            lblError.hide()
            KeyPadEntry.setText("")
            self.hide()

    def ExitKeypadToAdvanced(self,LineEntry):#Set entry in list and clean up
        print(KeyPad.Value)
        CommandList.addItem(LineEntry + ": " + KeyPad.Value)#add list value
        KeyPadEntry.setText("")
        self.hide()
    def gotoEnterDigit(self,DigitValue,lblError):
        KeyPad.Value = KeyPadEntry.text()
        lblError.hide()
        if KeyPad.Value == "0":
            KeyPad.Value = ""
        if self.lblKeyPadType.text() !="DelaySeconds" and self.lblKeyPadType.text() !="Password" :#If entering distance or rotation, allow only 3 digits
            if len(KeyPad.Value) < 3:
                KeyPad.Value = KeyPad.Value + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(KeyPad.Value)
        if self.lblKeyPadType.text() =="DelaySeconds":#If entering seconds, allow 4 digits
            if len(KeyPad.Value) < 4:
                KeyPad.Value = KeyPad.Value + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(KeyPad.Value)
        if self.lblKeyPadType.text() =="Password":#If entering Password, allow 8 digits
            if len(KeyPad.Value) < 8:
                KeyPad.Value = KeyPad.Value + DigitValue
                KeyPadEntry.clear()
                KeyPadEntry.setText(KeyPad.Value)
    def gotoDataDelete(self):
        KeyPad.Value = KeyPadEntry.text()
        if len(KeyPad.Value) > 1:
            KeyPad.Value = KeyPad.Value[:- 1]
            KeyPadEntry.clear()
            KeyPadEntry.setText(KeyPad.Value)
        else:
            KeyPadEntry.clear()

#*******************************************************************************Setup Window*******************************************************************************
class SetupWindow(QWidget):
    trigger = pyqtSignal()
    def __init__(self):
        super(SetupWindow, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'SetupWindow.ui'),self)
        self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)
        self.cmdExit.clicked.connect(self.gotoMainWindow)
        self.cmdRestart.clicked.connect(self.gotoRestart)
        self.cmdBasicApply.clicked.connect(self.gotoBasicApply)
        self.cmdDeviceApply.clicked.connect(self.gotoDeviceApply)
        self.cmdSendSerialString.clicked.connect(lambda: self.gotoSendSerialString(self.lblButtonCounter))
        self.cmdSendSerialChar1.clicked.connect(lambda: self.gotoSendSerialChar1(self.lblButtonCounter))#<
        self.cmdSendSerialChar2.clicked.connect(self.gotoSendSerialChar2)#x
        self.cmdSendSerialChar3.clicked.connect(self.gotoSendSerialChar3)#>
        self.cmdSendMQTTString.clicked.connect(self.gotoSendMQTTString)
        self.trigger.connect(lambda: self.gotoPopulateSerialData(self.lblSerOut,self.lblSerOut2))#trigger serial data recieved
            
    def gotoPopulateSerialData(self,SerOut,SerOut2):
            print("gotoPopulateSerialData")
            print(GlobalVars.SerialString)
            SerOut.setText(GlobalVars.RawSerialString)
            SerOut2.setText(GlobalVars.SerialString)
            setupwindow.lblSerOut2.setText(GlobalVars.SerialString)
            GlobalVars.SerialString = "" #Clear serial data

    def gotoSendSerialString(self,lblCounter):
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
        mainwindow.show()
    def gotoRestart(self):
        try:
            os.system('sudo restart')
        except Exception:
            print("Could Not Restart")
    def gotoBasicApply(self):
        print("BasicApply")
        #Reset errors and colors
        setupwindow.lblError.hide()
        setupwindow.txtLane.setStyleSheet("background-color: white")
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
            setupwindow.txtMaxFeet.setPlainText("Cannot be 0")
            setupwindow.lblError.show()
            setupwindow.txtMaxFeet.setStyleSheet("background-color: yellow")
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
        if self.rdoFeet.isChecked() : DefaultUnits = "Feet"
        if self.rdoYards.isChecked() : DefaultUnits = "Yards"
        if self.rdoMeters.isChecked() : DefaultUnits = "Meters"


        #Get the configparser object
        config_object = ConfigParser()
        #Write 1 section in the config file
        config_object["DEVICESETTINGS"] = {
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
        }
        #Write the above sections to device.ini file
        outfile = os.path.join(os.path.dirname(__file__), 'basic.ini')
        with open(outfile, 'w') as conf:
            config_object.write(conf)

    def gotoDeviceApply(self):
        print("DeviceApply")
        #Get the configparser object
        config_object = ConfigParser()
        #Write 1 section in the config file
        config_object["DEVICESETTINGS"] = {
        "xfast": "12345"
        ,"xfastramp": "12345"
        ,"xslow": "12345"
        ,"xslowramp": "12345"
        ,"xcreep": "12345"
        ,"rollaxis": "10"
        ,"rollfast": "12345"
        ,"rollslow": "12345"
        ,"light": "10"
        ,"acc1": "10"
        ,"acc2": "10"
        ,"acc3": "10"
        ,"acc4": "10"
        }
        #Write the above sections to device.ini file
        outfile = os.path.join(os.path.dirname(__file__), 'device.ini')
        with open(outfile, 'w') as conf:
            config_object.write(conf)
#*******************************************************************************Advanced Window*******************************************************************************
class AdvancedWindow(QWidget):
    def __init__(self):
        super(AdvancedWindow, self).__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(GlobalVars.Home, 'AdvancedWindow.ui'),self)
        print(GlobalVars.Dunit)
        self.cmdExit.clicked.connect(self.gotoMainWindow)
        self.cmdTargetCW.clicked.connect(self.gotoTargetRCW)
        self.cmdTargetCCW.clicked.connect(self.gotoTargetRCCW)
        self.cmdDelay.clicked.connect(self.gotoDelay)
        self.cmdLighton.clicked.connect(self.gotoLightOn)
        self.cmdLightoff.clicked.connect(self.gotoLightOff)
        self.cmdRepeat.clicked.connect(self.gotoRepeat)
        self.cmdRemovelast.clicked.connect(self.gotoRemoveLast)
        global CommandList #Need global for button assignments
        global CommandList2
        CommandList = QListWidget(self.lstCommand)
        CommandList2 = QListWidget(self.lstCommand2)
        self.cmdX.clicked.connect(self.gotoEnterX)
    def gotoEnterX(self):
        SetKeypadType("KeypadX")
        keypadwindow.show()

    def gotoTargetRCCW(self):
        SetKeypadType("KeypadRCCW")
        keypadwindow.show()

    def gotoTargetRCW(self):
        SetKeypadType("KeypadRCW")
        keypadwindow.show()

    def gotoDelay(self):
        SetKeypadType("DelaySeconds")
        keypadwindow.show()
    def gotoLightOn(self):
        CommandList.addItem("Target Light On")
    def gotoLightOff(self):
        CommandList.addItem("Target Light Off")
    def gotoRepeat(self):
        CommandList.addItem("Repeat")
    def gotoRemoveLast(self):
        CommandList.takeItem(CommandList.count()-1)
    def gotoMainWindow(self):
        CommandList.clear()
        CommandList2.clear()
        self.hide()
        mainwindow.show()



#*******************************************************************************Settings class*******************************************************************************
class Settings:
    def __init__(self,Lane, MaxFeet, AutoHome, Sleep, Error,TempLogin,AllowFeet,AllowYards,AllowMeters,EnableFeet,EnableYards,EnableMeters,DefaultUnits):
        self.Lane=Lane
#*******************************************************************************GlobalVars class*******************************************************************************
class GlobalVars:
    def __init__(self,Home,Dunit,OSType,PortName,BaudRate,RawSerialString,SerialString,TCounter,ElapsedTimeStart,CurrentDistance,MinFeet,MaxFeet,LoginType):
        self.SerialString = SerialString
        self.RawSerialString = RawSerialString
        self.TCounter = TCounter
        self.ElapsedTimeStart = ElapsedTimeStart
        self.CurrentDistance = CurrentDistance
        #self.SerialString = pyqtSignal(name = SerialString) #Need to define this so that the differnt thread can send data
        #valueChanged = pyqtSignal([int], ['QString'])
        self.Home = Home
#*******************************************************************************Keypad class*******************************************************************************
class Keypad:
    def __init__(self,Value):
        self.Value = Value
#*******************************************************************************MQTT status class*******************************************************************************
    def __init__(self,Status,Client):
        self.Status = Status


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$General Purpose functions$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#*******************************************************************************Measurement conversion *******************************************************************************
def ConvertUnit(Feet,CurrentUnit,MinMax):#Convert Min max from setup-feet to Yards.Round up for min, round down for Max
    OutUnit = 0
    try:
        intFeet = int(Feet)
        if MinMax == "MIN":
            if CurrentUnit == "Yards": OutUnit = (int(math.ceil(intFeet/3)))
            if CurrentUnit == "Meters": OutUnit = (int(math.ceil(intFeet/3.2808)))
        if MinMax == "MAX":
            if CurrentUnit == "Yards": OutUnit = (int(math.floor(intFeet/3)))
            if CurrentUnit == "Meters": OutUnit = (int(math.floor(intFeet/3.2808)))
    except Exception:
        return 0
    return OutUnit
#*******************************************************************************Maximum Value*******************************************************************************
def MaxValue(InvalRaw,CompareValueRaw,MaxMin):
    BinOut = False
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
    try:
        config_object = ConfigParser()
        infile = os.path.join(GlobalVars.Home, 'basic.ini')
        config_object.read(infile)
        #Get a key
        deviceinfo = config_object["DEVICESETTINGS"]
        try: Settings.Lane = deviceinfo["lane"]
        except Exception: Settings.Lane = "Default"

        Settings.MaxFeet = deviceinfo["maxfeet"]
        GlobalVars.MaxFeet = Settings.MaxFeet
        Settings.MinFeet = deviceinfo["minfeet"]
        GlobalVars.MinFeet = Settings.MinFeet
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

        try: TDefaultUnits = (deviceinfo["defaultunits"])
        except Exception: TDefaultUnits = "Feet"
        if TDefaultUnits != "Feet" and TDefaultUnits != "Yards" and TDefaultUnits != "Meters":TDefaultUnits = "Feet"#set default unit if not recognized
        Settings.DefaultUnits = str(TDefaultUnits)
    except Exception:
        print("Config file ERROR! Config file is missing or corrupt.  Loading defaults")
        print(str(Settings.EnableFeet))
        Settings.TempLogin = 0
def LoadSettingstoWindow():
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
        match Settings.DefaultUnits:
            case "Feet":
                setupwindow.rdoFeet.setChecked(True)
            case "Yards":
                setupwindow.rdoYards.setChecked(True)
            case "Meters":
                setupwindow.rdoMeters.setChecked(True)
            case _:
                setupwindow.rdoFeet.setChecked(True)

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
            print("Serial Len OK. Send to Screen")
            print(GlobalVars.SerialString)
            setupwindow.trigger.emit() #send a global trigger signal so that PYQT windows can update with data
            SerialDataRecieved = ""
         
    def run(self):                          # Run serial reader thread
        print("Opening %s at %u baud %s" % (self.portname, self.baudrate,
              "(hex display)" if hexmode else ""))
        try:
            self.ser = serial.Serial(self.portname, self.baudrate, timeout=SER_TIMEOUT)
            time.sleep(SER_TIMEOUT*1.2)
            self.ser.flushInput()
        except:
            self.ser = None
        if not self.ser:
            print("Cannot open serial port")
            self.running = False
        while self.running:
            s = self.ser.read(self.ser.in_waiting or 1)
            if s:                                       # Get data from serial port
                self.ser_in(bytes_str(s))               # ..and convert to string
            if not self.txq.empty():
                txd = str(self.txq.get())               # If Tx data in queue, write to serial port
                self.ser.write(str_bytes(txd))
        if self.ser:                                    # Close serial port when thread finished
            self.ser.close()
            self.ser = None


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
    mainwindow.lblSecurity.setText(str(UserLevel))
    if UserLevel == 0:
        mainwindow.cmdSetup.hide() 
        mainwindow.cmdAdvanced.hide() 
        mainwindow.cmdUnit.hide()
    if UserLevel == 1:
        mainwindow.cmdSetup.hide()
        mainwindow.cmdAdvanced.hide() 
        mainwindow.cmdUnit.show()
    if UserLevel == 2:
        mainwindow.cmdSetup.hide()
        mainwindow.cmdAdvanced.show()
        mainwindow.cmdUnit.show()
    if UserLevel == 3:
        mainwindow.cmdSetup.show()
        mainwindow.cmdAdvanced.show()
        mainwindow.cmdUnit.show()
    if UserLevel == 4:
        mainwindow.cmdSetup.show()
        mainwindow.cmdAdvanced.show()
        mainwindow.cmdUnit.show()
    

#****************************************************************************ElapsedTimer****************************************************************
class elapsedtimer:
    def CalcDisplayTimeDifference(self):
        if (GlobalVars.CurrentDistance != 0) :
            TotalSeconds = (GlobalVars.ElapsedTimeStart.secsTo(QTime.currentTime()))
            Minutes = math.trunc(TotalSeconds/60)
            Seconds = (TotalSeconds-(Minutes*60))
            if Minutes == 0 : 
                Seconds = TotalSeconds
                mainwindow.lblElapsedTime.setText(str(Seconds))
            else:
                mainwindow.lblElapsedTime.setText(str(Minutes) + ":" + str(Seconds))

#*******************************************************************************Main********************************************************************
app = QApplication(sys.argv)
GlobalVars.OSType = os.name
print("OS Type:")
print(GlobalVars.OSType)
if GlobalVars.OSType == "nt":               #TEST IF WINDOWS OR LINUX TO SET PORTNAME
    GlobalVars.PortName = winportname
else:
    GlobalVars.PortName = linuxportname
#Set globals here before any windows are defined------------------------------
GlobalVars.Home = os.path.dirname(__file__) #Get OS default path of python stript start
print("Measurement Unit Type:")
GlobalVars.Dunit = "Yards"                  #Default to yards
GlobalVars.SerialString = ""                #Set Object
GlobalVars.TCounter = 0
GlobalVars.CurrentDistance = 0
GlobalVars.LoginType = 0
widget=QtWidgets.QStackedWidget()
keypadwindow = KeyPad()
setupwindow = SetupWindow()
advancedwindow = AdvancedWindow()
mainwindow = MainWindow()
ElapsedTimer = elapsedtimer()
mainwindow.lblNewpos.setText("")
mainwindow.lblNewpos.show()
mainwindow.lblMKeyPadError.setText("")
mainwindow.lblMKeyPadError.hide()
#-----------------------------------------------------------------Get Startup settings-----------------------------------------------------------------
GetSettings()
print("Getting Settings")
print (GlobalVars.Home)
print (Settings.Lane)
print(Settings.TempLogin)
GlobalVars.LoginType = Settings.TempLogin
mainwindow.lblPosu.setText(GlobalVars.Dunit)
mainwindow.lblPosu_2.setText(GlobalVars.Dunit)
advancedwindow.lblPosu.setText(GlobalVars.Dunit)
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
#----------------------------------------------------------------Ititialize Serial Port-------------------------------------------------------
try:
    serth = SerialThread(GlobalVars.PortName, baudrate)   # Start serial thread
    serth.start()
except Exception:
    print("Serial connection failure")
    print("Settings Tried, Port:")
    print(GlobalVars.PortName)
    print("Baud:")
    print(baudrate)
#----------------------------------------------------------------Start PYQT Windows-----------------------------------------------------------
GlobalVars.ElapsedTimeStart = (QTime.currentTime())#set time started
mainwindow.show()
ApplySecurity("",Settings.TempLogin)


#Timed execution--------------------------------------------------------------
timer = QTimer()
#timer.timeout.connect(lambda: print('hi!'))
timer.timeout.connect(ElapsedTimer.CalcDisplayTimeDifference)
timer.start(1000)
#Main Loop execution error handling--------------------------------------------------------------

try:
    sys.exit(app.exec_())
except Exception:
    print("Exiting with fatal error")
