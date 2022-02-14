import random

#Cant be greater than 255
numberOfVirtuals = 255
virtualServerAddressStart = '192.168.1.'
poolSubnetStart = '10.0.'
virtualName='virtual'
virtualServerPort = "443"
virtualNameAppend  = "_vs"
poolNameAppend = "_pool"
poolPort = "80"
maxNumberOfPoolMembers = 10





for i in range (1,numberOfVirtuals):

	
	printString = virtualName + str(i) + virtualNameAppend + ',' + 	virtualServerAddressStart + str(i) + ',' + virtualServerPort + ',' + virtualName + str(i) + poolNameAppend + ',' + poolPort  + ','
	
	max = random.randint(1, maxNumberOfPoolMembers)

	for x in range(max):
	
		printString  = printString + poolSubnetStart + str(i) + '.' + str(x) + ','
	
	print(printString)



