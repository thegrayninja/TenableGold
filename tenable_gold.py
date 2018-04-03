#github.com/thegrayninja
#
#
#Current Version: 1.0.0
#Version Notes: Added extra info to "view agent info"
#
#Version History
#ver 1.0.0 - current version



import requests
import time, sys, os
import subprocess, platform

from auth_file import tenable_header



def main():
    CheckPythonVersion()
    print("\n\n\n\n\t\tWelcome To Tenable - Gold!\n")
    print("\t\tThe Number 1 API Utility for Tenable.io")
    menu()


def CheckPythonVersion():
    PyVerTuple = sys.version_info[:1]
    if PyVerTuple[0] > 2:
        return 0
    else:
        print("\n\nPlease run Python 3.x or newer\n")
        sys.exit(1)


def menu():
    #to reset the value
    print("\n\n\nAvailable Options\n")
    print("1\tAdd Agent(s) to a Group")
    print("2\tView Stale Agents")
    print("3\tDelete Stale Agents")
    print("4\tCheck if Agents are Installed against a list of hosts")
    print("5\tGenerate Vuln Report")

    print("\nq\tQuit  (or CTRL+C at any time)\n\n")
    UserResponse = input("Please make your selection: ")

    if UserResponse == "1":
        AddAgentsToGroup()
    elif UserResponse == "2":
        ViewStaleAgents()
    elif UserResponse == "3":
        DeleteStaleAgents()
    elif UserResponse == "4":
        CheckIfAgentInstalled()
    elif UserResponse == "5":
        GenerateVulnReport()

    elif UserResponse == "q":
        sys.exit(0)

    else:
        menu()



#### ADMIN INFO GATHERING - START ####

def GetOSVersion():
    return(platform.system())

def GetGroupInformation():
    return((requests.get('https://cloud.tenable.com/scanners/1/agent-groups', headers=tenable_header)).json())


def GetAgentsInformation():
    url = 'https://cloud.tenable.com/scanners/1/agents/?limit=5000'
    return(requests.get(url, headers=tenable_header).json())


def GetAssetsInformation():
    url = 'https://cloud.tenable.com/workbenches/assets'
    return(requests.get(url,headers=tenable_header)).json()


def SaveAgentsToFile(data, filename):
    TempFile= open(filename, "w")
    TempFile.write(data)
    TempFile.close()


def ReadImportedFile():
    print("\n\nEnter q to return to the main menu.")
    FileName = input("Please Enter the File Name: ")

    try:
        TempImportFile = open(FileName, "r")
    except:
        print("\n\n*************\nError. Filename could not be found.\nReturning to main menu.\n*************")
        menu()
    ImportedData = TempImportFile.readlines()
    TempImportFile.close()
    return (ImportedData)


def ConvertSeverityToEnglish(SeverityNumber):
    if SeverityNumber == 4:
        return "Critical"
    elif SeverityNumber == 3:
        return "High"
    elif SeverityNumber == 2:
        return "Medium"
    elif SeverityNumber == 1:
        return "Low"
    else:
        return "Unknown"


#### ADMIN INFO GATHERING - END ####




def CheckIfAgentInstalled():
    Results = ""
    URL = "https://cloud.tenable.com/scanners/1/agents?f=name:match:"

    HostNames = ReadImportedFile()
    print(HostNames)
    for Asset in HostNames:
        Asset = Asset.strip()
        FullPath = URL + Asset
        try:
            Data = (requests.get(FullPath, headers=tenable_header)).json()
            print(Data['agents'][0]['name'])
        except:
            print("Asset is missing agent: %s" % Asset)

        #print(i.strip())
    #print(Results)
    input("\nPress Return/Enter to Continue...")
    menu()



#### ADDING AGENTS TO GROUP - START ####

def AddAgentsToGroup():
    added_count = 0
    AgentHostnames = ReadImportedFile()
    ShowGroups()
    UserGroupSelection = input("Please Enter Group ID: ")

    AgentInfo = GetAgentsInformation()
    #print(AgentInfo)
    Counter = 0
    Results = ""
    AgentsScanned = ""
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        added_count += SaveAgentsToGroup(AgentIP, AgentID, AgentName, UserGroupSelection, AgentHostnames)
        #print(AgentName)
        Counter += 1
    print(added_count)
    input("\nPress Return/Enter to Continue...")
    menu()



