#github.com/thegrayninja
#
##identify agents that do not belong to a group
##save them to their own OS file, hostname only.
#
#Current Version: 0.2.1
#Version Notes: adding remaining Enter to Continue statements, DeleteStaleAgents(), 
#               DeleteLastCheckedIn(), GetAllAgentCount()
#
#Version History
#ver 0.2.0 - removing support for python 2.x and older
#ver 0.2.1 - first stab at combining all useful scripts


import requests
import time, sys, os
import subprocess, platform

from auth_file import tenable_header


added_count = 0

def CheckPythonVersion():
    PyVerTuple = sys.version_info[:1]
    if PyVerTuple[0] > 2:
        return 0
    else:
        print("\n\nPlease run Python 3.x or newer\n")
        sys.exit(1)



def GetGroupInformation():
    return((requests.get('https://cloud.tenable.com/scanners/1/agent-groups', headers=tenable_header)).json())



def GetAgentsInformation():
    url = 'https://cloud.tenable.com/scanners/1/agents/'
    return(requests.get(url, headers=tenable_header)).json()



##NOTE For AgentGroupExist
def AgentGroupExist():
    LinuxAgentGroupNull = ""
    MacAgentGroupNull = ""
    UnknownAgentGroupNull = ""
    WindowsAgentGroupNull = ""
    counter = 0
    TotalUnassigned = 0
    AgentInfo = GetAgentsInformation()
    print("\n\nThe following assets do not belong to a group:\n")
    for i in (AgentInfo["agents"]):
        if AgentInfo["agents"][counter]["groups"] == None:
            AgentName = AgentInfo["agents"][counter]["name"]
            AgentOS = AgentInfo["agents"][counter]["platform"]
            TotalUnassigned += 1
            print("\t%s. %s - %s" % (TotalUnassigned, AgentName, AgentOS))
            if "DARWIN" in AgentOS:
                MacAgentGroupNull += "%s\n" % AgentName
            elif "LINUX" in AgentOS:
                LinuxAgentGroupNull += "%s\n" % AgentName
            elif "Windows" in AgentOS:
                WindowsAgentGroupNull += "%s\n" % AgentName
            else:
                UnknownAgentGroupNull += "%s\n" % AgentName

        counter += 1
    input("\nPress Return/Enter to Continue...")
    SaveAgentsToFile(LinuxAgentGroupNull, "LinuxAgentGroupNull.txt")
    SaveAgentsToFile(MacAgentGroupNull, "MacAgentGroupNull.txt")
    SaveAgentsToFile(UnknownAgentGroupNull, "UnknownAgentGroupNull.txt")
    SaveAgentsToFile(WindowsAgentGroupNull, "WindowsAgentGroupNull.txt")
    print("\n\nData has been saved")
    #print("\nA total of %s agents do not belong to a group" % TotalUnassigned)
    print("\nPlease review the following files for additional information:")
    print("\t./LinuxAgentGroupNull.txt\n\t./MacAgentGroupNull.txt\n\t./WindowsAgentGroupNull.txt")
    print("\t./UnknownAgentGroupNull.txt")
    input("\nPress Return/Enter to Continue...")
    menu()
    return(0)



def ShowGroups():
    GroupInfo = GetGroupInformation()
    counter = 0
    for i in (GroupInfo["groups"]):
        GroupName = GroupInfo["groups"][counter]["name"]
        GroupID = GroupInfo["groups"][counter]["id"]
        print("ID: %s\tName: %s" %(GroupID, GroupName))
        counter += 1


##NOTE For AddAgentsToGroup
##TODO Update this function..name is lame and variables are jacked
def is_in(agentip, agentid, agentname, UserGroupSelection, AgentHostnames):
    #global import_search_strings
    #global search_group_id
    for ss in AgentHostnames:
        search_string = ss.strip()
        if search_string in agentname:
            url = 'https://cloud.tenable.com/scanners/1/agent-groups/%s/agents/%s' % (UserGroupSelection, agentid)
            temp_container = requests.put(url, headers=tenable_header)
            newentry = ("%s - %s was added to the group %s" % (agentip, agentname, UserGroupSelection))
            newFile = open("tenable_added_to_group.log", "a")
            newFile.write("%s\n" % (newentry))
            newFile.close()
            print (newentry)
            time.sleep(.3)
            global added_count
            added_count += 1


