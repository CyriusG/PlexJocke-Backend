from django.conf import settings

from email.utils import parseaddr

import requests

def send_message(sender, recipient, subject, message, html):
    data = {}

    if '@' in parseaddr(sender)[1] and '@' in parseaddr(recipient)[1]:
        if html:
            data={'from': sender,
                  'to': recipient,
                  'subject': subject,
                  'html': message}
        else:
            data={'from': sender,
                  'to': recipient,
                  'subject': subject,
                  'text': message}

    else:
        return False

    requests.post(settings.MAILGUN_ENDPOINT, auth=('api', settings.MAILGUN_API_KEY), data=data)

    return True
