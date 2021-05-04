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

import requests
import ssl
import time
import os
import json
import socket
import re

#Required for self signed certificate handling.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class inputSupport:
    def __init__(self):
        return

    def answerYesNo(self, message):
        questionExit = True
        while questionExit == True:
            os.system('clear')
            print (message + "[Yes / No]")
            newServerName = raw_input().lower()
            if newServerName in {'yes','y','ye'}:
                return True
            elif newServerName in {'no','n'}:
                return False

class timeFunctions:
    def __init__(self):
        return

    def getCurrentTime(self):
        return time.strftime("%Y%m%d%H%M%S")

class urlFunctions:
    def __init__(self, debug=False):
        self.debug = debug
        return

    def getData(self, url, data='', headers={"Content-Type": "Application/json"},requestType='post', cookie='' ):
        if self.debug == True:
            print(f"URL:\t\t{url}")
            print(f"Data:\t{data}")
            print(f"Headers:\t{headers}")
            print(f"Cookie:\t{cookie}")
            print(f"request Type:\t{requestType}")
        if requestType == 'post':
            request = requests.post(url, data=data, headers=headers, cookies=cookie, verify=False)
        elif requestType == 'get':
            request = requests.get(url, headers=headers, verify=False, cookies=cookie)
        if re.match("20[0-9]", f"{request.status_code}"):
            if self.debug == True:
                print("Request was successful")
            return request.text
        else:
            print('Failed to access APIC API')
            print(f'Reason: {request.reason}')
            print(request.text)
            exit()

    def getCookie(self, args):
        name_pwd = {'aaaUser':{'attributes': {'name': args.adminUser, 'pwd': f"{args.password}"}}}
        json_credentials = json.dumps(name_pwd)
        logonRequest = self.getData(url=f"https://{args.serverName}/api/aaaLogin.json", data=json_credentials, headers={"Content-Type": "application/json"})
        #print(logonRequest)
        logonRequestAttributes = json.loads(logonRequest)['imdata'][0]['aaaLogin']['attributes']
        return logonRequestAttributes['token']

class validation:
    def validateIP(self, ips):
        processIP=False
        ipList=[]
        if (len(ips) != 0):
            for ip in ips:
                try:
                    socket.inet_aton(ip)
                    ipList.append(ip)
                    processIP=True
                except socket.error:
                    print('Dropping IP: {0} ---> Format incorrect'.format(ip))
        if ((len(ips) > 0) and (len(ipList) == 0)):
            print('No processable IP addresses in the IP list provided.')
            print('Script will exit')
            quit()
        return processIP, ipList

    def validateMAC(self, macs):
        processMAC = False
        mac_pattern = re.compile('^[A-F0-9]{12}$')
        macList = []
        if (len(macs) != 0):
            for one_mac in macs:
                unformatedMAC = re.sub('[-\.:]', '', one_mac.upper())
                # Validate MAC format
                if mac_pattern.match(unformatedMAC):
                    macList.append('{0}:{1}:{2}:{3}:{4}:{5}'.format(
                        unformatedMAC[0:-10],
                        unformatedMAC[2:-8],
                        unformatedMAC[4:-6],
                        unformatedMAC[6:-4],
                        unformatedMAC[8:-2],
                        unformatedMAC[10:]
                    ))
                    processMAC = True
                else:
                    "Dropping MAC: {0} ---> Format incorrect".format(one_mac)
        if (len(macs) > 0) and (len(macList) == 0):
            print('No processable MAC addresses in the MAC list provided.')
            print('Script will exit')
            quit()
        return processMAC, macList




