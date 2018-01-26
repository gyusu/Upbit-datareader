import pandas as pd
import numpy as np
import tensorflow as tf
import requests
import ast
import datetime
import os
import sys

'''
업비트에서 이더리움 시세 받아오는 프로그램이다.
https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/10?code=CRIX.UPBIT.KRW-ETH&count=200&to=2017-12-27%2005:10:00
'''

# input : data 개수. 현재 시간까지 분단위로 n개 데이터 받아서 cvs로 저장. raw_data임.
def fecth_data(n):

    headers = {
        "User-Agent": "User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
    }

    today = datetime.datetime.today() - datetime.timedelta(hours=9)

    data_list=[]
    end_time = today
    for i in range(int(n/200)):
        end_time_str = datetime.datetime.strftime(end_time, "%Y-%m-%d%%20%H:%M:00")
        url = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/1?code=CRIX.UPBIT.KRW-ETH&count=200&to={}'.format(end_time_str)
        req = requests.get(url, headers=headers)
        raw_data = req.text
        raw_data = raw_data.replace('null', '0')
        data = ast.literal_eval(raw_data)
        data_list.append(data)
        end_time = end_time - datetime.timedelta(minutes=200)

    data_list = np.array(data_list).reshape(-1,)
    df = pd.DataFrame(data_list.tolist())
    df.set_index('candleDateTimeKst',inplace=True)
    df.sort_index(inplace=True)
    df.to_csv('ETH.csv')

def clean_data():

    if not os.path.isdir('clean'):
        os.mkdir('clean')

    df = pd.read_csv('ETH.csv')
    df.drop(['candleDateTime','code','timestamp','unit'], axis=1,inplace=True)
    df.rename(columns={'candleDateTimeKst': 'Time', 'openingPrice': 'Open',
                       'highPrice':'High', 'lowPrice':'Low', 'tradePrice':'Close',
                       'candleAccTradeVolume':'Volume', 'candleAccTradePrice':'Accprice'}, inplace=True)
    df.set_index('Time', inplace=True)
    df.to_csv('clean/ETH.csv')

if __name__ == '__main__':
    fecth_data(100000)
    clean_data()





