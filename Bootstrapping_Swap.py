# This file bootstraps ZCB rates from Swap and Deposit rates

# necessary imports
import QuantLib as ql
import pandas as pd
from Bootstrapping.bootstrapping_functions import bootstrap_zcb_curve, datetime_to_ql

# Inputs, reads file data.xlsx and stores it in a data frame, then splits the DF up by currency
raw_data = pd.read_excel("data.xlsx", sheetname=0)
raw_data['Date'] = pd.to_datetime(raw_data['Date'], format='%d%M%Y')
rates_usd = raw_data.iloc[:, 1:21] / 100
rates_eur = raw_data.iloc[:, 21:41] / 100


# defines maturities/tenors
deposit_maturities = [ql.Period(1, ql.Months), ql.Period(2, ql.Months), ql.Period(3, ql.Months),
                      ql.Period(6, ql.Months), ql.Period(12, ql.Months)]
swap_tenors = [ql.Period(2, ql.Years), ql.Period(3, ql.Years), ql.Period(4, ql.Years), ql.Period(5, ql.Years),
               ql.Period(6, ql.Years), ql.Period(7, ql.Years), ql.Period(8, ql.Years), ql.Period(9, ql.Years),
               ql.Period(10, ql.Years), ql.Period(11, ql.Years), ql.Period(12, ql.Years), ql.Period(15, ql.Years),
               ql.Period(20, ql.Years), ql.Period(25, ql.Years), ql.Period(30, ql.Years)]

# defines day count conventions (same for EUR + USD)
deposit_daycount = [ql.Actual360()] * len(deposit_maturities)
swap_daycount = [ql.Thirty360()] * len(swap_tenors)

###############################
# EURO
###############################
maturities = rates_eur.columns
print(maturities)
bootstrapped_rates_eur = {}

for i in range(len(rates_eur)):
    dep_eur = rates_eur.iloc[i, :5]
    swap_eur = rates_eur.iloc[i, 6:]
    value_date = raw_data.iloc[i, 0]
    yieldcurve_eur = bootstrap_zcb_curve(value_date, dep_eur, swap_eur, deposit_maturities, swap_tenors,
                                         deposit_daycount, swap_daycount, ql.Period(ql.Annual))

    zeros = []
    for d in yieldcurve_eur.dates():
        yrs = ql.Thirty360().yearFraction(datetime_to_ql(value_date), d)
        compounding = ql.Continuous
        freq = ql.Annual
        zr = yieldcurve_eur.zeroRate(yrs, compounding, freq)
        zeros.append(zr.rate())
    bootstrapped_rates_eur[value_date] = zeros

bootstrapped_eur = pd.DataFrame.from_dict(bootstrapped_rates_eur, orient='index')
bootstrapped_eur.columns = maturities
bootstrapped_eur.to_pickle("pickle_bootstrapped_eur.pickle")  # quick storage, read with df = pd.read_pickle(file_name)
bootstrapped_eur.index = pd.to_datetime(bootstrapped_eur.index).date
bootstrapped_eur.to_excel("bootstrapped_eur.xlsx", index=True)
print("Bootstrapping EUR done! \n \n")

###############################
# USD
###############################
maturities = rates_usd.columns
print(maturities)
bootstrapped_rates_usd = {}

for i in range(len(rates_usd)):
    dep_usd = rates_usd.iloc[i, :5]
    swap_usd = rates_usd.iloc[i, 6:]
    value_date = raw_data.iloc[i, 0]
    yieldcurve_usd = bootstrap_zcb_curve(value_date, dep_usd, swap_usd, deposit_maturities, swap_tenors,
                                         deposit_daycount, swap_daycount, ql.Period(ql.Semiannual))

    zeros = []
    for d in yieldcurve_usd.dates():
        yrs = ql.Thirty360().yearFraction(datetime_to_ql(value_date), d)
        # needs to have same daycount convention as swap
        compounding = ql.Continuous
        freq = ql.Annual
        zr = yieldcurve_usd.zeroRate(yrs, compounding, freq)
        zeros.append(zr.rate())
    bootstrapped_rates_usd[value_date] = zeros

bootstrapped_usd = pd.DataFrame.from_dict(bootstrapped_rates_usd, orient='index')
bootstrapped_usd.columns = maturities
bootstrapped_usd.to_pickle("pickle_bootstrapped_usd.pickle")  # quick storage, read with df = pd.read_pickle(file_name)
bootstrapped_usd.index = pd.to_datetime(bootstrapped_usd.index).date
bootstrapped_usd.to_excel("bootstrapped_usd.xlsx", index=True)