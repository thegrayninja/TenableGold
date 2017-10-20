## a portion of the TenableGold.py program
## specifically meant to update target groups based on a schedule/automated
##
## update logs, etc. as necessary


import requests
import os, time

def GetCurrentTime():
    return(time.strftime('%X %x %Z'))



from auth_file import tenable_header


def AppendDataToFile(data, filename):
    TempFile= open(filename, "a")
    TempFile.write(data)
    TempFile.close()


def UpdateTargetGroups(GroupID, GroupName, GroupMembers):
    url = 'https://cloud.tenable.com/target-groups/%s' % GroupID

    Data = {}
    Data["name"] = GroupName
    Data["members"] = GroupMembers
    Data["type"] = 'system'
    PostStatus = requests.put(url, headers=tenable_header, data=Data)
    StatusCode = str(PostStatus.status_code)
    if (StatusCode == "200"):
        CurrentTime = GetCurrentTime()
        LogData = "\n%s - %s updated successfully on cloud.tenable.com" % (CurrentTime, GroupName)
    else:
        LogData = "\n%s - %s - FAILURE - did not update on cloud.tenable.com" % (CurrentTime, GroupName)
    AppendDataToFile(LogData, "./logs/update_target_groups.log")


def ExportAssetsForTargetGroup():
    # TODO WINSERVER


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

    #print("\nWindows Server:")
    SaveAssetsForTargetGroup(WinServerURL, WinServerFileName, WinServerGroupID, WinServerGroupName)
    #print("\nWindows Client:")
    SaveAssetsForTargetGroup(WinClientURL, WinClientFileName, WinClientGroupID, WinClientGroupName)
    #print("\nLinux:")
    SaveAssetsForTargetGroup(LinuxURL, LinuxFileName, LinuxGroupID, LinuxGroupName)
    #print("\nMacOS:")
    SaveAssetsForTargetGroup(MacOSURL, MacOSFileName, MacOSGroupID, MacOSGroupName)
    #print("\n\nDone!")


def SaveAssetsForTargetGroup(URL, FileName, GroupID, GroupName):
    try:
        AssetInformation = (requests.get(URL, headers=tenable_header)).json()
        CurrentTime = GetCurrentTime()
        LogData = "\n%s - %s Data retrieved from the api call successfully." % (CurrentTime, GroupName)
        AppendDataToFile(LogData, "./logs/update_target_groups.log")
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

            Results += "%s\n" % Hostname
            Counter += 1

        Results = Results.replace("['","")
        Results = Results.replace("']", "")
        Results = Results.replace("[]","")
        Results = Results.replace("'", "")
        Results = Results.replace(", ", "\n")
        Results = Results.replace("\n", ", ")

        UpdateTargetGroups(GroupID, GroupName, Results)
        #print("Assets: {}".format(Counter))
    except:
        CurrentTime = GetCurrentTime()
        LogData = "\n%s - %s Data - FAILURE - an unknown error has occurred." % (CurrentTime, GroupName)
        AppendDataToFile(LogData, "./logs/update_target_groups.log")


def main():
    LogFolder = r'./logs'
    if not os.path.exists(LogFolder):
        os.makedirs(LogFolder)

    ExportAssetsForTargetGroup()



if __name__ == main():
    main()
