import json, pycurl
from io import BytesIO


class Couchpotato():

    def __init__(self, host, port, api_key):
        self.__host = host
        self.__port = port
        self.__api_key = api_key
        self.reply = {}

    def __apicall(self, host, port, api_key, endpoint):
        buffer = BytesIO()
        c = pycurl.Curl()

        c.setopt(pycurl.URL, 'http://' + host + ':' + port + '/api/' + api_key + endpoint)
        c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])
        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(c.WRITEDATA, buffer)

        try:
            c.perform()
            c.close()
        except pycurl.error:
            return 'Failed communicating with Couchpotato.'

        try:
            return buffer.getvalue().decode('utf-8')
        except json.JSONDecodeError:
            return 'JSON API failure'

    def addmovie(self, imdb_id):

        request = self.__apicall(self.__host, self.__port, self.__api_key, '/movie.add?identifier=' + imdb_id + '&force_readd=False')

        try:
            request_json = json.loads(request)

            if request_json['success'] == True:
                self.reply = request_json
                return True
            else:
                self.reply = {
                    'message': request_json,
                    'success': False,
                }
                return False

        except json.JSONDecodeError:
            self.reply = {
                'message': 'Failed communicating with Couchpotato.',
                'success': False,
            }
            return False

    def deletemovie(self, cp_id):

        request = self.__apicall(self.__host, self.__port, self.__api_key, '/movie.delete?id=' + cp_id + '&from=wanted')

        try:
            request_json = json.loads(request)

            if request_json['success'] == True:
                self.reply = request_json
                return True
            else:
                self.reply = {
                    'message': 'Failed to delete movie.',
                    'success': False,
                }
                return False

        except json.JSONDecodeError:
            self.reply = {
                'message': request,
                'success': False,
            }
            return False
