import os
import pandas as pd


def data_cleaning(coins, input_directory, output_directory):
    """
    /coin_dfs directory 에서 {coin}.csv 파일을 읽어들여서
    time,open,high,low,close,accprice,volume -> 7개의 column으로 변경한다.

    또한 'time' column 을 기존 string 형식에서 datetime 형식으로 변경한 뒤,
    한국 시간(GMT+09:00) 기준으로 저장한다. time 기준 오름차순 정렬한다.

    Output
    ------
    '/coin_dfs_mod/{}.csv'.format(coin)
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for coin in coins:
        df = pd.read_csv('{}/{}.csv'.format(input_directory, coin))

        df['candleDateTime'] = pd.to_datetime(df.candleDateTimeKst) + pd.to_timedelta(9, 'h')

        df.drop(['code', 'candleDateTimeKst', 'unit', 'timestamp'], 1, inplace=True)
        df.rename(columns={'candleDateTime': 'time', 'candleAccTradeVolume': 'volume',
                           'highPrice': 'high', 'lowPrice': 'low', 'openingPrice': 'open',
                           'tradePrice': 'close', 'candleAccTradePrice': 'accprice'}, inplace=True)

        df = df[['time', 'open', 'high', 'low', 'close',  'accprice', 'volume']]

        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)

        df.to_csv('{}/{}.csv'.format(output_directory, coin))


def compile_data(dropna=False):
    """
    /coin_dfs_mod directory 에서 모든 {coin}.csv 파일을 읽어들여서
    각각의 파일에서 'close' column만 뽑아서 하나의 KRW_Market_joined_closes.csv 파일에 저장한다.
    dropna=True인 경우 nan 값을 버린다.

    Output
    ------
    KRW_Market_joined_closes.csv
    """

    main_df = pd.DataFrame()

    file_list = os.listdir('coin_dfs_mod')
    coins = list(x[:-4] for x in file_list)

    print(coins)

    for count, coin in enumerate(coins):
        df = pd.read_csv('coin_dfs_mod/{}.csv'.format(coin))

        df.rename(columns={'close': coin}, inplace=True)
        df.drop(['open', 'high', 'low', 'accprice', 'volume'], 1, inplace=True)
        df.set_index('time', inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        # remove duplicated index (because of bug in pandas.join)
        # https://stackoverflow.com/questions/13035764/remove-rows-with-duplicate-indices-pandas-dataframe-and-timeseries
        main_df = main_df[~main_df.index.duplicated(keep='first')]

    if dropna:
        main_df.dropna(inplace=True)
        main_df.to_csv('KRW_Market_joined_closes(dropna).csv')
    else:
        main_df.to_csv('KRW_Market_joined_closes.csv')