def AddAgentsToGroup():
    AgentHostnames = ReadImportedFile()
    ShowGroups()
    UserGroupSelection = input("Please Enter Group ID: ")

    AgentInfo = GetAgentsInformation()
    Counter = 0
    Results = ""
    AgentsScanned = ""
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        is_in(AgentIP, AgentID, AgentName, UserGroupSelection, AgentHostnames)
        Counter += 1
    print(added_count)
    input("\nPress Return/Enter to Continue...")
    menu()


def DeleteStaleAgents():
    #agents that are part of a group which have not scanned within 60 days
    ListDeletedAgents = ""
    DeletedCount = 0
    TimeDiff = 7872650 #roughly 60 days
    Counter = 0
    AgentInfo = GetAgentsInformation()
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        LastScanned = (AgentInfo["agents"][Counter]["last_scanned"])

        if (AgentInfo["agents"][Counter]["groups"] == None):
            continue
        elif (LastScanned == None):
            continue
        elif (LastScanned + TimeDiff) < time.time():
            CurrentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            LastScannedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(LastScanned))
            URL = 'https://cloud.tenable.com/scanners/1/agents/%s' % (AgentID)
            DeleteAgent = requests.delete(URL, headers=tenable_header)
            #TestDeleteAgent = requests.get(URL, headers=tenable_header)
            ListDeletedAgents = ("%s (%s) was deleted at %s. Last Scanned at %s" %(AgentName, AgentIP, CurrentTime, LastScannedTime))
            DeletedAgentsFile = open("DeletedStaleAssets.log", "a")
            DeletedAgentsFile.write("%s\n" % (ListDeletedAgents))
            DeletedAgentsFile.close()
            print(ListDeletedAgents)
            time.sleep(.3)
            DeletedCount += 1
        Counter +=1
    print("\n%d Agents have been deleted" % (DeletedCount))
    print("You can review the deleted assets in DeletedStaleAssets.log")
    input("\nPress Return/Enter to Continue...")
    menu()


def DeleteLastCheckedIn():
    #all agents which have not checkedin within 60 days
    ListDeletedAgents = ""
    DeletedCount = 0
    TimeDiff = 7872650 #roughly 60 days
    Counter = 0
    AgentInfo = GetAgentsInformation()
    for i in (AgentInfo["agents"]):
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        LastChecked = AgentInfo["agents"][Counter]["last_connect"]
        if LastChecked != None:
            if (LastChecked + TimeDiff) < time.time():
                LastCheckedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(LastChecked))
                #print("%s - %s" % (AgentName, LastCheckedTime))

                CurrentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                LastCheckedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(LastChecked))
                URL = 'https://cloud.tenable.com/scanners/1/agents/%s' % (AgentID)
                DeleteAgent = requests.delete(URL, headers=tenable_header)
                #TestDeleteAgent = requests.get(URL, headers=tenable_header)
                ListDeletedAgents = ("%s (%s) was deleted at %s. Last Checked-in at %s" %(AgentName, AgentIP, CurrentTime, LastCheckedTime))
                DeletedAgentsFile = open("DeletedDisconnectedAssets.log", "a")
                DeletedAgentsFile.write("%s\n" % (ListDeletedAgents))
                DeletedAgentsFile.close()
                print(ListDeletedAgents)
                time.sleep(.3)
                DeletedCount += 1
        Counter += 1
    print("\n%d Agents have been deleted" % (DeletedCount))
    print("You can review the deleted assets in DeletedDisconnectedAssets.log")
    input("\nPress Return/Enter to Continue...")
    menu()
    return 0


def GetAllAgentCount():
    AgentInfo = GetAgentsInformation()
    TotalAgents = 0
    for i in (AgentInfo["agents"]):
        TotalAgents += 1
    print("\nThere are a total of %d Agents" % (TotalAgents))
    input("\nPress Return/Enter to Continue...")
    menu()
    return 0


