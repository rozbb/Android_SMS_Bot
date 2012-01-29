import android
import time
import random
import re

crapTextFile = "/sdcard/txt_list.txt"
targetsFile = "/sdcard/target_respond_list.txt"


droid = android.Android()

# Get the messages to be sent randomly
crapMessages = []
with open(crapTextFile) as file:
	for line in file:
		crapMessages.append(line.strip())

# Convert the numbers and rules of the file into a dictionary(number,set([rules]))
def parseFile(filename):
	validNumber = re.compile(r"1?\D*(\d{3})\D*(\d{3})\D*(\d{4})")
	numbers = dict()
	currentRule = ""
	with open(filename) as file:
		for line in file:
			# Establish rules
			if line.strip() == "random:": currentRule = "random"
			if line.strip() == "reverse:": currentRule = "reverse"
			if not currentRule: continue

			if validNumber.search(line):
			    number = ''.join(validNumber.search(line).groups())
			    if number in numbers.keys():
			        numbers[number] = numbers[number].union(set([currentRule]))
			    else:
			        numbers[number] = set([currentRule])
	return numbers


messageCount = droid.smsGetMessageCount(True)[1]

targetNumbers = parseFile(targetsFile)

print "Starting with " + str(messageCount) + " unread messages"
print "Crap Message list:"
print crapMessages
print "\n\nTarget numbers:"
for key in targetNumbers:
	responseStr = ""
	for response in targetNumbers[key]:
		responseStr += response + "  "
	print key + "\t" + responseStr
print "\n"

loopCount = -1

while True:
	loopCount += 1
	if droid.smsGetMessageCount(True)[1] > messageCount:
		message = droid.smsGetMessages(True)[1][0]
		#print message
		number = message['address'].replace('+1', '')
		print "Got a message from: " + number 
		if number in targetNumbers.keys():
			for method in targetNumbers[number]: # Iterate through all responses in the set
				if method == "random":
					print "Sending random crap to it..."
					droid.smsSend(number, crapMessages[random.randrange(0, len(crapMessages))])
				elif method == "reverse":
					print "Sending the reverse to it..."
					droid.smsSend(number, message['body'][::-1])

	messageCount = droid.smsGetMessageCount(True)[1]

	if loopCount is 30:	# Check for number change every minute (sleep time between loops is 2 sec)
		tmpDict = parseFile(targetsFile)
		if tmpDict != targetNumbers:
			print "Target numbers changed"
			targetNumbers = tmpDict
		loopCount = 0

	time.sleep(2)
