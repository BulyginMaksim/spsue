import csv
import argparse
import pandas as pd
import numpy as np
import yfinance as yf
import yahoo_fin.stock_info as si

import app_logger

logger = app_logger.get_logger(__name__)

def get_ticker_info(ticker):
    info_keys = [
        'symbol',
        'shortName',
        'longName',
        'financialCurrency',
        'sector',
        'currency',
        'industry',
        'country',
        'market'
    ]
    return {key: ticker.info.get(key, None) for key in info_keys}


def parse_single_ticker(stock_name, period_months=24):
    ticker = yf.Ticker(stock_name)
    columns_drop = ['Volume', 'Dividends', 'Stock Splits']
    tmp = ticker.history(period=f'{period_months}mo').reset_index().drop(columns=columns_drop)
    for key, value in get_ticker_info(ticker).items():
        tmp[key] = value
    return tmp


def write_data_to_csv(data: pd.DataFrame, csv_name='snp500.csv', create_csv=False):
    MODE = 'w' if create_csv else 'a'
    with open(csv_name, MODE, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        if create_csv:
            writer.writerow(data.T.index.tolist())
        for _, row in data.T.to_dict().items():
            writer.writerow(list(row.values()))


def parse_all_tickers(stock_names_list: list, csv_name='snp500.csv', limit=float('inf')):
    if not stock_names_list:
        logger.info("Given stock names list is empty.")
        return
    if limit < float('inf'):
        logger.info("")
        stock_names_list = np.random.choice(stock_names_list, size=limit)
    logger.info(f"Parsing 1/{len(stock_names_list)} stock.")
    ticker_data = parse_single_ticker(stock_names_list[0])
    write_data_to_csv(ticker_data, csv_name=csv_name, create_csv=True)
    logger.info(f"Parsed 1/{len(stock_names_list)} stock.")
    for i, stock_name in enumerate(stock_names_list[1:]):
        logger.info(f"Parsing {i + 2}/{len(stock_names_list)} stock.")
        ticker_data = parse_single_ticker(stock_name)
        write_data_to_csv(ticker_data, csv_name=csv_name)
        logger.info(f"Parsed {i + 2}/{len(stock_names_list)} stock.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv_name', dest='csv_name', type=str, default='snp500.csv', help='Csv table name to same parsed stock data.')
    parser.add_argument('-limit', dest='limit',  type=int, default=float('inf'), help='Number of stocks to be parsed')
    args = parser.parse_args()
    snp500_stock_names = si.tickers_sp500()
    logger.info("Started parsing S&P 500 stock data.")
    parse_all_tickers(snp500_stock_names, csv_name=args.csv_name, limit=args.limit)
    logger.info("Ended parsing S&P 500 stock data.")


if __name__ == '__main__':
    main()

