import gmail
import re
from datetime import *

__author__ = "aestis"


def importCredentials(filename="credentials"):
    passBook = {}  # {credential type: [username, password]}
    with open(filename+".txt","r") as credsFile:
        for line in credsFile:
            if "#" in line:
                credType = line[1:].rstrip("\n")
                print credType
                passBook[credType] = [None]*2
            elif "user:" in line:
                passBook[credType][0] = line[line.find(":")+1:].rstrip("\n")
            elif "pass:" in line:
                passBook[credType][1] = line[line.find(":")+1:].rstrip("\n")
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


class flight:
    def __init__(self, carrier, flightNum, ):
        self.airline = carrier
        self.number = flightNum


def parseEmail(emailText, emailType="delta"):
    # print emailText
    z = emailText.split("\n")[20]
    flightNoRegex = re.compile("^DELTA \d+$")
    for line in emailText.split("\n"):

        if flightNoRegex.search(line.strip()): print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!"+line
        # if re.search("^DELTA .+$", line): print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!" + line
        # Search for any line with 'DELTA 0000' where 0000 is any number of integers


def main():
    passBook = importCredentials()
    messages = gmailConnect(passBook)
    for message in messages:
        parseEmail(message.body)

if __name__ == "__main__":
    main()
