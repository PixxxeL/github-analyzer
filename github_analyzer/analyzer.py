# -*- coding: utf-8 -*-

import datetime
import logging
import re

from api import GithubApi
import conf


logger = logging.getLogger(__name__)

class Analyzer(object):

    __repo_re = re.compile(r'.*/?/?github\.com/([^/]+)/([^/\?]+).*')
    __commits_users_limit = conf.COMMITS_USERS_LIMIT

    def __init__(self, repo_url, start_date=None, end_date=None, branch='master', auth=None):
        self.__user, self.__project = map(
            lambda s: s.lower(),
            self.parse_repo_url(repo_url)
        )
        self.__start_date = self.parse_input_date(start_date)
        self.__end_date = self.parse_input_date(end_date)
        self.__branch = branch or 'master'
        self.__api = GithubApi(
            self.__user,
            self.__project,
            branch=self.__branch,
            auth=auth
        )

    def report_data(self):
        data = self.get_commits()
        data.update(self.get_pull_requests())
        data.update(self.get_issues())
        return data

    def get_commits(self):
        '''
        Самые активные участники.
        login commits_count(desc)
        self.__commits_users_limit
        '''
        logger.debug('Get commits info')
        data = {}
        for commit in self.__api.get_commits():
            _ = commit['commit']
            date = self.parse_api_date(
                _.get('author', _.get('committer', {})).get('date')
            )
            if self.__filter_by_date(date):
                continue
            user = commit.get('author', commit.get('committer'))
            if not user:
                continue
            login = user['login']
            if data.has_key(login):
                data[login] += 1
            else:
                data[login] = 1
        data = sorted(list(data.items()), key=lambda item: item[1], reverse=True)
        return {
            'commits' : data[:self.__commits_users_limit],
        }

    def get_pull_requests(self):
        '''
        Количество открытых и закрытых pull requests.
        Количество “старых” pull requests.
        Pull request считается старым, если он не закрывается в течение 30 дней.
        '''
        logger.debug('Get pull requests info')
        return {
            'pull_requests' : self.__get_with_state(
                self.__api.get_pull_requests, 30
            )
        }

    def get_issues(self):
        '''
        Количество открытых и закрытых issues.
        Количество “старых” issues.
        Issue считается старым, если он не закрывается в течение 14 дней.
        '''
        logger.debug('Get issues info')
        return {
            'issues' : self.__get_with_state(
                self.__api.get_issues, 14
            )
        }

    def parse_repo_url(self, repo_url):
        try:
            return self.__repo_re.findall(repo_url)[0]
        except IndexError:
            raise AnalyzerError('Invalid repository URL')

    def parse_api_date(self, dt_string):
        '''
        Конвертация даты из API: ISO 8601 YYYY-MM-DDTHH:MM:SSZ
        '''
        return datetime.datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%SZ')

    def parse_input_date(self, dt_string):
        '''
        Конвертация даты из строки YYYY-MM-DD
        '''
        if not dt_string:
            return
        try:
            return datetime.datetime.strptime(dt_string, '%Y-%m-%d')
        except ValueError:
            raise AnalyzerError('Invalid date format. Must be YYYY-MM-DD')

    @property
    def user(self):
        return self.__user

    @property
    def project(self):
        return self.__project

    def __get_with_state(self, api_meth, days_ago):
        data = {
            'opened' : 0,
            'closed' : 0,
            'oldest' : 0,
        }
        ago = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        for item in api_meth():
            created = self.parse_api_date(item['created_at'])
            if self.__filter_by_date(created):
                continue
            state = item['state']
            if state == 'open':
                data['opened'] += 1
                if created < ago:
                    data['oldest'] += 1
            elif state == 'closed':
                data['closed'] += 1
        return data

    def __filter_by_date(self, date):
        if self.__start_date and self.__start_date > date:
            return True
        if self.__end_date and self.__end_date < date:
            return True


class AnalyzerError(Exception):pass