def ShowGroups():
    GroupInfo = GetGroupInformation()
    counter = 0
    for i in (GroupInfo["groups"]):
        GroupName = GroupInfo["groups"][counter]["name"]
        GroupID = GroupInfo["groups"][counter]["id"]
        print("ID: %s\tName: %s" %(GroupID, GroupName))
        counter += 1



def SaveAgentsToGroup(agentip, agentid, agentname, UserGroupSelection, AgentHostnames):
    added_count = 0
    for ss in AgentHostnames:
        search_string = ss.strip()
        url = 'https://cloud.tenable.com/scanners/1/agent-groups/%s/agents/%s' % (UserGroupSelection, agentid)
        #print(url)
        #print(search_string)
        if search_string.lower() in agentname.lower():
            url = 'https://cloud.tenable.com/scanners/1/agent-groups/%s/agents/%s' % (UserGroupSelection, agentid)
            #temp_container = requests.put(url, headers=tenable_header)
            requests.put(url, headers=tenable_header)
            newentry = ("%s - %s was added to the group %s" % (agentip, agentname, UserGroupSelection))
            newFile = open("tenable_added_to_group.log", "a")
            newFile.write("%s\n" % (newentry))
            newFile.close()
            print(newentry)
            time.sleep(.3)
            #print("%s-%s\n" % (search_string, agentid))
            added_count += 1
    return(added_count)


#### ADDING AGENTS TO GROUP - END ####


def ViewStaleAgents():
    #agents that are part of a group which have not scanned within 120 days
    ListDeletedAgents = ""
    DeletedCount = 0
    TimeDiff = 15745300 #roughly 120 days
    Counter = 0
    AgentInfo = GetAgentsInformation()
    StaleAgents = 0
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        try:
            LastScanned = (AgentInfo["agents"][Counter]["last_scanned"])
        except:
            LastScanned = 9000000000
        try:
            if (LastScanned + TimeDiff) < time.time():
                Age = 1
                StaleAgents += 1
            else:
                Age = 0
        except:
            Age = 0
        if Age == 1:
            LastScannedTime = time.strftime('%Y-%m-%d,%H:%M:%S', time.localtime(LastScanned))
            print("%s,%s,%s,%s" % (AgentIP, AgentName, AgentID, LastScannedTime))
        Counter += 1
    print("\nStale Agents: %d\n" % StaleAgents)




def DeleteStaleAgents():
    #agents that are part of a group which have not scanned within 120 days
    ListDeletedAgentsHeader = "AgentIP,AgentName,AgentID,DateLastScanned,TimeLastScanned"
    ListDeletedAgents = ""
    #DeletedCount = 0
    TimeDiff = 15745300 #roughly 120 days
    Counter = 0
    AgentInfo = GetAgentsInformation()
    StaleAgents = 0
    DeleteAgentIDs = []
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        try:
            LastScanned = (AgentInfo["agents"][Counter]["last_scanned"])
        except:
            LastScanned = 9000000000
        try:
            if (LastScanned + TimeDiff) < time.time():
                Age = 1
                StaleAgents += 1
            else:
                Age = 0
        except:
            Age = 0
        if Age == 1:
            LastScannedTime = time.strftime('%Y-%m-%d,%H:%M:%S', time.localtime(LastScanned))
            ListDeletedAgents += "%s,%s,%s,%s\n" % (AgentIP, AgentName, AgentID, LastScannedTime)
            DeleteAgentIDs.append(AgentID)
        Counter += 1

    print(ListDeletedAgentsHeader + "\n" + ListDeletedAgents)
    print("\nStale Agents: %d\n" % StaleAgents)
    UserValue = 0
    while UserValue == 0:
        UserInput = input("Would you like to delete these stale agents? [y/n]: ")
        try:
            if UserInput[0].lower() == "y":
                UserValue = 1
                DeleteAgents(DeleteAgentIDs)
                print('deleted')
            elif UserInput[0].lower() == "n":
                UserValue = 1
                print('not deleted')
            else:
                print('ehh, try again')
        except:
            UserValue = 0
            print("next time don't leave it blank")

    DeletedAgentsFile = open("DeletedStaleAssets.log", "a")
    DeletedAgentsFile.write("%s\n" % ListDeletedAgents)
    DeletedAgentsFile.close()


