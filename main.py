import argparse
from datetime import datetime
import pytz

import git_logger
import export_sheets

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--invites", help="print pending invites", action="store_true")
    parser.add_argument("-p", help="log pull requests", action="store_true")
    parser.add_argument("-i", help="log issues", action="store_true")
    parser.add_argument("-e", help="export table to google sheets", action="store_true")
    parser.add_argument('-t', '--token', type=str, required=True, help='token github account')
    parser.add_argument('-l', '--list', type=str, required=True, help='repos names file')
    parser.add_argument('-o', '--out', type=str, required=True, help='output filename')
    parser.add_argument('-s', '--start', type=str, required=False, help='start time', default='2000/01/01-00:00:00')
    parser.add_argument('-f', '--finish', type=str, required=False, help='finish time', default='2400/01/01-00:00:00')
    parser.add_argument('-b', '--branch', type=str, required=False, help='branch to select commits, by default use "default" repository branch, use "all" to get all commits from all branches', default=None)
    parser.add_argument('--google_token', type=str, required=False, help='Specify path to google token file')
    parser.add_argument('--table_id', type=str, required=False,
                        help='Specify Google sheet document id (can find in url)')
    parser.add_argument('--sheet_id', type=str, required=False,
                        help='Specify title for a sheet in a document in which data will be printed')
    args = parser.parse_args()
    
    if args.e:
        for action in parser._actions:
            if action.dest == 'google_token':
                action.required = True
            if action.dest == 'table_id':
                action.required = True
            if action.dest == 'sheet_id':
                action.required = True
    return parser.parse_args()


def parse_time(datetime_str):
    start = datetime_str[0].split('/') + datetime_str[1].split(':') if len(datetime_str) == 2 \
        else datetime_str[0].split('/') + ['00', '00', '00']
    start = [int(i) for i in start]
    start_datetime = datetime(year=start[0], month=start[1], day=start[2], hour=start[3], minute=start[4],
                              second=start[5])
    return start_datetime.astimezone(pytz.timezone(git_logger.timezone))


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
        if not args.p and not args.i and not args.invites:
            git_logger.log_commits(client, repositories, csv_name, start, finish, args.branch)
            if (args.e):
                export_sheets.write_data_to_table(csv_name, args.google_token, args.table_id, args.sheet_id)
        if args.p:
            git_logger.log_pull_requests(client, repositories, csv_name, token, start, finish)
            if (args.e):
                export_sheets.write_data_to_table(csv_name, args.google_token, args.table_id, args.sheet_id)
        if args.i:
            git_logger.log_issues(client, repositories, csv_name, token, start, finish)
            if (args.e):
                export_sheets.write_data_to_table(csv_name, args.google_token, args.table_id, args.sheet_id)
        if args.invites:
            git_logger.log_invitations(client, repositories, csv_name)


if __name__ == '__main__':
    main()
