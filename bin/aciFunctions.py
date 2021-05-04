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

import json
import re
import csv
from common import urlFunctions

URL = urlFunctions()

class endPointFunctions:
    def __init__(self, filePath, writeCsv, debug=False):
        self.filePath = filePath
        self.writeCsv = writeCsv
        self.debug = debug
        if writeCsv == True:
            self.csvFileObj = open(filePath, 'w')
            self.csvWriter = csv.writer(self.csvFileObj, delimiter=',', quotechar='"')

        return

    def epJSONtoField(self, jsonData, baseurl, authCookie):
        endPoints = json.loads(jsonData)['imdata']
        self.epFullDetailHeader()
        for epJSON in endPoints:
            epDetailRequest = baseurl +\
                              '/api/node/mo/{0}'.format(epJSON['fvCEp']['attributes']['dn']) +\
                              '.json?query-target=subtree&'+\
                              'target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm'
            epDetailResponseRaw = URL.getData(url=epDetailRequest,cookie={"APIC-Cookie": authCookie},requestType='get')
            self.epFullDetails(epDetailResponseRaw)
        return

    def epFullDetailHeader(self):
        Column1 = 'MAC Address'
        Column2 = 'IP Address'
        Column3 = 'Encapsulation'
        Column4 = 'Tenant Name'
        Column5 = 'Application Name'
        Column6 = 'EPG Name'
        Column7 = 'Leaf Switch'
        Column8 = 'Interface'
        if self.writeCsv == True:
            self.csvWriter.writerow(
                [Column1,
                Column2,
                Column3,
                Column4,
                Column5,
                Column6,
                Column7,
                Column8])

        print(
            ' {0:19} | {1:17} | {2:16} | {3:20} | {4:20} | {5:20} | {6:20} | {7:20}'.format(
                Column1,
                Column2,
                Column3,
                Column4,
                Column5,
                Column6,
                Column7,
                Column8
            ))
        return

    def epFullDetails(self,jsonData):
        endPoint = json.loads(jsonData)['imdata']
        result = []
        if self.debug:
           print(endPoint)
        for one in endPoint:
            for key, value in one.items():
                if self.debug:
                    print(f"\n----- Key: {key}")
                    print(f"\n----- Value: {value} ")
                if key == 'fvCEp':
                    mac, ip, encap, tenant, app, epg = self.process_fvCEp(value)
                #elif key == 'fvRsCEpToPathEp' or key == 'fvRsToNic' or key == fvRsToVm:
                elif key == 'fvRsCEpToPathEp':
                    result.append( self.process_fvRsCEpToPathEp(value))
                    if self.debug:
                        print(f"\n\n##### Result Debug: {result} #####")
                        print(f"##### Result Length:    {len(result)}\n\n") 
        interfaceCount = len(result) - 1
        if self.debug:
            print(f"Result Count: {interfaceCount}")

        if interfaceCount <= 0:
            learnedInterface = 'None'
            learnedLeaf = 'None'
        for interface in result:
            learnedLeaf = f"{interface[2]}"
            learnedInterface = f"{interface[3]}"
            if interface[0] == True:
                break
        print(' {0:19} | {1:17} | {2:16} | {3:20} | {4:20} | {5:20} | {6:20} | {7:20}'.format(
                mac,
                ip,
                encap,
                tenant,
                app,
                epg,
                learnedLeaf,
                learnedInterface))
        if self.writeCsv == True:
            self.csvWriter.writerow(
                [mac,
                ip,
                encap,
                tenant,
                f'{app}',
                epg,
                learnedLeaf,
                learnedInterface])
        return

    def process_fvRsCEpToPathEp(self, value):
        vmm = False
        learned = False
        lcC = (value['attributes']['lcC']).split()
        for one in lcC:
            if one == 'learned':
                learned = True
            if one == 'vmm':
                vmm = True
        interface, leaf = self.process_dn(value['attributes']['dn'])
        return learned, vmm, leaf, interface

    def process_dn(self, dn_raw):
        if self.debug:
            print(f'\t##### Sent DN: {dn_raw} ##### ')
        searchResult = re.search('pathep-\[(.+)\]\]', dn_raw)
        lf = re.search('(paths-|protopaths-)(.*)/pathep-', dn_raw)
        if self.debug:
            print(f'\t##### Search Result: {searchResult} ##### ')
            print(f'\t##### lf Result: {lf} ##### ')
        if searchResult and lf:
            return searchResult.group(1), lf.group(2)
        else:
            return "None", "None"

    def process_fvCEp(self, value):
        dnSplit = (value['attributes']['dn']).split('/')
        return value['attributes']['mac'], \
               value['attributes']['ip'], \
               value['attributes']['encap'], \
               dnSplit[1][3:], \
               dnSplit[2][3:], \
               dnSplit[3][4:]

    def searchOneIpEp(self, ip, baseurl, authCookie):
        #This is just to get the DN. This does not return all of the end point data we need.
        ipRequest = baseurl +\
                    '/api/node/class/fvCEp.json?'+\
                    'rsp-subtree=full&'+\
                    'rsp-subtree-include=required&'+\
                    'rsp-subtree-filter=eq(fvIp.addr,"{0}")'.format(ip)
        ipResponseRaw = URL.getData(ipRequest,authCookie)
        self.epJSONtoField(ipResponseRaw, baseurl, authCookie)
        return

    def searchOneMacEp(self, mac, baseurl, authCookie):
        macRequest = baseurl + '/api/node/class/fvCEp.json?' +\
                     'rsp-subtree=full&' +\
                     'rsp-subtree-include=required&' +\
                     'query-target-filter=eq(fvCEp.mac,"{0}"'.format(mac)
        macResponseRaw = URL.getData(macRequest, authCookie)
        self.epJSONtoField(macResponseRaw, baseurl, authCookie)
        return
