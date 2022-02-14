import os, sys, re, json

#bigipObjectsLineRegex = '^(?P<virtualServerName>.*),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(<?<virtualServerPort>[0-9]{1,5}),(?P<virtualServerPool>.*),(?P<poolMemberAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))+'
#bigipObjectsLineRegex = '^(?P<virtualServerName>[0-9a-zA-Z\-\_]+),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(<?<virtualServerPort>[0-9]+),(?P<virtualServerPool>.*),(?P<poolMemberAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))+'
#bigipObjectsLineRegex = '^(?P<virtualServerName>[0-9a-zA-Z\-\_]+),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(?P<virtualServerPort>[0-9]+),(?P<virtualServerPool>[0-9a-zA-Z\-\_]+),(?P<virtualServerPoolPort>[0-9]+),(?P<poolMemberAddress1>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress2>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress3>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress4>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*,*(?P<poolMemberAddress5>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))*'
bigipObjectsLineRegex = '^(?P<virtualServerName>[0-9a-zA-Z\-\_]+),(?P<virtualServerIPAddress>((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])),(?P<virtualServerPort>[0-9]+),(?P<iRule>[0-9a-zA-Z\-\_]+),(?P<virtualServerPool>[0-9a-zA-Z\-\_]+),(?P<virtualServerPoolPort>[0-9]+),(?P<poolMemberAddressGroup>(((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]),*)+)'
addressGroupRegex='(((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]),*)'
as3ClientsslProfileAppend = "_clientssl"
as3PoolAppend = "_pool"
as3VirtualServerSNAT = "auto"
as3VSAppend = "_vs"
as3SSLCertificateAppend = "_cert"
as3CertificateName = '"bigip":"/Common/default.crt"'
as3KeyName = '"bigip":"/Common/default.key"'
as3CertificateBlob = "-----BEGIN CERTIFICATE-----\nMIIDSDCCAjCgAwIBAgIEFPdzHjANBgkqhkiG9w0BAQsFADBmMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHU2VhdHRsZTESMBAGA1UEAxMJQWNtZSBDb3JwMRwwGgYJKoZIhvcNAQkBFg10ZXN0QGFjbWUuY29tMB4XDTIxMDIyMzE1MjYyMloXDTIyMDIyMzE1MjYyMlowZjELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1NlYXR0bGUxEjAQBgNVBAMTCUFjbWUgQ29ycDEcMBoGCSqGSIb3DQEJARYNdGVzdEBhY21lLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMlj0IAPjyzSJzJZXzPPKnWWu6ErkfUhujBk1nQdp++K8YrvocLY5rbY/DZ9ipEz1TxIyZAGl9aBPoLGU4r2XNVMJZA5Zo/QMedEZFal14eOHn3JMMvCDjGrFaWR+cZ2TR9D9Jdxytq9QKUS/JdCKYz/Qxbx2Q4o0nZDqmPAipw//E24y4lLya/Qrwb537QoCGnxgMoUVNi9ruYrnGtS4uPth3+jYmbbivb8G1B8x93Peeu1QHBlOaXr6DndSwKcULIUt2RxcyYcjzeVQ5yrcrVHwvF8eb03Llm10zX0UI68vdjQuMpeUZ7K0RlmO59v0u6XdeoK1s82SJ8ufscqIrcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAN78Mxd1ZE9nUNefCxmqdJYbQUzO6baHgqWxNLRuIu/EtJsjBAuuMmpWOd+pWBQS42aDOrUc33zpcNJcquBvtKt6QaKnSzJwCyfk88ACNrb7yFyeKB3YhVALfLkJMal032pvV8U0n4FBlqRTUDrSY2MHaJ/Uar7iJ7t3RBoZ9LbTyikW188hW6h9s238oLOW89FIJluov18uyLJaj8sBP5tInZmnO3EEywzNop0vpqMe0XmTo9Dyq9SFRdcDnptSdoNLLWTXmpXacj/u/f9r7zQqneFbj2b0KqetYLb7Xs5BVi0DfC81FYOEwqiq+kYvEkBubNCP1C8fXzB/65kFXtg==\n-----END CERTIFICATE-----"
as3PrivateKeyBlob = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDJY9CAD48s0icyWV8zzyp1lruhK5H1IbowZNZ0HafvivGK76HC2Oa22Pw2fYqRM9U8SMmQBpfWgT6CxlOK9lzVTCWQOWaP0DHnRGRWpdeHjh59yTDLwg4xqxWlkfnGdk0fQ/SXccravUClEvyXQimM/0MW8dkOKNJ2Q6pjwIqcP/xNuMuJS8mv0K8G+d+0KAhp8YDKFFTYva7mK5xrUuLj7Yd/o2Jm24r2/BtQfMfdz3nrtUBwZTml6+g53UsCnFCyFLdkcXMmHI83lUOcq3K1R8LxfHm9Ny5ZtdM19FCOvL3Y0LjKXlGeytEZZjufb9Lul3XqCtbPNkifLn7HKiK3AgMBAAECggEAHrvaWmjFd1gc/jyQYFY5yxc1TCvbivbaNL920OKjudVQ9lyKqbMzRm1H1EMFbhJkdN5A0HeJHYW81fVRU5A0a6LCysdPxRvHOd2AmI6XnUrNkXGuPjI/u0m6NHnaDfUI4QAcaC5IAGjIYEjM/oJs1+UuxmYjM1t8furlqnJ8VMrTtfumTSzEoq3OSwK6JlxAtRwBkrYr+pZCI82Ao/ouZcktyO+LjLMCYd/7HpskA0G3Pp/SIjhfbNHsTm4Kvzar0XdxBVMu4M0a6xXvX+I/L8UFa7EuDumwQVdttMnG33+xbCX3yIrndxVk0rOCryYqeItOxSG+aZJ6ZN+r0crgvQKBgQDlolxVh3NQCqa9XS+TCXSGfcZENolAIEu+n6CkZKMqQrmz7KPrblHgMbc54x0jH/GhtkY4wMjV1stqqHWTBV9UqVcb+OXPt8Zwa0JvXEM3b0i9GTp2hQfKGbWTEz7PIUZbZPGrIijHrc4wX2rgq7K5GeUfteh7bZij0cQ5ubFXBQKBgQDgg0SzUIN87D7yRPqvVnd7l0yii740UztWDp/YDpml0T6WfG0rlXqnIEebUS+BxGNDt3ksG7dTfJIE34C/SlYBAlJ5hiJ4rErW7pm+ibLa96qnLAGEQpiwnYmV49Uc2mxxRuBFWqKal4tuY6MxNqaf2NLCT4JKTPMffRR0Iz/HiwKBgFN659hMCpaxmJZE1zO7/zmZZceMj+7ZDtA41byNvWdypHINeDXxgCBh0ntf3krTpRMl4XdmVlyu3npizYNqM5LikQFhRaJy69gYlilHwEPZ1/auwjst93v4RrM2DuJb9WjqVJTjMTIONGQPfBo7MRjrmgkiJ2cfm5sKeiyGHjtFAoGAOvwB1qJ2iSGAQCJDQkGTTpMnfST9qb2cPzXEZP0g/OGGcf7qp6K0AKiIZ5PiyVMRST8wxJfbiEGYE1Os/ZTIF6fGh0roT4/kcadqGRcQOFsNKLJ1C4x7lRsuhITA/r2b8/7M+SugwMDDzxK6UzmqeSB77rT45BBnZ4RzFTgVj5UCgYBasm6nh2v8PzE8aXzYM6YWsM5R0l3Xr2YvycLc6HfI5Sen+yqIyE9qDNFFk8qa3RZVKl83ZTk7wtAL8nMupmdVodNrx4pUgFW4U4WPPSvVXRZRTZdLHwGKw5Fa3u48qFxdYqpZmnBMB2RHEKcRB8T1+RkcByghNnCBwJMJSRHIWA==\n-----END PRIVATE KEY-----"
as3PoolMonitor = "http"
as3LoadBalancingMode = "round-robin"
as3CreateRedirectVSBoolean = False
as3iRuleNamePartition = '/Common/'

