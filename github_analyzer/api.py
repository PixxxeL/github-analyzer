# -*- coding: utf-8 -*-

import logging
import re
import time
import requests

import conf


logger = logging.getLogger(__name__)

class GithubApi(object):
    '''
    Basic Authentication or OAuth = 5000 requests per hour
    unauthenticated = 60 requests per hour
    @TODO:
        1. Change `page` param processing
        2. union of get_commits, get_issues, get_pull_requests
    '''

    __base_url = 'https://api.github.com'
    __headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    __per_page = 100
    __timeout = conf.API_REQUESTS_TIMEOUT
    __last_page_re = re.compile(r'[^_]page\=([\d]+)')

    def __init__(self, user, project, branch='master', auth=None):
        self.__user = user
        self.__project = project
        self.__branch = branch
        self.__auth = auth

    def get_commits(self):
        '''
        Самые активные участники.
        API doc: https://developer.github.com/v3/git/commits/
        Request: GET /repos/:owner/:repo/git/commits/:sha
        '''
        first_page_url = '%s/repos/%s/%s/commits?per_page=%s' % (
            self.__base_url,
            self.__user,
            self.__project,
            self.__per_page,
        )
        return self.get_total_pages(first_page_url) or []

    def get_issues(self):
        '''
        Количество открытых и закрытых issues.
        Количество “старых” issues.
        Issue считается старым, если он не закрывается в течение 14 дней.
        API doc: https://developer.github.com/v3/issues/
        Request: GET /repos/:owner/:repo/issues?state=closed
        '''
        first_page_url = '%s/repos/%s/%s/issues?state=all&per_page=%s' % (
            self.__base_url,
            self.__user,
            self.__project,
            self.__per_page,
        )
        return self.get_total_pages(first_page_url) or []

    def get_pull_requests(self):
        '''
        Количество открытых и закрытых pull requests.
        Количество “старых” pull requests.
        Pull request считается старым, если он не закрывается в течение 30 дней.
        API doc: https://developer.github.com/v3/pulls/#parameters
        Request: GET /repos/:owner/:repo/pulls
        '''
        first_page_url = '%s/repos/%s/%s/pulls?state=all&base=%s&per_page=%s' % (
            self.__base_url,
            self.__user,
            self.__project,
            self.__branch,
            self.__per_page,
        )
        return self.get_total_pages(first_page_url) or []

    def get_total_pages(self, first_page_url):
        logger.debug('Get first page: %s' % first_page_url)
        response = self.__request(first_page_url)
        data = response.json()
        last_page = self.__response_last_page(response)
        logger.debug('Total pages: %s' % last_page)
        if last_page:
            for i in range(2, last_page + 1):
                url = '%s&page=%s' % (first_page_url, i,)
                logger.debug('Get page: %s' % url)
                response = self.__request(url)
                data.extend(response.json())
                time.sleep(self.__timeout)
        return data

    def __request(self, url):
        response = requests.get(url, headers=self.__headers, auth=self.__auth)
        if response.status_code != 200:
            msg = 'Status code is not 200: %s, %s' % (
                response.status_code, response.text,
            )
            logger.error(msg)
            raise GithubApiError(msg)
        return response

    def __response_last_page(self, response):
        '''
        Header `Link` has view as:
        <https://api.github.com/repositories/4164482/commits?page256=&per_page=100&page=2>; rel="next", <https://api.github.com/repositories/4164482/commits?page256=&per_page=100&page=256>; rel="last"
        '''
        links = response.headers.get('link')
        if links is None:
            return
        for p in links.split(','):
            if p.find('rel="last"') != -1:
                try:
                    return int(self.__last_page_re.findall(p)[0])
                except:
                    pass


class GithubApiError(Exception):pass
