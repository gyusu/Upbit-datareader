import requests
import ast
import os
import pandas as pd
import datetime as dt
import upbit_coins

"""
[Upbit Unofficial API Format]
    https://crix-api-endpoint.upbit.com/v1/crix/candles/기간타입/기간?code=CRIX.UPBIT.마켓-암호화폐기호&count=시세데이터수&to=최종시세데이터일시
    기간타입: minutes, days, weeks, months (hours는 없으며 minutes로 대체)
    기간: 1, 3, 5, 10, 15, 30, 60, 240 (기간타입 minutes만 해당)
    마켓: KRW, BTC, ETH, USDT
    암호화폐기호: BTC, ETH, XRP, STEEM, SBD 등 각 마켓의 지원 암호화폐
    시세데이터수: 1(기본값), 2, 3, 4 등 원하는 시세 데이터 수 (최종시세데이터일시 기준)
    최종시세데이터일시: 조회를 원하는 최종 시세 데이터 일시 (생략시 가장 최근 시세 데이터 일시, UTC 기준)
                     (형식 : 2017-12-27%2005:10:00)
                 
[Raw Data Format]
    {"code":"CRIX.UPBIT.KRW-BTC",
    "candleDateTime":"2018-01-11T12:45:00+00:00",
    "candleDateTimeKst":"2018-01-11T21:45:00+09:00",
    "openingPrice":19351000.00000000,
    "highPrice":19630000.00000000,
    "lowPrice":19333000.00000000,
    "tradePrice":19452000.0,
    "candleAccTradeVolume":291.10165834,
    "candleAccTradePrice":5680151681.252510000,
    "timestamp":1515675220567,
    "unit":15}

데이터가 완전하지 않으니 적용하기 전에 nan 데이터나 제공되지 않은 데이터가 있음을 유의
중간중간 날짜가 빠져있는 경우도 존재함

* tradePrice가 closePrice를 의미함
"""

# 데이터 가져오는 도중에 today가 변경되지 않도록 하기 위해 전역으로 초기에 호출
today = dt.datetime.today() - dt.timedelta(hours=9)
today -= dt.timedelta(seconds=today.second)


def make_url(code, **kwargs):
	"""
	Parameters
	----------
	time : 'minutes', 'days', 'weeks', 'months' (minutes 사용 권장)
	period : time 이 minute인 경우에만 사용가능 (eg. 1, 3, 5, 10, 15, 30, 60, 240)
	market : Market Name (eg. "KRW", "BTC", "ETH", ...)
	count : endpoint 까지 몇 개의 데이터를 가져올 지를 의미
					하나의 url은 최대 200개 시점의 데이터를 가져올 수 있다.
	endpoint : 조회를 원하는 최종 데이터 시점.

	Returns
	-------
	string : url
	"""
	kwargs.setdefault('time', "minutes")
	kwargs.setdefault('period', 15)
	kwargs.setdefault('market', "KRW")
	kwargs.setdefault('count', 200)
	kwargs.setdefault('endpoint', today)
	if kwargs['count'] > 200:
		kwargs['count'] = 200

	kwargs['endpoint'] = kwargs['endpoint'].strftime('%Y-%m-%d%%20%H:%M:%S')

	url = "https://crix-api-endpoint.upbit.com/v1/crix/candles/{0}/{1}?code=CRIX.UPBIT.{2}-{3}&count={4}&to={5}".format(
		kwargs['time'], kwargs['period'], kwargs['market'], code, kwargs['count'], kwargs['endpoint'])

	return url


def get_data_from_upbit(**kwargs):
	"""
	현재시점(today())까지 count 개의 데이터를 upbit 에서 가져와서 .csv 파일로 저장하는 함수
	비공식 api 가 제공하는 데이터 형식을 가공하지 않고 그대로 저장한다.
	2017-09-30 이전에는 상장되지 않은 코인들이 많아 nan 처리 필요

	Parameters
	----------
	time : 'minutes', 'days', 'weeks', 'months' (minutes 사용 권장)
	period : time 이 minute 인 경우에만 사용가능 (eg. 1, 3, 5, 10, 15, 30, 60, 240)
	market : Market Name (eg. "KRW", "BTC", "ETH", ...)
	count : endpoint 까지 몇 개의 데이터를 가져올 지를 의미
					하나의 url은 최대 200개 시점의 데이터를 가져올 수 있다.

	Output
	------
	'/coin_dfs/{}.csv'.format(coin)

	Returns
	-------
	None
	"""
	kwargs.setdefault('time', "minutes")
	kwargs.setdefault('period', 15)
	kwargs.setdefault('market', "KRW")
	kwargs.setdefault('count', 100)
	kwargs.setdefault('coins', 'all')
	kwargs.setdefault('save_dirname', 'coin_dfs')

	# time_delta 는 분 단위로 계산
	time_delta = min(kwargs['count'], 200) * kwargs['period']

	if kwargs['time'] == 'days':
		time_delta *= 60 * 24

	# set header for avoiding 'forbidden 403 error'
	url_header = {'User-Agent': 'Mozilla/5.0', 'referer': "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"}

	if not os.path.exists(kwargs['save_dirname']):
		os.makedirs(kwargs['save_dirname'])

	if kwargs['coins'] == 'all':
		coins = upbit_coins.coin_list(kwargs['market'])
	else:
		coins = kwargs['coins']

	for coin in coins:
		# if not os.path.exists('coin_dfs/{}.csv'.format(coin)):
		success = False
		count = kwargs['count']
		tickers = []
		endpoint = today

		while count > 0:
			url = make_url(coin, count=count, endpoint=endpoint, period=kwargs['period'],
			               market=kwargs['market'], time=kwargs['time'])
			resp = requests.get(url, headers=url_header)

			# need to be improved...
			try:
				ticker_text = resp.text
				ticker_text = ticker_text.replace("null", "0")

				# list 안에 dictionary 가 있는 형식으로 받아진 데이터(문자열)를
				# 실제 python list, dictionary 형식에 맞게 저장한다.
				ticker = ast.literal_eval(ticker_text)
				tickers.extend(ticker)

				count -= 200
				endpoint -= dt.timedelta(minutes=time_delta)
				success = True

			except:
				print('Unable to get data : {}'.format(coin), end='\t')
				print('response = {}'.format(resp))
				success = False
				break

		if success:
			df = pd.DataFrame(tickers)
			df.set_index('candleDateTimeKst', inplace=True)
			df.to_csv('{}/{}.csv'.format(kwargs['save_dirname'], coin))