as3AppName = "csvToDeclarativeApp"
as3VirtualServerPortMappingDict = {}
as3VirtualServerPortMappingDict["80"] = "Service_HTTP"
as3VirtualServerPortMappingDict["443"] = "Service_HTTPS"
l4ServiceClass = "Service_L4"

as3Dict = {}

as3Dict['class'] = "AS3"
as3Dict['action'] = "deploy"
as3Dict['persist'] = True
as3Dict['declaration'] = {}
as3Dict['declaration']['class'] = "ADC"
as3Dict['declaration']['schemaVersion'] = "3.7.0"
as3Dict['declaration'][as3AppName] = {}
as3Dict['declaration'][as3AppName]['class'] = "Tenant"



if len(sys.argv) < 1:
    sys.exit('Usage: %s <bigiplist.txt>' % sys.argv[0])

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: File %s was not found!' % sys.argv[1])

for line in open(sys.argv[1], 'r'):


		matchBigipLine = re.match(bigipObjectsLineRegex,line)
		
		if matchBigipLine:
		
				
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')]['class'] = "Application"
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ] = {}
			#as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]['class'] = as3VirtualServerPortMappingDict[matchBigipLine.group('virtualServerPort')]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]['class'] = as3VirtualServerPortMappingDict.get(matchBigipLine.group('virtualServerPort'),l4ServiceClass)
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["virtualAddresses"] = [0]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["virtualAddresses"][0] = matchBigipLine.group('virtualServerIPAddress')
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ][ 'virtualPort' ] = int(matchBigipLine.group('virtualServerPort'))
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["pool"] = matchBigipLine.group('virtualServerName') + as3PoolAppend
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["serverTLS"] = matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["snat"] = as3VirtualServerSNAT 
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["redirect80"] = as3CreateRedirectVSBoolean
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["iRules"] = [0]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["iRules"][0] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][matchBigipLine.group('virtualServerName') + as3VSAppend ]["iRules"][0]['bigip'] = as3iRuleNamePartition + matchBigipLine.group('iRule')


			#pool
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ][ "class" ] = "Pool" 
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ][ "loadBalancingMode" ] = as3LoadBalancingMode
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["monitors"] = [0]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["monitors"][0] = as3PoolMonitor
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"] = [0]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0]["servicePort"] = int(matchBigipLine.group('virtualServerPoolPort'))
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0]["shareNodes"] = True
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0]["serverAddresses"] = []
			#as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0]["serverAddresses"][0] = matchBigipLine.group('poolMemberAddressGroup')
			
			regexPattern = re.compile(addressGroupRegex)
						
			for match in re.finditer(regexPattern,matchBigipLine.group('poolMemberAddressGroup')):
				as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3PoolAppend ]["members"][0]["serverAddresses"].append(match.group(1).replace(',',''))

		

			#Create clientssl profile
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ]["class"] = "TLS_Server"
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ]["certificates"] = [0]
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ]["certificates"][0] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ]["certificates"][0]["certificate"] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3ClientsslProfileAppend ]["certificates"][0]["certificate"] = matchBigipLine.group('virtualServerName') + as3SSLCertificateAppend
			
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3SSLCertificateAppend ] = {}
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3SSLCertificateAppend ]["class"] = "Certificate"
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3SSLCertificateAppend ]["certificate"] = as3CertificateBlob
			as3Dict['declaration'][as3AppName][matchBigipLine.group('virtualServerName')][ matchBigipLine.group('virtualServerName') + as3SSLCertificateAppend ]["privateKey"] = as3PrivateKeyBlob


# Serializing json  
as3Json = json.dumps(as3Dict, indent = 4) 
print(as3Json)
