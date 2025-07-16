import asyncio
import requests
import os
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import concurrent.futures
from playwright.async_api import async_playwright
import datetime
import zipfile
from io import BytesIO

"""we may need a class to handle these objects when we are done with them"""

        
def treasuries(year: str|int = datetime.date.today().year, month: str|int = "", real_rates: bool = False):
    year = str(year)
    month = str(month)

    if month:
        if len(month) < 2:
            month = "0" + month
    date = None
    one_month = None
    three_month = None
    six_month = None
    two = None
    five = None
    seven = None
    ten = None
    twenty = None
    thirty = None
    
    # current month filter
    """
    Args:
        year : year of 
    """
    interest_rate_data_url = f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value={year+month}'
    if real_rates:
        """Call real_rates function defined within here"""
        
    data = []
    
    response = requests.get(url=interest_rate_data_url)
    soup = BeautifulSoup(response.content, 'lxml')
    rows = soup.find_all('tr')
    for row in rows:
        date = row.select_one('.views-field.views-field-field-tdr-date')
        one_month = row.find('td', headers='view-field-bc-1month-table-column')
        three_month = row.find('td', headers = 'view-field-bc-3month-table-column')
        six_month = row.find('td', headers = 'views-field views-field-field-bc-6month')
        two = row.find('td', headers = 'view-field-bc-2year-table-column')
        five = row.find('td', headers = 'views-field views-field-field-bc-5year')
        seven = row.find('td', headers = 'views-field views-field-field-bc-7year')
        ten = row.find('td', headers = 'views-field-field-bc-10year-table-column')
        twenty = row.find('td', headers = 'view-field-bc-20year-table-column')
        thirty = row.find('td', headers = 'view-field-bc-30year-table-column')
        print(type(date),date)
        print(type(one_month),one_month)
        print(type(three_month),three_month)
        print(type(six_month),six_month)
        print(type(two),two)
        print(type(five),five)
        print(type(seven),seven)
        print(type(ten),ten)
        print(type(twenty),twenty)
        print(type(thirty),thirty)
        data.append([date, one_month, three_month, six_month, two, five, seven, ten, twenty, thirty])
    """<class 'bs4.element.Tag'> <td class="views-field views-field-field-tdr-date" headers="view-field-tdr-date-table-column"><time class="datetime" datetime="2025-07-14T12:00:00Z">07/14/2025</time>
</td>
<class 'bs4.element.Tag'> <td class="bc1month views-field views-field-field-bc-1month" headers="view-field-bc-1month-table-column">4.37          </td>
<class 'bs4.element.Tag'> <td class="bc3month views-field views-field-field-bc-3month" headers="view-field-bc-3month-table-column">4.42          </td>
<class 'NoneType'> None
<class 'bs4.element.Tag'> <td class="views-field views-field-field-bc-2year" headers="view-field-bc-2year-table-column">3.90          </td>
<class 'NoneType'> None
<class 'NoneType'> None
<class 'NoneType'> None
<class 'bs4.element.Tag'> <td class="bc20year views-field views-field-field-bc-20year" headers="view-field-bc-20year-table-column">4.97          </td>
<class 'bs4.element.Tag'> <td class="bc30year views-field views-field-field-bc-30year" headers="view-field-bc-30year-table-column">4.97          </td>"""
    def real_rates():
        interest_rate_data_url = f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value={year}'
    
treasuries()
def url_to_df(url: str) -> pd.DataFrame:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(BytesIO(response.content))
def entire_vix_process() -> pd.DataFrame:
    async def fetch_vix_futures( cutoff_year: int = None, cutoff_month: int = 1, cutoff_day: int = 1) -> None:
        if cutoff_year:
            if isinstance(cutoff_year, int) or cutoff_year.isdigit():
                cutoff_year = int(cutoff_year)
            else:
                raise TypeError(f"Argument expected int, got {cutoff_year} of type {type(cutoff_year).__name__!r}")
        if isinstance(cutoff_month, int) or cutoff_month.isdigit():
            cutoff_month = int(cutoff_month)
        else:
            raise TypeError(f"Argument expected int, got {cutoff_month} of type {type(cutoff_month).__name__!r}")
        if isinstance(cutoff_day, int) or cutoff_day.isdigit():
            cutoff_day = int(cutoff_day)
        else:
            raise TypeError(f"Argument expected int, got {cutoff_day} of type {type(cutoff_day).__name__!r}")
        async with async_playwright() as p:
            # Choose browser: chromium, firefox, or webkit
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://www.cboe.com/us/futures/market_statistics/historical_data/")
            links = page.locator('a', has_text=r"VXT/")
            count = await links.count()
            hrefs = [await links.nth(i).get_attribute("href") for i in range(count)]
            hrefs = [(i[-14:-4].replace('-',''), i) for i in hrefs]
            hrefs = [(datetime.date(int(one[0:4]), int(one[4:6]), int(one[6:])), two) for one, two in hrefs]
            if cutoff_year:
                slicer = datetime.date(cutoff_year, cutoff_month, cutoff_day)
            else: 
                slicer = datetime.date.today()
            hrefs.append((slicer, None))
            hrefs = sorted(hrefs)
            hrefs = [i for _, i in hrefs if slicer < _]
            hrefs = hrefs[:5]
            await browser.close()

        def vix_df():
            dfs = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
                for df_ in pool.map(url_to_df, hrefs):
                    dfs.append(df_)
            return dfs
        df = pd.concat(vix_df())
        df = df[['Settle','Trade Date', 'Open Interest', 'Futures']]
        df.set_index('Trade Date', inplace=True)
        df = df.pivot(values=['Settle', 'Open Interest'],
                   columns='Futures')
        df.dropna(inplace=True)
        return df
    return asyncio.run(fetch_vix_futures())


