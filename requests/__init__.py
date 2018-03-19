# -*- coding: utf-8 -*-
'''
Библиотека-эмулятор requests.
Поддерживаются только свойства и методы, используемые в github_analyzer.
Сигнатура методов не полная, минимально необходимая.
'''

import base64
import json
import urllib2


class Response(object):

    def __init__(self, response):
        self._parse_info(response.info())
        self.data = response.read()

    def json(self):
        return json.loads(self.data)

    def _parse_info(self, info):
        self.headers = {}
        for header in info.headers:
            k, v = header.split(': ')
            self.headers[k.lower()] = v.strip()
        status = self.headers['status'].split(' ')
        self.status_code = int(status[0])


def get(url, headers={}, auth=None):
    request = urllib2.Request(url)
    if isinstance(auth, tuple):
        base64string = base64.encodestring('%s:%s' % auth).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
    if headers:
        map(lambda pair: request.add_header(*pair), headers.items())
    return Response(urllib2.urlopen(request))
