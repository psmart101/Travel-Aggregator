import gmail

__author__ = "aestis"


def importCredentials(filename="credentials"):
    passBook = {}  # {credential type: [username, password]}
    with open(filename+".txt","r") as credsFile:
        for line in credsFile:
            if "#" in line:
                credType = line[1:]
                passBook[credType] = [None]*2
            elif "user:" in line:
                passBook[credType][0] = line[line.find(":")+1:]
            elif "pass:" in line:
                passBook[credType][1] = line[line.find(":")+1:]
    return passBook


def gmailConnect(passBook, secureAuth=False):
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
        print message.body
        print "-----------"

def main():
    passBook = importCredentials()
    gmailConnect(passBook)
