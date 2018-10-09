## created to help with automation in determining asset information in Tenable
import requests
from auth_file import tenable_header



def main():
    AssetList = GetAssetList()
    AssetVulnDict, VulnCountDict = GetAssetID(AssetList)
    for key, value in AssetVulnDict.items():
        print(key)
        for Finding in value:
            print(Finding)
        #print("{}\n{}".format(key, value))

    print("Total:")
    for key, value in sorted((VulnCountDict.items())):
        if (key != "Info") and (key != "Low"):
            print("{}: {}".format(key, value))

    return 0


def GetAssetList():
    AssetList = ["site01.com", "anothersite.com"]

    return AssetList



def GetAssetID(AssetList):

    AssetDict = {}
    TotalVulnCountDict = {"Info":0, "Low":0, "Medium":0, "High":0, "Critical":0}
    for Host in AssetList:
        print(Host)
        URL = 'https://cloud.tenable.com/workbenches/assets?filter.0.filter=hostname&filter.0.quality=match&filter.0.value={}'.format(Host)
        Results = (requests.get(URL, headers=tenable_header)).json()
        AssetID = Results['assets'][0]['id']
        print(AssetID)
        AssetVulns, VulnCountDict = GetAssetVulns(AssetID)
        AssetDict[Host] = AssetVulns
        for key, value in VulnCountDict.items():
            TotalVulnCountDict[key] += value

    return AssetDict, TotalVulnCountDict


def GetAssetVulns(AssetID):
    URL = 'https://cloud.tenable.com/workbenches/assets/{}/vulnerabilities'.format(AssetID)
    Results = (requests.get(URL, headers=tenable_header)).json()
    #print(Results)
    SeverityDict = {0:"Info", 1:"Low", 2:"Medium", 3:"High", 4:"Critical"}
    VulnCountDict = {"Info":0, "Low":0, "Medium":0, "High":0, "Critical":0}
    AssetVulns = ""
    AssetVulnsList = []
    Counter = 0
    for Vuln in Results['vulnerabilities']:
        VulnSeverity = Results['vulnerabilities'][Counter]['severity']
        PluginName = Results['vulnerabilities'][Counter]['plugin_name']
        Counter += 1
        if VulnSeverity > 1:
            VulnSeverity = SeverityDict[VulnSeverity]
            VulnCountDict[VulnSeverity] += 1
            #AssetVulns += "\t{} - {}\n".format(VulnSeverity, PluginName)
            AssetVulnsList.append("\t{} - {}".format(VulnSeverity, PluginName))
    AssetVulnsList = sorted(AssetVulnsList)
    AssetVulnsList.append("\nVulnerability Count:\n\tCritical: {}\n\tHigh: {}\n\tMedium: {}\n\n".format(VulnCountDict["Critical"], VulnCountDict["High"], VulnCountDict["Medium"]))
    #for Entry in AssetVulnsList:
    #    print(Entry)
    return AssetVulnsList, VulnCountDict



if __name__ == "__main__":
    main()
