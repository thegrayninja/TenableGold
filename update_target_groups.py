## a portion of the TenableGold.py program
## specifically meant to update target groups based on a schedule/automated
## added the ability to enter multiple urls per one target group
## update logs, etc. as necessary




import requests
import os, time
from auth_file import tenable_header



def main():
    print("and then?")

    LogFolder = r'./logs'
    if not os.path.exists(LogFolder):
        os.makedirs(LogFolder)

    ExportAssetsForTargetGroup()
    print("no 'and then'!")





def GetCurrentTime():
    return(time.strftime('%X %x %Z'))


def AppendDataToFile(data, filename):
    TempFile= open(filename, "a")
    TempFile.write(data)
    TempFile.close()





# TODO Capture URLs, Target Group Info
def ExportAssetsForTargetGroup():

    WinServerURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Windows%20Server']
    WinServerGroupID = '29136'
    WinServerGroupName = '_WindowsServer'

    WinClientURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Windows%207&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Windows%2010&filter.search_type=or']
    WinClientGroupID = '29215'
    WinClientGroupName = '_WindowsClients'

    LinuxURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Linux']
    LinuxGroupID = '29139'
    LinuxGroupName = '_Linux'

    MacOSURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Mac%20OS']
    MacOSGroupID = '29222'
    MacOSGroupName = '_MacOS'


    NetworkURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Cisco%20IOS&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Cisco%20IOS&filter.search_type=or',
        'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Cisco%20IOS&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Cisco%20IOS&filter.search_type=or',
        'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Cisco%20IOS&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Cisco%20IOS&filter.search_type=or',
        'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=Cisco%20IOS&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=Cisco%20IOS&filter.search_type=or']
    NetworkGroupID = '29338'
    NetworkGroupName = '_Network'

    StorageURL = ['https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=iDRAC&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=iDRAC&filter.search_type=or',
                  'https://cloud.tenable.com/workbenches/assets?date_range=30&filter.0.quality=match&filter.0.filter=operating_system&filter.0.value=iDRAC&filter.1.quality=match&filter.1.filter=operating_system&filter.1.value=iDRAC&filter.search_type=or']
    StorageGroupID = '29358'
    StorageGroupName = '_Storage'

    #print(WinServerURL[0])
    SaveAssetsForTargetGroup(WinServerURL, WinServerGroupID, WinServerGroupName)
    SaveAssetsForTargetGroup(WinClientURL, WinClientGroupID, WinClientGroupName)
    SaveAssetsForTargetGroup(LinuxURL, LinuxGroupID, LinuxGroupName)
    SaveAssetsForTargetGroup( MacOSURL, MacOSGroupID,  MacOSGroupName)
    SaveAssetsForTargetGroup(NetworkURL, NetworkGroupID, NetworkGroupName)
    SaveAssetsForTargetGroup(StorageURL, StorageGroupID, StorageGroupName)


# TODO Format URLs Response Data
# TODO Append URLs Response Data to Variable
def SaveAssetsForTargetGroup(URL, GroupID, GroupName):

    Results = ""
    URLCount = 1
    while URLCount <= len(URL):
        try:
            AssetInformation = (requests.get(URL[URLCount-1], headers=tenable_header)).json()
            CurrentTime = GetCurrentTime()
            LogData = "\n%s - %s Data retrieved from the api call successfully." % (CurrentTime, GroupName)
            AppendDataToFile(LogData, "./logs/update_target_groups.log")
            Counter = 0
            for Asset in AssetInformation["assets"]:
                if (AssetInformation["assets"][Counter]["ipv4"] == []):
                    if (AssetInformation["assets"][Counter]["fqdn"] == []):
                        Hostname = AssetInformation["assets"][Counter]["netbios_name"]
                    else:
                        Hostname = AssetInformation["assets"][Counter]["fqdn"]
                else:
                    Hostname = AssetInformation["assets"][Counter]["ipv4"]
                Results += "%s\n" % Hostname
                Counter +=1
            Results = Results.replace("['", "")
            Results = Results.replace("']", "")
            Results = Results.replace("[u", "")
            Results = Results.replace("[]", "")
            Results = Results.replace("'", "")
            Results = Results.replace(", ", "\n")
            Results = Results.replace("\n", ", ")

            URLCount += 1
        except:
            CurrentTime = GetCurrentTime()
            LogData = "\n%s - %s Data - FAILURE - an unknown error has occurred." % (CurrentTime, GroupName)
            AppendDataToFile(LogData, "./logs/update_target_groups.log")
            print("error")
            URLCount += 1

    #print(Results)
    UpdateTargetGroups(GroupID, GroupName, Results)






# TODO Upload Variable to Target Group
def UpdateTargetGroups(GroupID, GroupName, GroupMembers):
    url = 'https://cloud.tenable.com/target-groups/%s' % GroupID

    Data = {}
    Data["name"] = GroupName
    Data["members"] = GroupMembers
    Data["type"] = 'system'
    PostStatus = requests.put(url, headers=tenable_header, data=Data)
    StatusCode = str(PostStatus.status_code)
    CurrentTime = GetCurrentTime()
    if (StatusCode == "200"):
        LogData = "\n%s - %s updated successfully on cloud.tenable.com" % (CurrentTime, GroupName)
    else:
        LogData = "\n%s - %s - FAILURE - did not update on cloud.tenable.com" % (CurrentTime, GroupName)
    AppendDataToFile(LogData, "./logs/update_target_groups.log")







if __name__ == main():
    main()