def DeleteAgents(AgentIDs):
    DeletedCount = 0
    try:
        for i in AgentIDs:
            print(i)
            DeletedCount += 1
    except:
        print("error deleting agents")
    print("Deleted Agents: %s" % DeletedCount)








def GenerateVulnReport():
    #TODO Make Request Based on filters to gather asset ids

    FinalReport = "FQDN,IPv4,Severity,PluginName,PluginID,PluginFamily,NetBIOS,OS,LastScanned\n"
    WinServerGroupID = "29136"
    WinClientGroupID = "29215"
    LinuxGroupID = "29139"
    MacOSGroupID = "29222"
    CDEBHNGroupID = "29838"

    URL = "https://cloud.tenable.com/workbenches/assets/vulnerabilities?filter.0.quality=match&filter.0.filter=target_group&filter.0.value=29838&filter.1.quality=match&filter.1.filter=severity&filter.1.value=critical"
    RequestData = (requests.get(URL, headers=tenable_header)).json()
    Counter = 0
    for i in RequestData["assets"]:
        AssetID = RequestData["assets"][Counter]["id"]
        InfoURL = "https://cloud.tenable.com/workbenches/assets/%s/info" % AssetID
        InfoData = (requests.get(InfoURL, headers=tenable_header)).json()

        AssetFQDN = InfoData["info"]["fqdn"]
        AssetIPv4 = InfoData["info"]["ipv4"]
        AssetLastScanned = InfoData["info"]["last_licensed_scan_date"]
        AssetNetBIOS = InfoData["info"]["netbios_name"]
        AssetOS = InfoData["info"]["operating_system"]

        VulnURL = "https://cloud.tenable.com/workbenches/assets/%s/vulnerabilities" % AssetID
        VulnData = (requests.get(VulnURL, headers=tenable_header)).json()

        VulnCounter = 0
        for i in VulnData["vulnerabilities"]:
            PluginFamily = VulnData["vulnerabilities"][VulnCounter]["plugin_family"]
            PluginID = VulnData["vulnerabilities"][VulnCounter]["plugin_id"]
            PluginName = VulnData["vulnerabilities"][VulnCounter]["plugin_name"]
            VSeverity = VulnData["vulnerabilities"][VulnCounter]["severity"]
            if VSeverity == 0:
                VulnSeverity =  "Info"
            elif VSeverity == 1:
                VulnSeverity =  "Low"
            elif VSeverity == 2:
                VulnSeverity =  "Medium"
            elif VSeverity == 3:
                VulnSeverity = "High"
            elif VulnSeverity == 4:
                VulnSeverity = "Critical"
            else:
                VulnSeverity = "Unknown"

            VulnCounter += 1
            Vulnerabilities = "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(AssetFQDN, AssetIPv4, VulnSeverity, PluginName, PluginID, PluginFamily, AssetNetBIOS, AssetOS, AssetLastScanned)
            print(Vulnerabilities)
            FinalReport += Vulnerabilities



        Counter += 1
    SaveAgentsToFile(FinalReport, ".\Docs\\report_test.csv")

    #TODO Pull asset info based on asset id
    #TODO Save data to variables
    #TODO Pull vuln data based off asset id
    #TODO Save data to variable and merge with asset info
    #TODO Save as temp or append to csv
    #TODO Setup previous rules in a for-loop to attack all assets
    #TODO Save file to csv









#### ^^^^^ USEFUL ####

#### .... (down arrow) .... NEEDS TESTING ####