def AD_line_lol():
    df = pd.read_excel(
    "https://www.mcoscillator.com/data/osc_data/OSC-DATA.xls",
    sheet_name=0)
    df = df.dropna()
    df = df.loc[1:, df.columns[0]:df.columns[4]]
    df.columns = ['Date', 'Advances', 'Declines', 'Up Volume', 'Down Volume']
    df.set_index('Date', inplace=True)
    df = df.astype(int)
    df['AD'] = (df['Advances'] - df['Declines']).cumsum()
    df['AD_vol'] = (df['Up Volume'] - df['Down Volume']).cumsum()
    df['Volume_pct'] = np.where(df['Up Volume'] > df['Down Volume'], df['Up Volume'] / (df['Down Volume'] + df['Up Volume']), -df['Down Volume'] / (df['Down Volume'] + df['Up Volume']))
    def plotting():
        import matplotlib.pyplot as plt
        ax = df.plot( y='Volume_pct', kind='line', title='Advance/Decline')
        ax.axhline(y=.90, color='green', linestyle='--', alpha=0.7)
        ax.axhline(y=-.90, color='red', linestyle='--', alpha=0.7)
        plt.show()


async def finra_hy_ig():
    """Returns a link to a zipped download"""
    async with async_playwright() as p:
        """Load Page"""
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.finra.org/finra-data/fixed-income/market-activity')    

        """Filter only 'CORP' bonds"""
        button = page.locator('finra-button').nth(2)
        await button.wait_for(state="visible")
        await button.click()
        
        await page.locator('input[type="search"]').click()

        await page.locator('span:has-text("Type")').click()

        # I guess these are equivalent??
        # type_button = page.get_by_text("Type", exact=True)
        

        # Filter bonds for corporate bonds
        filter_bar = page.locator("finra-text-filter")
        
        await filter_bar.click()
        await filter_bar.type('CORP')
        await page.get_by_text('Apply Filter').click()

        # Adjust Date Filter
        date = datetime.date.today() - datetime.timedelta(days=200)

        await page.locator('input[type="search"]').click()
        await page.get_by_role("treeitem", name="Date").locator("span").click()
        await page.locator("finra-dropdown").click()
        await page.locator("finra-dropdown-option").filter(has_text="Greater than").click()

        date_filter_bar = page.get_by_role("textbox", name="YYYY-MM-DD")
        await date_filter_bar.click()
        await date_filter_bar.type(str(date))

        await page.get_by_text('Apply Filter').click()
        await page.get_by_text('Done').click()

        await page.locator('finra-button').filter(has_text='Export').click()
        async with page.expect_download() as download_info:
            await page.get_by_text("EXPORT", exact=True).click()

        download = await download_info.value

        """ Apparently the path needs to be 'permanent' """
        download_path = await download.path()

        import shutil
        permanent_path = f'finra_data'

        shutil.copy(download_path, permanent_path)
        await browser.close()
        
        return permanent_path

#pass finra_hy_ig into finra_cleaner    
async def process_finra():
    zip_file_path = await finra_hy_ig()

    with open(zip_file_path, 'rb') as f:
        zip_data = f.read()

    zip_buffer = BytesIO(zip_data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        print("Files in zip:", zip_file.namelist())

        for filename in zip_file.namelist():
            if filename.endswith(".csv"):
                csv_data = zip_file.read(filename)
                df = pd.read_csv(BytesIO(csv_data))
                print(df.head)
    # os.remove(zip_file_path)
    return df


def finra_cleaner(df):
    df.rename(columns={'Unnamed: 0': "Metrics"}, inplace=True)

    df = df.pivot_table(
    index=['Date'],
    columns='Metrics',
    values=['High Yield', 'Investment Grade']
    )

    df[('High Yield', 'AD')] = (df[('High Yield', 'Advances')] - df[('High Yield', 'Declines')]).cumsum()
    df[('Investment Grade', 'AD')] = (df[('Investment Grade', 'Advances')] - df[('Investment Grade', 'Declines')]).cumsum()

    df[('High Yield', 'Net Highs')] = (df[('High Yield', '52 Week High')] - df[('High Yield', '52 Week Low')])
    df[('Investment Grade', 'Net Highs')] = (df[('Investment Grade', '52 Week High')] - df[('Investment Grade', '52 Week Low')])
    return df


def pc_ratio(time_in_days: int = None):
    
    def define_urls() -> list:
        # see which dates we need to make the list current
        pass

    async def put_call():
        async def make_request_async(url, browser):
            page = await browser.new_page()
            try:
                response = await page.goto(url)
                title = await page.title()
                return {
                    'url': url,
                    'status': response.status,
                    'title': title
                }
            finally:
                await page.close()
        with async_playwright as p:
            browser = await p.chromium.launch(headless=False, slow_mo=2000)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto('https://www.finra.org/finra-data/fixed-income/market-activity')    
            tasks = [make_request_async(url, browser) for url in define_urls()]
            results = await asyncio.gather(*tasks)        
# Next up: three dimensional plot of vix curve
#   Scrape: interest rates, put/call ratios