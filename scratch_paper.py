import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv(r'C:\Users\josep\OneDrive\Desktop\Coding_env\blank.csv')
df2 = pd.read_csv(r'C:\Users\josep\OneDrive\Desktop\Coding_env\blank2.csv')

df3 = pd.merge(df, df2, on='label', how='outer')
df3.to_csv('shootfromhip.csv')