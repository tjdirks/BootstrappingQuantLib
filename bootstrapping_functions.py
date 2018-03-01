import QuantLib as ql

def datetime_to_ql(date):
    return ql.Date(date.day, date.month, date.year)


def ql_to_datetime(date):
    return dt.datetime(date.year(), date.month(), date.dayOfMonth())


def bootstrap_zcb_curve(value_date, deposit_rates, swap_rates, deposit_maturities, swap_tenors, deposit_daycount,
                        swap_daycount, fixed_freq):
    spot_lag = 2
    swap_prices = [100] * len(swap_tenors)  # swaps priced like par cpn bond
    swap_fixed_freq = [fixed_freq] * len(swap_tenors)
    value_date = datetime_to_ql(value_date)
    calendar = ql.TARGET()
    ql.Settings.instance().evaluationDate = value_date

    helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(r)), mat, spot_lag, calendar,
                                    ql.ModifiedFollowing, True, dc)
               for r, mat, dc in zip(deposit_rates, deposit_maturities, deposit_daycount)]

    for r, mat, dc, l, w in zip(swap_prices, swap_tenors, swap_daycount, swap_fixed_freq, swap_rates):
        termination_date = value_date + mat
        schedule = ql.Schedule(value_date,
                               termination_date,
                               l,
                               calendar,
                               ql.ModifiedFollowing,
                               ql.ModifiedFollowing,
                               ql.DateGeneration.Backward,
                               True)

        helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(r)),
                                        spot_lag,
                                        100,
                                        schedule,
                                        [w],
                                        dc,
                                        ql.ModifiedFollowing
                                        )
        helpers.append(helper)
    yieldcurve = ql.PiecewiseLinearZero(value_date, helpers, swap_daycount[0])
    return yieldcurve
