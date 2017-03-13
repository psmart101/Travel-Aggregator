import gmail
import re
import sys
import csv
import logging
from suds import null, WebFault
from suds.client import Client
from datetime import *

__author__ = "aestis"


def importCredentials(filename="credentials"):
    passBook = {}  # {credential type: [username, password]}
    with open(filename + ".txt", "r") as credsFile:
        for line in credsFile:
            if "#" in line:
                credType = line[1:].rstrip("\n")
                passBook[credType] = [None] * 2
            elif "user:" in line:
                passBook[credType][0] = line[line.find(":") + 1:].rstrip("\n")
            elif "pass:" in line:
                passBook[credType][1] = line[line.find(":") + 1:].rstrip("\n")
    return passBook


def retrieveGmail(secureAuth=False):
    passBook = importCredentials()
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


def carrierEmailRegexGen(domain="e.delta.com"):
    # Handling for flights sent from e.delta.com
    if domain.lower() == "e.delta.com":
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


class segment:
    def __init__(self, carrier, flightNum, origin, destination, depDate, depTime=None, arrTime=None):
        assert isinstance(carrier, airline), "<!> Must instantiate Segment object with an Airline object."

        self.carrier = carrier  # of type 'airline'
        self.number = flightNum
        self.origin = origin
        self.destination = destination
        self.depDate = depDate
        self.depTime = depTime if depTime else ""
        self.arrTime = arrTime if arrTime else ""

    def selfDescribe(self):
        print self.carrier.icao, self.number
        print " ".join([self.depTime, self.origin]) + " - " + " ".join([self.arrTime, self.destination])
        print self.depDate.strftime("%B %d, %Y")

    def flightAwareFormat(self):
        return self.carrier.icao.upper() + self.number


class airline:
    def __init__(self, senderDomain, convention="ICAO"):
        self.domain = senderDomain

        # Lookup other information about airline with getAirlineID()
        self.icao, self.iata, self.callsign, self.airlineName = self.getAirlineID()

        # Use ICAO convention unless otherwise specified.
        self.id = self.icao if convention == "ICAO" else self.iata

    def getAirlineID(self):
        """Retrieve and return an international airline code from the accompanying csv file, iata_icao_airlines
        or iata_icao_airlines_brief.
        :param codeType: Type of airline identifier. 0=IATA, 1=ICAO, 2=Full airline name.
        :param self: Airline: Airline object, which will be searched by domain in accompanying csv.
        :return: String IATA ICAO airline code or full name
        """
        with open("iata_icao_airlines_brief.csv", "r") as csvFile:
            csvReader = csv.reader(csvFile)
            for row in filter(lambda x: x[0] == self.domain, csvReader):
                airlineInfo = row[1:5]
                return airlineInfo

    def selfDescribe(self):
        print self.airlineName
        print "Callsign:", self.callsign
        print "ICAO:", self.icao
        print "IATA:", self.iata


def flightAwareConnect(passBook):
    user, apiKey = passBook["flightAware"]
    url = 'http://flightxml.flightaware.com/soap/FlightXML2/wsdl'

    logging.basicConfig(level=logging.INFO)
    api = Client(url, username=user, password=apiKey)

    return api


def flightAwareQuery(searchCriteria):
    passBook = importCredentials()
    api = flightAwareConnect(passBook)
    flightData = api.service.FlightInfo()


def emailToSegments(inputMessage):
    # Future: Carrier should be dynamic, according to sender of email
    FlightNumList = []
    detailsList = []
    flightsList = []
    emailText = inputMessage.body.split("\n")
    # print emailText
    emailSender = inputMessage.fr  # Future: Attribute sender (personal email address) to user.

    # Scan the header of the email and find sender's domain in From: line
    for line in filter(lambda x: re.search("From: .+<.+@.+>$", x.strip()), emailText[:5]):
        carrierDomain = line[line.find("@") + 1:line.find(">")]

    # Retrieve regex's for specific carrier's email format from carrierEmailRegexGen()
    flightNoRegex, flightDateRegex = carrierEmailRegexGen(carrierDomain)

    # Use regex to parse through lines and find information...
    for line in emailText:
        if flightNoRegex.search(line.strip()):
            # flight number
            FlightNumList.append([line.split()[1]])
        elif flightDateRegex.search(line.strip()):
            # The logic will assume that the order of dates matches the order of the flights in the email.
            dateText = line.split()[1:4]
            # Departure date
            flightDate = datetime.strptime(" ".join(dateText), "%d %b %Y")  # Convert date string into datetime

            # Origin and destination
            origin = line.split()[5]
            destination = line.split()[-1]
            assert len(origin) == 3, "<!> Invalid origin airport; check email parser: " + origin
            assert len(destination) == 3, "<!> Invalid destination airport; check email parser: " + destination

            detailsList.append([origin, destination, flightDate])

    carrier = airline(carrierDomain)

    for eachFlight in zip(FlightNumList, detailsList):
        flightInstantiator = [carrier] + eachFlight[0] + eachFlight[1]
        flightsList.append(segment(*flightInstantiator))
    return flightsList


def main():
    messages = retrieveGmail()
    for message in messages:
        flightsList = emailToSegments(message)
        for flight in flightsList:
            flight.selfDescribe()


if __name__ == "__main__":
    main()
