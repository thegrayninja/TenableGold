# TenableGold
The #1 Utility for Tenable.io API                    (At least in my own universe) 


To run this tool, you will need to install Python 3.x. You will also need to install the ‘requests’ library.

Python 3.6.4: https://www.python.org/ftp/python/3.6.4/python-3.6.4.exe

Install python. (for example purposes, install to: “C:\Python”

Add python to your $PATH. 
    via powershell:  $env:Path += ";C:\Python")
    via linux, if necessary: export PATH=$PATH:/path/to/dir

Open Powershell as admin
cd C:\Python\Scripts
  .\easy_install.exe requests   
 
  #Note, the file may be easy_install-3.6.exe. Just run ls/dir/gci to confirm. 
  #The easy_install is the windows equivalent of PIP on linux. This will install the requests library


or via Linux:
  python3 pip install requests



Tenable Gold: https://github.com/thegrayninja/TenableGold
 Grab the “tenable_gold.py” and “auth_file_fake.py” files. Save them to a working directory. 
Rename auth_file_fake.py to auth_file.py. Also, update the API keys in the auth_file.py. 

You can get your API keys by logging into cloud.tenable.com, clicking the “person in hat” icon in the upper-right corner of the window, and clicking “My Account”. Click the “API Keys” tab, then click the “Generate” button to view your API keys. 
