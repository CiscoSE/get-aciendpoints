#!/usr/bin/python2.7
__license__ ='''Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.'''

#Python provided modules
import sys
import os
import getpass
import argparse
import re

#Add custom modules bin directory to path
sys.path.append(os.getcwd()+'/bin')
print(sys.path)

#Custom modules
from common       import urlFunctions
from common       import timeFunctions
from common       import inputSupport
from aciFunctions import endPointFunctions
from common       import validation


time  = timeFunctions()
YesNo = inputSupport()


defaultServer = '10.82.6.65'
defaultUser   = 'admin'

#Clear the screen
os.system('clear')

#Argument Help
helpmsg = '''
This tool connects to ACI and pulls end point information. 
If no end point information is provided, all end points are return.
'''

argsParse = argparse.ArgumentParser(description=helpmsg)
argsParse.add_argument('-i',         action='append',     dest='ips',        default=[],            help='Provide a list of IPv4 addresses to search for (one or many)')
argsParse.add_argument('-m',         action='append',     dest='mac',        default=[],            help='Provide a list of MAC Addresses to search for (one or many)')
argsParse.add_argument('--csv',      action='store_true', dest='writeCsv',   default=False,         help='Switch to enable exporting to file. File will be written to working directory.')
argsParse.add_argument('--aci-user', action='store',      dest='adminUser',  default=defaultUser,   help='Provide the user name for ACI access. Default is admin')
argsParse.add_argument('-s',         action='store',      dest='serverName', default=defaultServer, help='Provide APIC DNS name or IP address')
argsParse.add_argument('--aci-pass', action='store',      dest='password',   default='',            help='Enter Password for APIC access. If none provided, you will be prompted')
argsParse.add_argument('-d',         action='store',      dest='directory',  default='./',          help='Directory to write csv report to')
argsParse.add_argument('-debug',	 action='store_true', dest='debug',		 default=False, 	    help='Advanced Output')
args = argsParse.parse_args()

URL   = urlFunctions(debug = args.debug)

#Argument Validation for IP and MAC
processIP,  ipList  = validation().validateIP(args.ips)
processMAC, macList = validation().validateMAC(args.mac)


if args.writeCsv == True:
	#Default settings for output file name.
	if f'{args.directory}'[-1] == '/':
		directory = f"{args.directory}"
	else:
		directory = f"{args.directory}/"
	if args.debug == True:
		print(f"Directory:\t{directory}")
	fileSuffix = '-EndPoint-Report.csv'
	fileName   = '{0}{1}{2}'.format(directory, time.getCurrentTime(), fileSuffix)
	if args.debug == True:
		print(f"File Name\t{fileName}")

	#Test Directory
	if os.path.isdir(f'{directory}') == False:
		os.makedirs(f'{directory}')
	epgF = endPointFunctions(filePath=fileName, writeCsv=True, debug=args.debug)
else:
	epgF = endPointFunctions(filePath='', writeCsv=False, debug=args.debug)

# URL path to REST interface.
baseurl  	   = 'https://{0}'.format(args.serverName)

#This is just to give you something on the screen so you can verify who you are going to.
print('''
Getting end point data:
Server:		{0}
User:   	{1}
baseurl:	{2}
IP List:	{3}
Enter the password for the APIC user.
'''.format(
	args.serverName,
	args.adminUser,
	baseurl,
	processIP
))

if args.password == '':
    args.password = getpass.getpass()

#Get a cookie and print it out so the operator knows we have it.
authCookie = URL.getCookie(args)
if args.debug == True:
	print ('Authorization Cookie Obtained: {0}\n'.format(authCookie))
headers = {"Content-Type": "application/json"}

#If no mac address or IP provided, we dump all end points.
if (processIP == False and processMAC == False):
	#Get a list of endpoints (This could be a lot of data)
	dn = "/api/node/class/fvCEp.json?rsp-subtree=full"
	endpoint_json = URL.getData(url=baseurl + dn, headers=headers,requestType='get',cookie={'APIC-Cookie': f"{authCookie}"})
	epgF.epJSONtoField(endpoint_json,baseurl, authCookie)

if (processIP == True):
	#process IP list
	for ip in ipList:
		epgF.searchOneIpEp(ip, baseurl, authCookie)

if (processMAC == True):
    #process MAC list
    for mac in macList:
        epgF.searchOneMacEp(mac, baseurl, authCookie)