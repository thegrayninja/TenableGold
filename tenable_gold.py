#github.com/thegrayninja
#
##identify agents that do not belong to a group
##save them to their own OS file, hostname only.
#
#ver 0.2.0 - removing support for python 2.x and older
#


import requests
import time, sys

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
	return((requests.get(url, headers=tenable_header)).json())



##NOTE For AgentGroupExist
def AgentGroupExist():
	LinuxAgentGroupNull = ""
	MacAgentGroupNull = ""
	UnknownAgentGroupNull = ""
	WindowsAgentGroupNull = ""
	counter = 0
	TotalUnassigned = 0
	AgentInfo = GetAgentsInformation()
	for i in (AgentInfo["agents"]):
		if (AgentInfo["agents"][counter]["groups"] == None):
			AgentName = AgentInfo["agents"][counter]["name"]
			AgentOS = AgentInfo["agents"][counter]["platform"]
			if ("DARWIN" in AgentOS):
				MacAgentGroupNull += "%s\n" % (AgentName)
				TotalUnassigned += 1
			elif ("LINUX" in AgentOS):
				LinuxAgentGroupNull += "%s\n" % (AgentName)
				TotalUnassigned += 1
			elif ("Windows" in AgentOS):
				WindowsAgentGroupNull += "%s\n" % (AgentName)
				TotalUnassigned += 1
			else:
				UnknownAgentGroupNull += "%s\n" % (AgentName)
				TotalUnassigned += 1
		
		counter += 1

	SaveAgentsToFile(LinuxAgentGroupNull, "LinuxAgentGroupNull.txt")
	SaveAgentsToFile(MacAgentGroupNull, "MacAgentGroupNull.txt")
	SaveAgentsToFile(UnknownAgentGroupNull, "UnknownAgentGroupNull.txt")
	SaveAgentsToFile(WindowsAgentGroupNull, "WindowsAgentGroupNull.txt")	
	print("\nData has been saved")
	print("\nA total of %s agents do not belong to a group" % (TotalUnassigned))
	print("\nPlease review the following files for additional information:")
	print("\t./LinuxAgentGroupNull.txt\n\t./MacAgentGroupNull.txt\n\t./WindowsAgentGroupNull.txt")
	print("\t./UnknownAgentGroupNull.txt")
	ToContinue = input("\nPress Return/Enter to Continue...")
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
	print("2\tDelete Stale Agents")
	print("3\tDelete Offline Agents")
	print("4\tAdd Agents to Group (via hostname)")
	print("\nq\tQuit  (or CTRL+C at any time)\n\n")
	UserResponse = input("Please make your selection: ")

	if UserResponse == "1":
		print(AgentGroupExist())
	elif UserResponse == "4":
		AddAgentsToGroup()
	elif UserResponse == "q":
		sys.exit(0)
	
	else:
		menu()

#TODO Create Menu content for 2, 3, and 4


def main():
	CheckPythonVersion()
	print("\n\n\n\n\t\tWelcome To Tenable - Gold!\n")
	print("\t\tThe number 1 API for Tenable.io")
	menu()



if __name__ == main():
	main()
