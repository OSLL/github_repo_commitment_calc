import argparse
import git_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="log pull requests", action="store_true")
    parser.add_argument("-i", help="log issues", action="store_true")
    parser.add_argument('-t', '--token', type=str, required=True, help='token github account')
    parser.add_argument('-l', '--list', type=str, required=True, help='repos names file')
    parser.add_argument('-o', '--out', type=str, required=True, help='output filename')
    return parser.parse_args()


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
        if not args.p and not args.i:
            git_logger.log_commits(client, repositories, csv_name)
        if args.p:
            git_logger.log_pull_requests(client, repositories, csv_name)
        if args.i:
            git_logger.log_issues(client, repositories, csv_name)


if __name__ == '__main__':
    main()
