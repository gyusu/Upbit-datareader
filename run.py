import upbit_data_fetch
import upbit_data_manipulation
import upbit_index_generation
import datetime

# This is an example code

# make today's directory name
today = datetime.date.today()
today = today.strftime('%y%m%d')
dir_name = 'run'+today

# for 'BTC' coin, fetch 10000 data points, by 1 minute, to dir_name directory
upbit_data_fetch.get_data_from_upbit(coins=['BTC'], count=10000, period=1, save_dirname=dir_name)

# clean up data, for 'BTC' coin which we have .csv file, from dir_name, to dir_name/cleaned
upbit_data_manipulation.data_cleaning(['BTC'], dir_name, dir_name+'/cleaned')

# generate indices and save it
ig = upbit_index_generation.IndexGenerator(['BTC'], dir_name+'/cleaned')
ig.drop_studies(['ad_oscillator'])
ig.to_csv(dir_name+'/studies')

