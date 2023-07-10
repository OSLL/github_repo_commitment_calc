import argparse
from datetime import datetime
import pytz

import git_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="log pull requests", action="store_true")
    parser.add_argument("-i", help="log issues", action="store_true")
    parser.add_argument('-t', '--token', type=str, required=True, help='token github account')
    parser.add_argument('-l', '--list', type=str, required=True, help='repos names file')
    parser.add_argument('-o', '--out', type=str, required=True, help='output filename')
    parser.add_argument('-s', '--start', type=str, required=False, help='start time', default='2000/01/01-00:00:00')
    parser.add_argument('-f', '--finish', type=str, required=False, help='finish time', default='2400/01/01-00:00:00')
    return parser.parse_args()


def parse_time(datetime_str):
    start = datetime_str[0].split('/') + datetime_str[1].split(':') if len(datetime_str) == 2 \
        else datetime_str[0].split('/') + ['00', '00', '00']
    start = [int(i) for i in start]
    start_datetime = datetime(year=start[0], month=start[1], day=start[2], hour=start[3], minute=start[4],
                              second=start[5])
    return start_datetime.astimezone(pytz.timezone('Europe/Moscow'))


def main():
    args = parse_args()
    token = args.token
    repositories = args.list
    csv_name = args.out

    try:
        client = git_logger.login(token=token)
    except Exception as e:
        print(e)
    else:
        if args.start:
            start = parse_time(args.start.split('-'))
        if args.finish:
            finish = parse_time(args.finish.split('-'))
        if not args.p and not args.i:
            git_logger.log_commits(client, repositories, csv_name, start, finish)
        if args.p:
            git_logger.log_pull_requests(client, repositories, csv_name, start, finish)
        if args.i:
            git_logger.log_issues(client, repositories, csv_name, start, finish)



if __name__ == '__main__':
    main()
