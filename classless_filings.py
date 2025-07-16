
import numpy as np
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Callable, Optional, Union
import pandas as pd
import requests
import time
import json
from openpyxl import Workbook
from rapidfuzz import process, fuzz
pd.options.mode.copy_on_write = True
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Allow wide output
pd.set_option('display.max_colwidth', None)  # Show full column content
path_to_CIK_dict = "C:\\Users\\josep\\OneDrive\\Desktop\\Coding_env\\FinancialProject\\CIK_Keys.json"

def fetch_sec(ticker):
	# Define the headers
	ticker = ticker.upper()
	headers = {
		'User-Agent': 'Joseph Kiley (joseph13285@gmail.com)',
		'Accept-Encoding': 'gzip, deflate',
		'Host': 'data.sec.gov'
	}
	with open(path_to_CIK_dict, 'r') as f:
		data = json.load(f)
	if ticker.upper() in data:
		CIK = data[ticker]

	# Else if CIK is not found in the dictionary	
	else:
		# init_response = requests.get(f'https://efts.sec.gov/LATEST/search-index?keysTyped={self.ticker}', headers = headers)
		driver = webdriver.Chrome()
		response = f'https://efts.sec.gov/LATEST/search-index?keysTyped={ticker}'
		driver.get(response)
		source = driver.page_source
		parsed_json = json.loads(BeautifulSoup(source, 'lxml').find('pre').get_text(strip=True))
		driver.quit()
		try:
			first_hit = parsed_json['hits']['hits'][0]
			CIK = first_hit['_id']
		except IndexError:
			print('Invalid Ticker: Please Check Ticker')
			driver.quit()
			return None
		while len(CIK) < 10:
			CIK = "0" + CIK
		
		data[ticker] = CIK
		with open(path_to_CIK_dict, 'w') as f:
			json.dump(data, f, indent=4, sort_keys=True)
	response = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json', headers=headers)
	if response.status_code != 200:
		print("Invalid CIK")

		return None

	json_response: Dict[str, Any] = response.json()
	df = pd.DataFrame(
		data=[
			[
				ticker,
				fact,
				item.get('val'),
				re.sub('[^0-9]', '', item.get('frame', '')), # We dont even need regex any more
				item.get('filed')
			]
			for acc_conv in json_response['facts']
			for fact in json_response['facts'][acc_conv]
			for unit in json_response['facts'][acc_conv][fact]['units']
			for item in json_response['facts'][acc_conv][fact]['units'][unit]
			if item.get('frame') 
		],
		columns=['ticker', 'label', 'value', 'Frame', 'date']
	)
	# all balance sheet info ends with I
	df['Frame'] = df['Frame'].astype(float)       
	df['Frame'] = np.where(df['Frame'] > 9999, df['Frame'] / 10, df['Frame'])
	return df

	# self.df = self.df[self.df['Frame'].apply(lambda x: x.is_integer() == False)] # Quarterly Values Only filter
	# self.df = self.df[self.df['Frame'].apply(lambda x: x.is_integer() == True)] # Annual Values Only filter
	
print(fetch_sec('aapl'))