def DownloadAgentInstallers():

    #TODO copy/paste Download Agent code here
    AgentList = ["-amzn.x86_64.rpm", "-debian6_amd64.deb", "-es5.x86_64.rpm",
                  "-es6.x86_64.rpm", "-es7.x86_64.rpm", "-fc20.x86_64.rpm",
                  "-suse11.x86_64.rpm", "-suse12.x86_64.rpm", "-ubuntu910_amd64.deb",
                  "-ubuntu1110_amd64.deb", ".dmg", "-x64.msi"]

    AgentVersion = input("Please enter the Agent Version (Ex: NessusAgent-6.11.1):")
    print("\nNOTE: You must enter the License Agreement Cookie. No way around this that I have discovered.")
    print("To get your cookie, go here: http://www.tenable.com/products/nessus/select-your-operating-system#tos")
    print("and click on any file to download. Accept the terms, then right-click the Download button and copy ")
    print("the link. The end of the string will contain the cookie. Copy it and paste in the field below.\n")
    TenableCookie = (input("Enter License Agreement Cookie (Ex: 1ea0fe39437453a7e12a12115194e8e5):")).strip()
    OSVersion = (platform.system())
    if "Windows" in OSVersion:
        ##TODO For Windows --doesn't work
        SaveFolder = r'.\Agents'
        if not os.path.exists(SaveFolder):
            os.makedirs(SaveFolder)
        AgentList = "-x64.msi"
        for Agent in AgentList:
            AgentFileName = AgentVersion.strip() + Agent.strip()
            PSDownloadCommand = 'Invoke-WebRequest -OutFile %s -URI "http://downloads.nessus.org/nessus3dl.php?file=%s&licence_accept=yes&t=%s"' % (AgentFileName, AgentFileName, TenableCookie)
            subprocess.call(["powershell.exe", PSDownloadCommand])

        print("\n\n\n\t\t**Download is complete**")
        print("\nPlease view your agent installer files here: .\Agents\\")
        print("\n\n**Note: Windows version may not actually download any files. Still a work in progress.")

    else:
        ##TODO For Linux
        SaveFolder = r'./Agents'
        if not os.path.exists(SaveFolder):
            os.makedirs(SaveFolder)

        for Agent in AgentList:
            AgentFileName = AgentVersion.strip() + Agent.strip()
            WgetFormat = 'wget --no-check-certificate -O %s/%s "http://downloads.nessus.org/nessus3dl.php?file=%s&licence_accept=yes&t=%s"' % (SaveFolder, AgentFileName, AgentFileName, TenableCookie)
            os.system(WgetFormat)

        print("\n\n\n\t\t**Download is complete**")
        print("\nPlease view your agent installer files here: ./Agents/")

    input("\nPress Return/Enter to Continue...")
    menu()
    return(0)

def SaveAgentsToFile(data, filename):
    TempFile= open(filename, "w")
    TempFile.write(data)
    TempFile.close()


def ReadImportedFile():
    FileName = input("Please Enter the File Name: ")
    try:
        TempImportFile = open(FileName, "r")
    except:
        print("\n\n*************\nError. Filename could not be found.\nReturning to main menu.\n*************")
        menu()
    ImportedData = TempImportFile.readlines()
    TempImportFile.close()
    return (ImportedData)




def menu():
    print("\n\n\nAvailable Options\n")
    print("1\tView Unassigned Agents")
    print("2\tDelete Agents - Last Scanned over 60 days ago")
    print("3\tDelete Agents - Last Checked-In over 60 days ago")
    print("4\tAdd Agents to Group (via hostname)")
    print("5\tGet Count of All Agents")
    print("6\tDownload Agent Installer Files")
    print("\nq\tQuit  (or CTRL+C at any time)\n\n")
    UserResponse = input("Please make your selection: ")

    if UserResponse == "1":
        print(AgentGroupExist())
    elif UserResponse == "2":
        DeleteStaleAgents()
    elif UserResponse == "3":
        DeleteLastCheckedIn()
    elif UserResponse == "4":
        AddAgentsToGroup()
    elif UserResponse == "5":
        GetAllAgentCount()
    elif UserResponse == "6":
        DownloadAgentInstallers()
    elif UserResponse == "q":
        sys.exit(0)

    else:
        menu()

#TODO Create Additional Menus


def main():
    CheckPythonVersion()
    print("\n\n\n\n\t\tWelcome To Tenable - Gold!\n")
    print("\t\tThe Number 1 API Utility for Tenable.io")
    menu()



if __name__ == main():
    main()
