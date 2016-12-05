import json, pycurl, time
from io import BytesIO
from slugify import slugify


class Sonarr():

    def __init__(self, host, port, api_key):
        self.__host = host
        self.__port = port
        self.__api_key = api_key
        self.reply = {}

    def __apicall(self, host, port, request_type, api_key, endpoint, data):
        buffer = BytesIO()
        c = pycurl.Curl()

        c.setopt(pycurl.URL, 'http://' + host + ':' + port + '/api/' + endpoint + "?apikey=" + api_key)
        c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])

        if request_type == 'post':
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, json.dumps(data))

        if request_type == 'put':
            c.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, json.dumps(data))

        if request_type == 'delete':
            c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')

        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(c.WRITEDATA, buffer)

        try:
            c.perform()
            c.close()
        except pycurl.error:
            return 'Failed communicating with Sonarr.'

        try:
            return buffer.getvalue().decode('utf-8')
        except json.JSONDecodeError:
            return 'JSON API failure'

    def addshow(self, title, poster, tvdb_id, path, quality):
        data = {
            "title": title,
            "images": [
                {
                    "coverType": "poster",
                    "url": poster
                }
            ],
            "seasons": [
                {
                    "seasonNumber": 0,
                    "monitored": False
                }
            ],
            "path": path + title,
            "qualityProfileId": quality,
            "seasonFolder": True,
            "monitored": False,
            "tvdbId": tvdb_id,
            "titleSlug": slugify(title),
        }

        request = self.__apicall(self.__host, self.__port, "post", self.__api_key, 'series', data)

        try:
            request_json = json.loads(request)

            try:
                try:
                    self.reply = request_json

                    time.sleep(1)

                    update_show_json = json.loads(self.__apicall(self.__host, self.__port, 'get', self.__api_key, 'series/' + str(request_json['id']), {}))
                    update_show_json['monitored'] = True

                    self.__apicall(self.__host, self.__port, 'put', self.__api_key, 'series', update_show_json)

                    return True
                except TypeError:
                    self.reply = {
                        'message': 'Show already requested.'
                    }
                    return False
            except KeyError:
                self.reply = request_json
                return True

        except json.JSONDecodeError:
            return False

    def search_for_seasons(self, sonarr_id, seasons):

        for season in seasons.split(','):
            if season == '-1':
                data = {
                    'name': 'SeriesSearch',
                    'seriesId': sonarr_id,
                }
            else:
                data = {
                    'name': 'SeasonSearch',
                    'seriesId': sonarr_id,
                    'seasonNumber': season
                }

            self.__apicall(self.__host, self.__port, 'post', self.__api_key, 'command', data)

    def delete_show(self, sonarr_id):

        request = self.__apicall(self.__host, self.__port, 'delete', self.__api_key, 'series/' + str(sonarr_id), {})

        try:
            request_json = json.loads(request)

            if request_json == {}:
                self.reply = request_json
                return True
            else:
                self.reply = {
                    'message': 'Failed to delete show.',
                    'success': False,
                }
                return False

        except json.JSONDecodeError:
            self.reply = {
                'message': request,
                'success': False,
            }
            return False