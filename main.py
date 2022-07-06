import argparse
import git_logger


def parse_args():
    parser = argparse.ArgumentParser()
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
        git_logger.log_repositories(client=client, repositories=repositories, csv_name=csv_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