def ViewStaleAgents_temp():
    #agents that are part of a group which have not scanned within 120 days
    ListDeletedAgents = ""
    DeletedCount = 0
    TimeDiff = 15745300 #roughly 120 days
    Counter = 0
    AgentInfo = GetAgentsInformation()
    for i in (AgentInfo["agents"]):
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentID = AgentInfo["agents"][Counter]["id"]
        try:
            LastScanned = (AgentInfo["agents"][Counter]["last_scanned"])
        except:
            continue

        if (AgentInfo["agents"][Counter]["groups"] == None):
            continue
        elif (LastScanned == None):
            continue
        elif (LastScanned + TimeDiff) < time.time():
            CurrentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            LastScannedTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(LastScanned))
            URL = 'https://cloud.tenable.com/scanners/1/agents/%s' % (AgentID)
            #ViewAgent = requests.get(URL, headers=tenable_header)
            #TestDeleteAgent = requests.get(URL, headers=tenable_header)
            ListStaleAgents = ("%s (%s) is stale (time: %s). Last Scanned at %s" %(AgentName, AgentIP, CurrentTime, LastScannedTime))
            #DeletedAgentsFile = open("DeletedStaleAssets.log", "a")
            #DeletedAgentsFile.write("%s\n" % (ListDeletedAgents))
            #DeletedAgentsFile.close()
            print(ListStaleAgents)
            time.sleep(.3)
            DeletedCount += 1
        Counter +=1
    print("\n%d Agents have been deleted" % (DeletedCount))
    print("You can review the deleted assets in DeletedStaleAssets.log")
    input("\nPress Return/Enter to Continue...")
    menu()











def ListAgentGroups():
    LinuxAgentGroupNull = ""
    MacAgentGroupNull = ""
    UnknownAgentGroupNull = ""
    WindowsAgentGroupNull = ""
    counter = 0
    TotalUnassigned = 0
    AgentInfo = GetAgentsInformation()
    print("\n\nThe following assets do not belong to a group:\n")
    for i in (AgentInfo["agents"]):

        AssetGroups = (AgentInfo["agents"][counter]).get("groups", 0)
        #xx = x.get("groups", 0)
        #try:
        #    AllGroups = ""
        #    for i in xx:
        #        AllGroups += "%s," % (i.get("name"))
        #    print(AllGroups)
        #except:
        #    print("not in a group")

        if AssetGroups == 0:
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

def ReturnAssetsWithoutAgents():
    AssetList = GetAssetsInformation()
    Counter = 0
    TotalAssetsWithoutAgents = 0
    MissingAgents = "FQDN,HOSTNAME,IPV4,OS\n"
    for Asset in (AssetList["assets"]):
        if AssetList["assets"][Counter]["has_agent"] == False:
            AssetFQDN = ''.join(AssetList["assets"][Counter]["fqdn"])
            AssetFQDN = AssetFQDN.replace('[','')
            AssetFQDN = AssetFQDN.replace(']', '')
            AssetName = ''.join(AssetList["assets"][Counter]["netbios_name"])
            AssetName = AssetName.replace('[','')
            AssetName = AssetName.replace(']', '')
            AssetIP = ''.join(AssetList["assets"][Counter]["ipv4"])
            AssetIP = AssetIP.replace('[','')
            AssetIP = AssetIP.replace(']', '')
            AssetOS = ''.join(AssetList["assets"][Counter]["operating_system"])
            AssetOS = AssetOS.replace('[','')
            AssetOS = AssetOS.replace(']', '')
            MissingAgents += "%s,%s,%s,%s\n" % (AssetFQDN, AssetName, AssetIP, AssetOS)
            TotalAssetsWithoutAgents += 1
        Counter += 1
    print(TotalAssetsWithoutAgents)

    OSVersion = GetOSVersion()

    if "Windows" in OSVersion:
        SaveFolder = r'.\Docs'
        if not os.path.exists(SaveFolder):
            os.makedirs(SaveFolder)
        FilePath = "%s\AssetsWithoutAgents.csv" % SaveFolder

    elif "Linux" in OSVersion:
        SaveFolder = r'./Docs'
        if not os.path.exists(SaveFolder):
            os.makedirs(SaveFolder)
        FilePath = "%s/AssetsWithoutAgents.csv" % SaveFolder

    else:
        FilePath = "AssetsWithoutAgents.csv"

    SaveAgentsToFile(MissingAgents, FilePath)
    print("\n%s has been saved to your current directory." % FilePath)
    input("\nPress Return/Enter to Continue...")
    menu()

    return 0


