# -*- coding: utf-8 -*-

import argparse
import sys

from analyzer import Analyzer
import conf
import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description='Analyze of repository by github URL'
    )
    parser.add_argument(
        '-u', '--url', action="store", dest='url', required=True,
        help='URL of analyzed repository'
    )
    parser.add_argument(
        '-s', '--start-date', action="store", dest='start_date', default=None,
        help='Start date of analyze priod as YYYY-MM-DD'
    )
    parser.add_argument(
        '-e', '--end-date', action="store", dest='end_date', default=None,
        help='End date of analyze priod as YYYY-MM-DD'
    )
    parser.add_argument(
        '-b', '--branch', action="store", dest='branch', default='master',
        help='Branch of analyzed repository'
    )
    return parser.parse_args()


def get_data(url, **kwargs):
    return Analyzer(url, auth=conf.GITHUB_BASIC_AUTH, **kwargs).report_data()


def view(data):
    out(u'Самые активные участники:\n')
    map(lambda _: out(u'%20s %s' % tuple(_)), data['commits'])
    _ = data['pull_requests']
    out(u'\nКоличество открытых pull requests: %s' % _['opened'])
    out(u'Количество закрытых pull requests: %s' % _['closed'])
    out(u'Количество старых pull requests: %s' % _['oldest'])
    _ = data['issues']
    out(u'\nКоличество открытых issues: %s' % _['opened'])
    out(u'Количество закрытых issues: %s' % _['closed'])
    out(u'Количество старых issues: %s' % _['oldest'])


def out(unicode_str):
    print unicode_str.encode(sys.stdout.encoding)


def main():
    view(get_data(**dict(parse_args()._get_kwargs())))


if __name__ == '__main__':
    main()
