import os, sys, re, json

#bigipObjectsLineRegex = '^(?P<virtualServerName>.*),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(<?<virtualServerPort>[0-9]{1,5}),(?P<virtualServerPool>.*),(?P<poolMemberAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))+'
#bigipObjectsLineRegex = '^(?P<virtualServerName>[0-9a-zA-Z\-\_]+),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(<?<virtualServerPort>[0-9]+),(?P<virtualServerPool>.*),(?P<poolMemberAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))+'
bigipObjectsLineRegex = '^(?P<virtualServerName>[0-9a-zA-Z\-\_]+),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(?P<virtualServerPort>[0-9]+),(?P<virtualServerPool>[0-9a-zA-Z\-\_]+),(?P<virtualServerPoolPort>[0-9]+),(?P<poolMemberAddress1>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress2>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress3>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress4>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress5>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*'


as3AppName = "csvToDeclarativeApp"
#For port 80 virtual server
#asVirtualServerPort = "Service_HTTP"
#For port 443 virtual server
asVirtualServerPort = "Service_HTTPS"

as3Dict = {}

as3Dict['class'] = "AS3"
as3Dict['action'] = "deploy"
as3Dict['persist'] = True
as3Dict['declaration'] = {}
as3Dict['declaration']['class'] = "ADC"
as3Dict['declaration']['schemaVersion'] = "3.7.0"
as3Dict['declaration'][as3AppName] = {}
as3Dict['declaration'][as3AppName]['class'] = "Tenant"
as3Dict['declaration'][as3AppName]['A1'] = {}
as3Dict['declaration'][as3AppName]['A1']['class'] = "Application"
as3Dict['declaration'][as3AppName]['A1']['service'] = {}
as3Dict['declaration'][as3AppName]['A1']['service']['class'] = asVirtualServerPort
as3Dict['declaration'][as3AppName]['A1']['service']["virtualAddresses"] = [0]
as3Dict['declaration'][as3AppName]['A1']['service']["virtualAddresses"][0] = "10.0.1.10"
#as3Dict['declaration'][as3AppName]['A1']['service']["virtualAddresses"][1] = "10.0.1.11"

print(as3Dict['declaration'][as3AppName]['A1']['service']["virtualAddresses"][0])

if len(sys.argv) < 1:
    sys.exit('Usage: %s <bigiplist.txt>' % sys.argv[0])

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: File %s was not found!' % sys.argv[1])

print("Hi")
for line in open(sys.argv[1], 'r'):

		print(line)

		matchBigipLine = re.match(bigipObjectsLineRegex,line)
		
		if matchBigipLine:
		
			print("Hello")
			print(matchBigipLine.group('virtualServerName'))
			print(matchBigipLine.group('virtualServerIPAddress'))
			print(matchBigipLine.group('virtualServerPort'))
			
			if matchBigipLine.group('poolMemberAddress2'):
			
				print(matchBigipLine.group('poolMemberAddress2'))
	

# Serializing json  
as3Json = json.dumps(as3Dict, indent = 4) 
print(as3Json)