def ListNeverCheckedIn():
    Counter = 0
    TotalNeverCheckedIn = 0
    ListNever = ""
    AgentInfo = GetAgentsInformation()
    for i in (AgentInfo["agents"]):
        AgentName = AgentInfo["agents"][Counter]["name"]
        AgentIP = AgentInfo["agents"][Counter]["ip"]
        AgentOS = AgentInfo["agents"][Counter]["platform"]
        LastChecked = AgentInfo["agents"][Counter]["last_connect"]
        if LastChecked == None:
            print("%s,%s,%s" % (AgentName, AgentIP, AgentOS))
            ListNever += "%s,%s,%s\n" % (AgentName, AgentIP, AgentOS)
            TotalNeverCheckedIn += 1
        Counter += 1
    print("\n\nTotal Agents that have not checked in: %d" % TotalNeverCheckedIn)
    ListAgentsFile = open(".\\Docs\\NeverCheckedInAssets.log", "w")
    ListAgentsFile.write(ListNever)
    ListAgentsFile.close()
    print("\nThe list has been saved to .\\Docs\\NeverCheckedInAssets.log")


    input("\nPress Return/Enter to Continue...")
    menu()
    return(0)


#### UPDATING TARGET GROUPS - START ####

def ExportAssetsForTargetGroup():
    # TODO WINSERVER
    #WinServerURL = 'https://cloud.tenable.com/workbenches/assets?filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Windows%20Server'
    WinServerURL = 'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Windows%20Server&filter.search_type=and'
    WinServerFileName = '.\Docs\WindowsServer_Assets.txt'
    WinServerGroupID = '29136'
    WinServerGroupName = '_WindowsServer'
    WinClientURL = 'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Windows%207&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Windows%2010&filter.search_type=or'
    WinClientFileName = '.\Docs\WindowsClient_Assets.txt'
    WinClientGroupID = '29215'
    WinClientGroupName = '_WindowsClients'
    LinuxURL = 'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Linux'
    LinuxFileName = '.\Docs\Linux_Assets.txt'
    LinuxGroupID = '29139'
    LinuxGroupName = '_Linux'
    MacOSURL = 'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Mac%20OS'
    MacOSFileName = '.\Docs\MacOS_Assets.txt'
    MacOSGroupID = '29222'
    MacOSGroupName = '_MacOS'
    print("\nWindows Server:")
    SaveAssetsForTargetGroup(WinServerURL, WinServerFileName, WinServerGroupID, WinServerGroupName)
    print("\nWindows Client:")
    SaveAssetsForTargetGroup(WinClientURL, WinClientFileName, WinClientGroupID, WinClientGroupName)
    print("\nLinux:")
    SaveAssetsForTargetGroup(LinuxURL, LinuxFileName, LinuxGroupID, LinuxGroupName)
    print("\nMacOS:")
    SaveAssetsForTargetGroup(MacOSURL, MacOSFileName, MacOSGroupID, MacOSGroupName)
    print("\n\nDone!")



def SaveAssetsForTargetGroup(URL, FileName, GroupID, GroupName):
    AssetInformation = (requests.get(URL, headers=tenable_header)).json()
    Counter = 0
    Results = ""
    for Asset in AssetInformation["assets"]:
        if (AssetInformation["assets"][Counter]["ipv4"] == []):
            if (AssetInformation["assets"][Counter]["fqdn"] == []):
                Hostname = AssetInformation["assets"][Counter]["netbios_name"]
            else:
                Hostname = AssetInformation["assets"][Counter]["fqdn"]
        else:
            Hostname = AssetInformation["assets"][Counter]["ipv4"]
        #Hostname = AssetInformation["assets"][Counter]["fqdn"]
        Results += "%s\n" % Hostname
        Counter += 1

    Results = Results.replace("['","")
    Results = Results.replace("']", "")
    Results = Results.replace("[u", "")
    Results = Results.replace("[]","")
    Results = Results.replace("'", "")
    Results = Results.replace(", ", "\n")
    Results = Results.replace("\n", ", ")
    SaveAgentsToFile(Results,FileName)
    UpdateTargetGroups(GroupID, GroupName, Results)
    print("Assets: {}".format(Counter))


