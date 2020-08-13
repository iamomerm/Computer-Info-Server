import os
import sys
import platform
import psutil
import shutil
from flask import Flask, render_template
from bs4 import BeautifulSoup

Root = os.path.dirname(os.path.realpath(__file__))

Template = Root + '/templates/template.ht'
myHTML = Root + '/templates/index.html'

if os.path.exists(myHTML):
    os.remove(myHTML)
    
shutil.copy2(Template, myHTML)
    
# - HTML Generator -
class ComputerInfo:

    def __init__(self):
        
        # - Computer -
        self.cName = os.environ['COMPUTERNAME']
        
        # - Operating System -
        self.osName = sys.platform
        self.osVersion = platform.version()
        self.osPlatform = platform.machine()
        self.OS = self.osName + ' ' + self.osVersion + ' ' + self.osPlatform

        # - Hardware Info -
		
        #CPU
        self.cProcessor = platform.processor()
        self.cProcessorUsage = psutil.cpu_percent(interval=1)
		
        #Drives
        Drives = psutil.disk_partitions()
        self.DrivesInfo = [] #total, used, free, precent
        
        for Drive in Drives:
            try:
                driveUsage = psutil.disk_usage(Drive.device)
                self.DrivesInfo.append([Drive.device, driveUsage])
            except:
                pass

        #Memory
        self.ramTotal = psutil.virtual_memory().total
        self.ramAvailable = psutil.virtual_memory().available
        self.ramUsed = psutil.virtual_memory().used
        self.ramPercent = psutil.virtual_memory().percent
        
class HGenerator:
    
    def __init__(self):
    
        #Get Computer Information
        myComputer = ComputerInfo()

        #Get HTML Content
        with open (myHTML) as HTML:
            Soup = BeautifulSoup(HTML, 'lxml')
            
        #Computer Name
        myHeader = Soup.find(id='Header')
        myHeader.string = str(myComputer.cName)

        #CPU
        myCPU = Soup.find(id='CPU')
        myCPU.string = 'CPU: ' + str(myComputer.cProcessor)

        myCPUusage = Soup.find(id='CPU-Usage')
        myCPUusage.string = 'CPU Usage: ' + str(myComputer.cProcessorUsage) + ' %'

        #OS
        myOS = Soup.find(id='OS')
        myOS.string = 'OS: ' + str(myComputer.OS)

        #Memory
        myTotalRam = Soup.find(id='Ram-Total')
        myTotalRam.string = 'Total Ram: ' + str(int(myComputer.ramTotal) / 1000000) + ' Mb'

        myAvailableRam = Soup.find(id='Ram-Available')
        myAvailableRam.string = 'Available Ram: ' + str(int(myComputer.ramAvailable) / 1000000) + ' Mb ' + str(100 - int(myComputer.ramPercent)) + '%'

        myUsedRam = Soup.find(id='Ram-Used')
        myUsedRam.string = 'Used Ram: ' + str(int(myComputer.ramUsed) / 1000000) + ' Mb ' + str(myComputer.ramPercent) + '%'

        #Drives
        myDrives = myComputer.DrivesInfo
        InfoDiv = Soup.find(id='Information-Div')

        #Clear Previous Data
        for aDrive in Soup.find_all("h3", {'id':'Drive'}): 
            aDrive.decompose()

        for Drive in myDrives:
            dName = str(Drive[0])           
            myDrive = Soup.new_tag('h3', attrs={'class':'Information', 'id':'Drive'})
            myDrive.string = 'Drive: ' + dName + ' - Size: ' + str(int(Drive[1].total / 1000000)) + ' Mb, Used: ' + str(int(Drive[1].used / 1000000)) + ' Mb ' + str(Drive[1].percent) + '%, Free: ' + str(int(Drive[1].free / 1000000)) + ' Mb ' + str(100 - int(Drive[1].percent)) + '%'
            InfoDiv.append(myDrive)
            
        with open(myHTML, "w") as nHTML:
            nHTML.write(str(Soup))

Application = Flask(__name__)

@Application.route("/")
def Home():
    Generate = HGenerator()
    return render_template('index.html')

if __name__ == '__main__':
    Application.run(debug=False, host='0.0.0.0', port=8000)
