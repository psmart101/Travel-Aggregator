import gmail
import re
from datetime import *

__author__ = "aestis"


def importCredentials(filename="credentials"):
    passBook = {}  # {credential type: [username, password]}
    with open(filename + ".txt", "r") as credsFile:
        for line in credsFile:
            if "#" in line:
                credType = line[1:].rstrip("\n")
                print credType
                passBook[credType] = [None] * 2
            elif "user:" in line:
                passBook[credType][0] = line[line.find(":") + 1:].rstrip("\n")
            elif "pass:" in line:
                passBook[credType][1] = line[line.find(":") + 1:].rstrip("\n")
        print passBook
    return passBook


def gmailConnect(passBook, secureAuth=False):
    messages = []
    try:
        if not secureAuth:
            user, pw = passBook["gmail"]
            loginInstance = gmail.login(user, pw)
    # Look into getting an OAuth 2 access Token from Google.
    # https://developers.google.com/accounts/docs/OAuth2

    except gmail.exceptions.AuthenticationError:
        print "<!> Auth Error."

    # loginInstance.inbox().mail()[0].fetch()
    # print loginInstance.inbox().mail()[0].subject

    for message in loginInstance.inbox().mail(unread=True):
        message.fetch()
        # print message.subject
        # print message.body
        # print "-----------"
        messages.append(message)
    return messages


def regexGen(emailType="DELTA"):
    if emailType.upper() == "DELTA":
        flightNoRegex = re.compile("^DELTA \d+$")
        re1 = '((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Tues|Thur|Thurs' \
              '|Sun|Mon|Tue|Wed|Thu|Fri|Sat))'  # Day Of Week 1
        re2 = '(\\s+)'  # White Space 1
        re3 = '((?:(?:[0-2]?\\d{1})|(?:[3][01]{1})))(?![\\d])'  # Day 1
        re4 = '(\\s+)'  # White Space 2
        re5 = '((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|' \
              'Aug(?:ust)?|Sep(?:tember)?|Sept|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))'  # Month 1
        re6 = '(\\s+)'  # White Space 3
        re7 = '((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'  # Year 1
        re8 = '(\\s+)'  # White Space 4
        re9 = '((?:[a-z][a-z0-9_]*))'  # Variable Name 1
        re10 = '(:)'  # Any Single Character 1
        re11 = '(\\s+)'  # White Space 5
        re12 = '((?:[a-z][a-z0-9_]*))'  # Variable Name 2
        re13 = '(\\s+)'  # White Space 6
        re14 = '(\\[.*?\\])'  # Square Braces 1
        re15 = '(\\s+)'  # White Space 7
        re16 = '((?:[a-z][a-z0-9_]*))'  # Variable Name 3
        flightDateRegex = re.compile(
            re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9 + re10 + re11 + re12 + re13 + re14 + re15 + re16,
            re.IGNORECASE | re.DOTALL)
        return flightNoRegex, flightDateRegex


class flight:
    def __init__(self, carrier, flightNum, origin, destination, depTime=None, arrTime=None):
        self.airline = carrier
        self.number = flightNum
        self.origin = origin
        self.destination = destination
        self.depTime = depTime
        self.arrTime = arrTime


def parseEmail(emailText):
    carrier = "DELTA"  # Future: This should be dynamic, according to sender of email
    flights = []
    flightNoRegex, flightDateRegex = regexGen(carrier)
    for line in emailText.split("\n"):
        if flightNoRegex.search(line.strip()):
            flights.append(line)
        elif flightDateRegex.search(line.strip()):
            # The logic will assume that the order of dates matches the order of the flights in the email.
            print line.split()[:4]

    for flight in flights:
        print flight


def main():
    passBook = importCredentials()
    messages = gmailConnect(passBook)
    for message in messages:
        parseEmail(message.body)


if __name__ == "__main__":
    main()
