__author__ = 'raviottaj'

import pandas as pd
import numpy as np
import datetime

pd.set_option('display.width', 250)


def read_data(xl_sheet_list):
    """opens file and reads data using import helper functions"""
    combined = pd.DataFrame()
    for i in xl_sheet_list:
        xl_file = i[0]
        xl_sheet = i[1]
        year = xl_file.split('/')[-1].split('.')[0].split('_')[0]
        xl = pd.ExcelFile(xl_file)
        df = xl.parse(xl_sheet, header=3, skiprows=2)
        df.columns = ['Group', 'Region', 'Area', 'Month', 'VaccinatedPct', '95 CI']
        df['Year'] = year
        combined = combined.append(df, ignore_index=True)
    return combined


kid_vax_coverage = read_data([("../data/2013-14_coverage.xlsx", '6m-17y'),
                              ("../data/2012-13_coverage.xlsx", '6m-17y'),
                              ("../data/2011-12_coverage.xlsx", '6m-17y'),
                              ("../data/2010-11_coverage.xls", '6m-17y')])

national = kid_vax_coverage[kid_vax_coverage.Region == 'National']
national['VaccinatedPct'] = national['VaccinatedPct'].astype(float)
national['Month'] = pd.DatetimeIndex(pd.to_datetime(national['Month'], format='%B')).month
bymonth = national.groupby('Month').mean()
bymonth.to_csv('../data/kid_avg_vax_rates_2010-2014.csv')
national.to_csv('../data/kid_vax_rates_2010-2014.csv', encoding='utf-8')
print debug