def UpdateTargetGroups(GroupID, GroupName, GroupMembers):
    url = 'https://cloud.tenable.com/target-groups/%s' % GroupID
    #data = {"name":"_thouse_test","members":"redbull, pickles, garbage","type":"system"}

    Data = {}
    Data["name"] = GroupName
    Data["members"] = GroupMembers
    Data["type"] = 'system'
    PostStatus = requests.put(url, headers=tenable_header, data=Data)
    print("Response Code: {}".format(PostStatus.status_code))
    #print(Data)


def AddToTargetGroups(GroupID, GroupName, GroupMembers):

    UpdateTargetGroups(GroupID, GroupName, GroupMembers)
    print("\nDone!")
    return 0

##### END OF UPDATING TARGET GROUPS #####




def CreateAgentGroup():
    GroupName = input("\n\nPlease enter the Group Name: ")
    Data = {}
    Data["name"] = GroupName

    url = 'https://cloud.tenable.com/scanners/1/agent-groups/'
    # temp_container = requests.put(url, headers=tenable_header)
    Results = requests.post(url, headers=tenable_header, data=Data)
    print(Results.content)

    input("\nPress Return/Enter to Continue...")
    menu()
    return 0





def AppendGlobalScanGroups():
    Counter = 0
    TotalUnassigned = 0
    AgentInfo = GetAgentsInformation()

    GroupURL = 'https://cloud.tenable.com/scanners/1/agent-groups/11/?limit=5000'
    BHNGlobalAgentsJson = requests.get(GroupURL, headers=tenable_header).json()
    BHNGlobalAgents = BHNGlobalAgentsJson["agents"]
    BHNAgents = []
    AgentCounter = 0
    for i in BHNGlobalAgents:
        BHNAgents.append(BHNGlobalAgents[AgentCounter]["id"])
        AgentCounter +=1


    TotalAgents = 0
    for i in (AgentInfo["agents"]):
        TotalAgents +=1

    for i in (AgentInfo["agents"]):
        AgentAll = AgentInfo["agents"][Counter]
        AgentID = AgentAll.get("id", 0)
        if AgentID not in BHNAgents:
            URL = 'https://cloud.tenable.com/scanners/1/agent-groups/11/agents/%s/' % (AgentID)
            requests.put(URL, headers=tenable_header)
        else:
            print("%s is already in BHN Global" %(AgentID))

        if (Counter + 1) == TotalAgents:
            print("100%")
        elif (Counter+1)%15 == 0:
            Percentage = ((Counter+1)/TotalAgents)*100
            print("%s%s" %(Percentage, '%'))


        Counter += 1
    print("BHN Global scan group now contains (roughly) %d agents." %(Counter+1))


    input("\nPress Return/Enter to Continue...")
    menu()
    return(0)




def GetAgentHostnameViaIP():
    AgentInfo = GetAgentsInformation()
    ImportIPFile = input("Please Enter the filename that contains your ip addresses (column listed): ")
    TempIPFile = open(ImportIPFile, "r")
    ImportIPList = TempIPFile.readlines()
    TempIPFile.close()
    Counter = 0
    for Asset in AgentInfo["agents"]:
        for IP in ImportIPList:
            IPStripped = IP.strip()
            if IPStripped in AgentInfo["agents"][Counter]["ip"]:
                AgentName = (AgentInfo["agents"][Counter]["name"])
                AgentIP = (AgentInfo["agents"][Counter]["ip"])
                #AgentID = (AgentInfo["agents"][Counter]["id"])
                print ("%s, %s" % (AgentName, AgentIP))
        Counter += 1

    input("\nPress Return/Enter to Continue...")
    menu()
    return 0







if __name__ == main():
    main()
