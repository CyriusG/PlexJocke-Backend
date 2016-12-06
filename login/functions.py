import pycurl
from io import BytesIO
import json
from django.conf import settings

from bs4 import BeautifulSoup


# Takes a username and password and returns the Plex token or nothing if the credentials were incorrect.
def getToken(username, password):
    buffer = BytesIO()
    c = pycurl.Curl()

    # Set the curl header
    header = [
        'Content-Type: application/xml; charset=utf-8',
        'Content-Length: 0',
        'X-Plex-Client-Identifier: 8334-8A72-4C28-FDAF-29AB-479E-4069-C3A3',
        'X-Plex-Product: YTB-SSO',
        'X-Plex-Version: v2.0',
    ]

    # Configure curl with the necessary parameters.
    c.setopt(pycurl.URL, 'https://plex.tv/users/sign_in.json')
    c.setopt(pycurl.HTTPHEADER, header)
    c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    c.setopt(pycurl.USERPWD, '%s:%s' % (username, password))
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.WRITEDATA, buffer)

    # Run curl and close the process
    try:
        c.perform()
        c.close()
    except pycurl.error:
        return None

    # Save the json response into body
    body = json.loads(buffer.getvalue().decode('utf-8'))

    # Try and retrieve the authToken and return it, if it fails return None.
    try:
        return body['user']['authToken']
    except KeyError:
        return None

def testToken(token):
    buffer = BytesIO()
    c = pycurl.Curl()

    # Set the curl header
    header = [
        'X-Plex-Token: ' + token,
    ]

    # Configure curl with the necessary parameters.
    c.setopt(pycurl.URL, 'https://plex.tv/users/account')
    c.setopt(pycurl.HTTPHEADER, header)
    c.setopt(pycurl.WRITEDATA, buffer)

    # Run curl and close the process
    try:
        c.perform()
        c.close()
    except pycurl.error:
        return None

    body = BeautifulSoup(buffer.getvalue().decode('utf-8'))

    try:
        if check_friend(body.user.get('username')):
            return True
        else:
            return False
    except AttributeError:
        return False


def check_friend(username):
    if username != settings.PLEX_OWNER:
        buffer = BytesIO()
        c = pycurl.Curl()

        # Set the curl header
        header = [
            'Content-Type: application/xml; charset=utf-8',
            'Content-Length: 0',
            'X-Plex-Client-Identifier: 8334-8A72-4C28-FDAF-29AB-479E-4069-C3A3',
            'X-Plex-Product: YTB-SSO',
            'X-Plex-Version: v2.0',
            'X-Plex-Token: ' + settings.PLEX_OWNER_TOKEN,
        ]

        # Configure curl with the necessary parameters.
        c.setopt(pycurl.URL, 'https://plex.tv/pms/friends/all')
        c.setopt(pycurl.HTTPHEADER, header)
        c.setopt(pycurl.WRITEDATA, buffer)

        # Run curl and close the process
        try:
            c.perform()
            c.close()
        except pycurl.error:
            return False

        body = BeautifulSoup(buffer.getvalue().decode('utf-8'))

        for user in body.findAll('user'):
            if username == user['username'] or username == user['email']:
                return True
        return False
    else:
        return True
