    #---------------------------------------------------------------------------Setup Window------------------------------------------------
class SetupWindow(QWidget):
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
        #check Values
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

        if str.isnumeric(self.txtAutoHome.toPlainText()) == False: TooFar = True  #Check Auto Return
        else: TooFar = MaxValue(self.txtAutoHome.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtAutoHome.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtAutoHome.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtSleep.toPlainText()) == False: TooFar = True  #Check Sleep
        else: TooFar = MaxValue(self.txtSleep.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtSleep.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtSleep.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file

        if str.isnumeric(self.txtError.toPlainText()) == False: TooFar = True  #Check error
        else: TooFar = MaxValue(self.txtError.toPlainText(),999,"MAX")
        if TooFar:
            setupwindow.txtError.setPlainText("INVALID VALUE")
            setupwindow.lblError.show()
            setupwindow.txtError.setStyleSheet("background-color: yellow")
            return#exit function **Do not Write to data file
        
        #Get the configparser object
        config_object = ConfigParser()
        #Write 1 section in the config file
        config_object["DEVICESETTINGS"] = {
        "lane": self.txtLane.toPlainText()
        ,"maxfeet": self.txtMaxFeet.toPlainText()
        ,"autohome": self.txtAutoHome.toPlainText()
        ,"sleep": self.txtSleep.toPlainText()
        ,"error": self.txtError.toPlainText()
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