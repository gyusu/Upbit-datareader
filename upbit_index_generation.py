import os
import numpy as np
import pandas as pd


class IndexGenerator:
    """
        Input csv format
        -------------
        time,open,high,low,close,accprice,volume
        2017-11-08 04:10:00,8176000.0,8176000.0,8176000.0,8176000.0,7434146.1432,0.90926445
    """
    def __init__(self, coins: list, input_dir):
        self.coins = coins
        self.input_dir = input_dir
        self.studies = ['simple_ma', 'weighted_ma', 'exp_ma', 'momentum', 'stochastic_k',
                        'stochastic_d', 'rsi', 'macd', 'larry_williams_r', 'ad_oscillator', 'cci' ]

    def drop_studies(self, drop_list: list):
        for i, study in enumerate(self.studies):
            if study in drop_list:
                del self.studies[i]

    def simple_ma(self, data,n):
        """
        Simple n - Moving Average

        Input
        -----
        data : 1-D array. eg. [1000000, 1100000, ...]

        Output
        ------
        shape(-1,1) n - Moving Averages array. eg. [[NaN]... [1000000], [1100000]]
        Note!!! First n-1 values are NaN
        """
        data_df = pd.DataFrame(data)
        output_df = data_df.rolling(window=n, min_periods=n).mean()
        return output_df.values

    def weighted_ma(self, data,n):
        """
        Linear weighted n - Moving Average

        Input
        -----
        data : 1-D array. eg. [1000000, 1100000, ...]

        Output
        ------
        shape(-1,1) Linear weighted n - Moving Averages array. eg. [[NaN]... [1000000], [1100000]]
        Note!!! First n-1 values are NaN
        """
        data_df = pd.DataFrame(data)

        sum_w = sum(range(1,n+1))
        wts = list(w/sum_w for w in range(1,n+1))

        # def f(w):
        #     def g(x):
        #         return (w*x).sum()
        #     return g
        #
        # and then.. -> apply(f(wts)) is OK..
        # but i would use below one.

        def f(x):
            return (wts*x).sum()

        output_df = data_df.rolling(window=n, min_periods=n).apply(f)
        return output_df.values

    def exp_ma(self, data,n):
        """
        Exponential n - Moving Average

        계산식 : ema = 전일ema + k * (금일 종가 - 전일ema)
        ( k = 2 / (n+1) )

        Input
        -----
        data : 1-D array. eg. [1000000, 1100000, ...]

        Output
        ------
        shape(-1,1), Exponential n - Moving Averages array. eg. [[NaN]... [1000000], [1100000]]
        """
        ema = []
        ema.append(data[0])

        k = 2 / (n+1)

        for i in range(1, len(data)):
            res = ema[i-1] + k*(data[i]- ema[i-1])
            ema.append(res)

        ema = np.array(ema)

        return ema.reshape((-1,1))

    def momentum(self, data, n):
        output = []
        for i in range(n):
            output.append(float('nan'))

        for i in range(n, len(data)):
            output.append(data[i]-data[i-n])

        output = np.array(output)

        return output.reshape((-1,1))

    def stochastic_k(self, data, n):
        """
        Input
        -----
        data : high, low, close in shape(3,None)
        eg. stochastic_K([df.high.values,df.low.values,df.close.values], 5)

        Output
        ------
        (오늘 종가 - n 일 중 최저가) / (n일 중 최고가 - n일 중 최저가)

        """

        output = []
        for i in range(n):
            output.append(float('nan'))

        for i in range(n, len(data[0])):
            numerator = data[2][i] - min(data[1][i-n:i+1])
            denominator = max(data[0][i-n:i+1]) - min(data[1][i-n:i+1])
            output.append(numerator/denominator)

        output = np.array(output)

        return output.reshape((-1,1))

    def stochastic_d(self, data, n, m):
        """
        stochastic_d는 stochastic_k의 n-MA 이다.
        """
        s_k = self.stochastic_k(data,n)

        s_k = s_k.reshape(-1)

        output = self.simple_ma(s_k, m)

        return output

    def rsi(self, data, n):
        """
        Input
        -----
        data : close

        Output
        ------
        [n일간의 주가 상승폭 합계 / (n일간의 주가상승폭 합계 + n일간의 주가 하락폭 합계)〕× 100

        * 여기서 계산하는 RSI는 wilder's smoothing을 적용하지 않은 값이다.
        """

        data_df = pd.DataFrame(data)

        def f(x):
            delta_up = delta_down = 0
            for i in range(1,len(x)):
                delta = x[i] - x[i-1]
                if delta > 0:
                    delta_up += delta
                else :
                    delta_down += -delta
            return delta_up / (delta_up + delta_down) * 100

        output_df = data_df.rolling(window=n, min_periods=n).apply(f)
        return output_df.values

    def macd(self, data, fast_n, slow_n, signal_n):
        """
        Input
        -----
        data : close
        ...

        Formula
        -------
        macd_val = fast ema - slow_ema
        signal_ma = macd_val's ema

        Output
        ------
        diff = macd_val - signal_ma
        """
        fast_ma = self.exp_ma(data, fast_n)
        slow_ma = self.exp_ma(data, slow_n)

        macd_val = fast_ma - slow_ma
        signal_ma = self.exp_ma(macd_val, signal_n)
        diff = macd_val - signal_ma

        return diff

    def larry_williams_r(self, data, n):

        """
        Input
        -----
        data : high, low, close in shape(3,None)

        Output
        ------
        (기간 중 최고가 - 오늘 종가) / (기간중 최고가 - 기간중 최저가)*100
        """
        output = []
        for i in range(n):
            output.append(float('nan'))

        for i in range(n, len(data[0])):
            numerator = max(data[0][i - n:i + 1]) - data[2][i]
            denominator = max(data[0][i - n:i + 1]) - min(data[1][i - n:i + 1])
            output.append(numerator / denominator * 100)

        output = np.array(output)

        return output.reshape((-1,1))

    def ad_oscillator(self, data, n):

        """
        Input
        -----
        data : high, low, close in shape(3,None)

        Output
        ------
        (오늘 최고가 - 어제 종가) / (오늘 최고가 - 오늘 최저가)
        """
        pass

    def cci(self, data,n):

        """
        Input
        -----
        data : high, low, close in shape(3,None)

        Formula
        -------
        m_t = 오늘의 high low close의 평균값
        sm_t = m_t의 n 이동평균
        d_t = (m_t - sm_t)의 절대값을 n 이동평균

        Output
        ------
        cci = (m_t-sm_t) / (0.015*d_t)
        """
        m_t = []
        for i in range(len(data[0])):
            m_t.append((data[0][i]+data[1][i]+data[2][i])/3)



        sm_t = self.simple_ma(m_t, n)

        m_t = np.array(m_t)
        m_t = m_t.reshape((-1, 1))

        d_t = []
        for i in range(len(data[0])):
            d_t.append(abs(m_t[i] - sm_t[i]))

        d_t = self.simple_ma(d_t, n)

        output = []

        for i in range(2*n):
            output.append(float('nan'))

        for i in range(2*n,len(data[0])):
            numerator = m_t[i] - sm_t[i]
            denominator = 0.015*d_t[i]
            output.append(numerator / denominator)

        output = np.array(output)

        return output.reshape((-1,1))

    def to_csv(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for coin in self.coins:
            input_df = pd.read_csv('{}/{}.csv'.format(self.input_dir,coin))
            output_df = pd.DataFrame()

            output_df['time'] = input_df.time.values
            output_df['close'] = input_df.close.values
            output_df['simple_ma'] = self.simple_ma(input_df.close.values, 10).reshape(-1)
            output_df['weighted_ma'] = self.weighted_ma(input_df.close.values, 10).reshape(-1)
            output_df['momentum'] = self.momentum(input_df.close.values, 10).reshape(-1)
            output_df['stochastic_k'] = self.stochastic_k([input_df.high.values,input_df.low.values,input_df.close.values], 10).reshape(-1)
            output_df['stochastic_d'] = self.stochastic_d([input_df.high.values,input_df.low.values,input_df.close.values], 10, 5).reshape(-1)
            output_df['rsi'] = self.rsi(input_df.close.values, 10).reshape(-1)
            output_df['macd'] = self.macd(input_df.close.values, 12,26,9).reshape(-1)
            output_df['larry_williams_r'] = self.larry_williams_r([input_df.high.values,input_df.low.values,input_df.close.values], 10).reshape(-1)
            output_df['cci'] = self.cci([input_df.high.values,input_df.low.values,input_df.close.values], 10).reshape(-1)

            output_df['volume'] = input_df.volume.values

            output_df.dropna(inplace=True)
            output_df.set_index('time', inplace=True)

            output_df.to_csv('{}/{}.csv'.format(output_dir,coin))
