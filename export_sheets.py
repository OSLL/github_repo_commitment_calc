import pygsheets
import pandas as pd
import argparse


INT_MASS = [{
    "one": 1,
    "two": 2,
    "what?": 3
}]
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', type=str, required=True, help='Specify path to output csv file')
    parser.add_argument('--google_token', type=str, required=False, help='Specify path to google token file')
    parser.add_argument('--table_id', type=str, required=False, help='Specify Google sheet document id (can find in url)')
    parser.add_argument('--sheet_id', type=str, required=False, help='Specify title for a sheet in a document in which data will be printed')
    args = parser.parse_args()
    return args

def write_data_to_table(csv_path, google_token, table_id, sheet_id):
    if google_token and sheet_id and table_id :
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    try:
        sh.worksheets('title', sheet_id)
    except:
        sh.add_worksheet(sheet_id)

    wk_content = sh.worksheet_by_title(sheet_id)

    if csv_path:
        df = pd.read_csv(csv_path, delimiter=',', encoding='cp1251')
    else:
        df = pd.DataFrame(INT_MASS)

    # Очистка существующих данных
    wk_content.clear()

    # Запись новых данных
    wk_content.set_dataframe(df, 'A1', copy_head=True)


def main():
    args = arg_parser()
    write_data_to_table(args.csv_path, args.google_token, args.table_id, args.sheet_id)


if __name__ == "__main__":
    main()