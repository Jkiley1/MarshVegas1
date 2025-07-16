from __future__ import annotations


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

class FinancialReports():
	"""Notes
	Below is a sample of the JSON response from the SEC API.
{
	"cik": 1050446,
	"entityName": "MICROSTRATEGY INCORPORATED",
	"facts": {
		"us-gaap": {
			"AccountsPayableAndAccruedLiabilitiesCurrent": {
				"label": "Accounts Payable and Accrued Liabilities, Current",
				"description": "Sum of the carrying values as of the balance sheet date of obligations...",
				"units": {
					"USD": [
						{
							"end": "2010-12-31",
							"val": 36683000,
							"accn": "0001193125-12-067605",
							"fy": 2011,
							"fp": "FY",
							"form": "10-K",
							"filed": "2012-02-17",
							"frame": "CY2010Q4I"
						},
						{
							"end": "2010-12-31",
							"val": 36683000,
							"accn": "0001193125-11-294608",
							"fy": 2011,
							"fp": "Q3",
							"form": "10-Q",
							"filed": "2011-11-03"
						},
					]
				}
			}
		}
	}
	"""
	# We'll create the parent nodes here: If the parent nodes are found in 'label' drop them
	BALANCESHEET = ()
	INCOMESTATEMENT = ('AssetsCurrent') 
	def __init__(self, ticker: str, annual: bool = False):
		self.ticker = ticker.upper()
		self.annual = False
		self.CF_df = None
		self.BS_df = None
		self.IS_df = None
		self.df = None
		self._path_to_CIK_dict = "C:\\Users\\josep\\OneDrive\\Desktop\\Coding_env\\FinancialProject\\CIK_Keys.json"
		
		
		
		self.BS = [
		'CashAndCashEquivalentsAtCarryingValue',
		'InventoryNet',
		['AccountsReceivableNetCurrent', 'ReceivablesNetCurrent'],
		'PrepaidExpenseAndOtherAssetsCurrent',
		'OtherAssetsCurrent',
		'AssetsCurrent',
		'IntangibleAssetsNetExcludingGoodwill', 
		'Goodwill',
		'PropertyPlantAndEquipmentNet', 
		'OperatingLeaseRightOfUseAsset',
		'OtherAssetsNonCurrent',
		'Assets',

		'AccountsPayableCurrent',
		'AccruedLiabilitiesCurrent',
		'InterestPayableCurrent',
		'DividendsPayableCurrent',
		'DebtCurrent',
		'LongTermDebtCurrent',
		'LiabilitiesCurrent',
		'LongTermDebt',
		'MarketableSecuritiesNoncurrent',
		'LiabilitiesNoncurrent',

		'CommonStockSharesIssued',
		'RetainedEarningsAccumulatedDeficit',
		'CommonStockValue',
		'TreasuryStockValue',
		'StockholdersEquity'
		]
								
		self.IS = [
		['RegulatedAndUnregulatedOperatingRevenue',
		'Revenue', 
		'SalesRevenueNet',
		'RevenueFromContractWithCustomerExcludingAssessedTax'],
		['CostsAndExpenses',
		'CostOfSold',
		'CostOfGoodsAndServicesSold',
		'CostOfGoodsSold',
		'OperatingExpenses'],		
		'ResearchDevelopmentAndRelatedExpenses',
		'SellingGeneralAndAdministrativeExpense',
		'InterestIncomeExpenseNet'
		]
		
		self.CF = [
		'NetCashProvidedByUsedInDiscontinuedOperations',
		'NetCashProvidedByUsedInInvestingActivities',
		'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
		'NetCashProvidedByUsedInOperatingActivities',
		'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
		'NetCashProvidedByUsedInFinancingActivities',
		'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations',
								
		'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',
		'IncreaseDecreaseInAccountsPayable',
		'IncreaseDecreaseInContractWithCustomerLiability',
		'IncreaseDecreaseInDeferredRevenue', 
		'IncreaseDecreaseInInventories',
		'IncreaseDecreaseInOtherOperatingAssets',
		'IncreaseDecreaseInOtherOperatingLiabilities',
		'IncreaseDecreaseInOtherReceivables'
		]

		self.divisors = [{
			'Interest Coverage': ('Earnings', 'InterestExpense'), # Label: (Numerator: Denominator)
			'Fake': ('dividendsPaidToMyselfDuh', 'InterestExpense')
		}]
	


	def _retrieval(self):
		# Define the headers
		headers = {
			'User-Agent': 'Joseph Kiley (joseph13285@gmail.com)',
			'Accept-Encoding': 'gzip, deflate',
			'Host': 'data.sec.gov'
		}
		with open(self._path_to_CIK_dict, 'r') as f:
			data = json.load(f)

		if self.ticker.upper() in data:
			CIK = data[self.ticker]

	# handle the case where the CIK is not found
		else:
			# init_response = requests.get(f'https://efts.sec.gov/LATEST/search-index?keysTyped={self.ticker}', headers = headers)
			driver = webdriver.Chrome()
			response = f'https://efts.sec.gov/LATEST/search-index?keysTyped={self.ticker}'
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
			
			data[self.ticker] = CIK

			with open(self._path_to_CIK_dict, 'w') as f:
				json.dump(data, f, indent=4, sort_keys=True)

		response = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json', headers=headers)

		if response.status_code != 200:
			print("Invalid CIK")
			return None
		return response.json()  

	def json_to_df(self):
		json_response: Dict[str, Any] = self._retrieval()
		df = pd.DataFrame(
			data=[
				[
					self.ticker,
					fact,
					item.get('val'),
					re.sub('[^0-9]', '', item.get('frame', '')), 
					item.get('filed')
				]
				for acc_conv in json_response['facts']
				for fact in json_response['facts'][acc_conv]
				for unit in json_response['facts'][acc_conv][fact]['units']
				for item in json_response['facts'][acc_conv][fact]['units'][unit]
				if item.get('frame') 
			],
			columns=['ticker', 'label', 'value', 'frame', 'date']
		)

		# all balance sheet info ends with I


		# bs_df = df[~df['frame'].str.endswith("I")]
		# is_df = df[df['frame'].str.endswith("I")]
		
		# bs_df['frame'] = bs_df['frame'].apply(lambda x: re.sub('[^0-9]', '', x))
		# is_df['frame'] = is_df['frame'].apply(lambda x: re.sub('[^0-9]', '', x))
		
		
		df['frame'] = df['frame'].astype(float)
		df['frame'] = np.where(df['frame'] > 9999, df['frame'] / 10, df['frame'])

		self.df = self.df[self.df['Frame'].apply(lambda x: x.is_integer() == True)] # Annual Values Only filter
		# self.df = self.df[self.df['Frame'].apply(lambda x: x.is_integer() == False)] # Quarterly Values Only filter
		df = df[df['frame'] >= 2020]
		return df

		
	def map_financial_terms(self):
		df = self.json_to_df()
		
		"""_summary_
		This function tries to map the financial terms defined in the dictionaries above to the terms from the SEC. 
		The goal is to have an end result of a dictionary of dictionaries, 
		where the key is the period and the value is a dictionary of the financial terms and their values.
			For example: {'2020': {'Revenue': 1000, 'COGS': 500, 'Net Income': 500}}, {'2021': {'Revenue': 2000, 'COGS': 1000, 'Net Income': 1000}}, etc. 
		
		"""
		mapped_BS = []
		mapped_IS = []
		mapped_CF = []

		NONO_BS = []
		NONO_IS = []
		NONO_CF = []
		mapped_divisors = []
		cutoff = 80
		# for _dict in self.divisors:
		#     for ratio in _dict.keys():
		#         try:
		#             mapped_divisors.append(
		#             [ratio, # Title
		#             (process.extractOne(_dict[ratio][0], df, score_cutoff=cutoff)[0], # Numerator
		#             (process.extractOne(_dict[ratio][1], df, score_cutoff=cutoff)[0]))] # Denominator
		#             )
		#         except TypeError:
		#             pass
		for _key in range(len(self.BS)):
			if isinstance(self.BS[_key], list):
				best_match = None
				best_score = 0
				for subkey in self.BS[_key]:
					match = process.extractOne(subkey, df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)
					if match and match[1] > best_score:
						best_score = match[1]
						best_match = match[0]
				   
				if best_match:
					if best_match not in NONO_BS:
						mapped_BS.append(best_match)
						NONO_BS.append(best_match)
			   
			else: 
				try:
					if (matched_item := process.extractOne(self.BS[_key], df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)[0]) not in NONO_BS: 
						mapped_BS.append(matched_item)
				except TypeError:
					pass

		for _key in range(len(self.IS)):
			if isinstance(self.IS[_key], list):
				best_match = None
				best_score = 0
				for subkey in self.IS[_key]:
					match = process.extractOne(subkey, df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)
					if match and match[1] > best_score:
						best_score = match[1]
						best_match = match[0]
				   
				if best_match:
					if best_match not in NONO_IS:
						mapped_IS.append(best_match)
						NONO_IS.append(best_match)
			   
			else: 
				try: 
					if (matched_item := process.extractOne(self.IS[_key], df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)[0]) not in NONO_IS:
						mapped_IS.append(matched_item)
				except TypeError:
					pass
		for _key in range(len(self.CF)):
			if isinstance(self.CF[_key], list):
				best_match = None
				best_score = 0
				for subkey in self.CF[_key]:
					match = process.extractOne(subkey, df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)
					if match and match[1] > best_score:
						best_score = match[1]
						best_match = match[0]
				    
				if best_match:
					if best_match not in NONO_CF:
						mapped_CF.append(best_match)
						NONO_CF.append(best_match)
			   
			else: 
				try: 
					if (matched_item := process.extractOne(self.CF[_key], df.loc[df['frame'] > df['frame'].max() - 1, 'label'].unique(), scorer=fuzz.token_sort_ratio, score_cutoff=cutoff)[0]) not in NONO_CF:
						mapped_CF.append(matched_item)
				except TypeError:
					pass
		
		self.BS_df = df.loc[df['label'].isin(mapped_BS)]
		self.BS_df = self.BS_df.pivot(index='label', columns='frame', values='value')
		self.BS_df = self.BS_df.reindex(mapped_BS)
		
		self.IS_df = df.loc[df['label'].isin(mapped_IS)]
		self.IS_df = self.IS_df.pivot(index='label', columns='frame', values='value')
		self.IS_df = self.IS_df.reindex(mapped_IS)
		
		self.CF_df = df.loc[df['label'].isin(mapped_CF)]
		self.CF_df = self.CF_df.pivot(index='label', columns='frame', values='value')
		self.CF_df = self.CF_df.reindex(mapped_CF)


		print(self.IS_df)
		# BS_threshold = self.BS_df.shape[0] // 2
		# IS_threshold = self.IS_df.shape[0] // 2
		# CF_threshold = self.CF_df.shape[0] // 2
		
		# self.BS_df = self.BS_df.dropna(axis=1, thresh=BS_threshold)
		# self.IS_df = self.IS_df.dropna(axis=1, thresh=IS_threshold)
		# self.CF_df = self.CF_df.dropna(axis=1, thresh=CF_threshold)

		# self.BS_df.to_csv('Balance.csv')
		# self.IS_df.to_csv('Income.csv')
		# self.CF_df.to_csv('Cash.csv')

		
FinancialReports('aapl').map_financial_terms()

		
	
# FINRA API
# LIBROSA
"""
G
U
I
L
T
Yours Truly
"""