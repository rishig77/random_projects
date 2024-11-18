

import numpy as np
import pandas as pd
from numba import jit
import data
from data_keys import *

########################################################################
# Constants.

# Average number of days in a year. Normal years have 365 days,
# but every 4th year is a leap-year with 366 days.
DAYS_PER_YEAR = 365.25

# Average number of business- or trading-days in a year.
BDAYS_PER_YEAR = 251.67

########################################################################
# Public functions.


def total_return(df):
    """
    Calculate the "Total Return" of a stock when dividends are
    reinvested in the stock.

    The formula is:

    Total_Return[t] = Total_Return[t-1] * (Dividend[t] + Share_Price[t]) / Share_Price[t-1]

    :param df:
        Pandas data-frame assumed to contain SHARE_PRICE and DIVIDEND.
    :return:
        Pandas series with the Total Return.
    """

    # Copy the relevant data so we don't change it.
    df2 = df[[SHARE_PRICE, DIVIDEND]].copy()

    # Fill NA-values in the Dividend-column with zeros.
    df2[DIVIDEND].fillna(0, inplace=True)

    # Calculate the daily Total Return.
    tot_ret_daily = (df2[DIVIDEND] + df2[SHARE_PRICE]) / df2[SHARE_PRICE].shift(1)

    # Calculate the cumulative Total Return.
    tot_ret = tot_ret_daily.cumprod()

    # Replace the first row's NA with 1.0
    tot_ret.iloc[0] = 1.0

    return tot_ret


def annualized_returns(series, years):
    """
    Calculate the annualized returns for all possible
    periods of the given number of years.

    For example, given the Total Return of a stock we want
    to know the annualized returns of all holding-periods
    of 10 years.

    :param series:
        Pandas series e.g. with the Total Return of a stock.
        Assumed to be daily data.
    :param years:
        Number of years in each period.
    :return:
        Pandas series of same length as the input series. Each
        day has the annualized return of the period starting
        that day and for the given number of years. The end of
        the series has NA for the given number of years.
    """

    # Number of days to shift data. All years have 365 days
    # except leap-years which have 366 and occur every 4th year.
    # So on average a year has 365.25 days.
    days = int(years * 365.25)

    # Calculate annualized returns for all periods of this length.
    # Note: It is important we have daily (interpolated) data,
    # otherwise the series.shift(365) would shift much more than
    # a year, if the data only contains e.g. 250 days per year.
    ann_return = (series.shift(-days) / series) ** (1 / years) - 1.0

    return ann_return


def prepare_ann_returns(df, years, key=PSALES, subtract=None):
    """
    Prepare annualized returns e.g. for making a scatter-plot.
    The x-axis is given by the key (e.g. PSALES) and the y-axis
    would be the annualized returns.

    :param df:
        Pandas DataFrame with columns named key and TOTAL_RETURN.
    :param years:
        Number of years for annualized returns.
    :param key:
        Name of the data-column for x-axis e.g. PSALES or PBOOK.
    :param subtract:
        Pandas Series to be subtracted from ann-returns
        to adjust for e.g. growth in sales-per-share.
    :return:
        (x, y) Pandas Series with key and adjusted ANN_RETURN.
    """

    # Create a new data-frame so we don't modify the original.
    # We basically just use this to sync the data we are
    # interested in for the common dates and avoid NA-data.
    df2 = pd.DataFrame()

    # Copy the key-data e.g. PSALES.
    df2[key] = df[key]

    # Calculate all annualized returns for all periods of
    # the given number of years using the Total Return.
    ann_return = annualized_returns(series=df[TOTAL_RETURN], years=years)

    if subtract is None:
        # Add the ann-returns to the new data-frame.
        df2[ANN_RETURN] = ann_return
    else:
        # Calculate all annualized returns for the series
        # that must be subtracted e.g. sales-per-share.
        ann_return_subtract = annualized_returns(series=subtract, years=years)

        # Subtract the ann. returns for the total return
        # and the adjustment (e.g. sales-per-share).
        # Then add the result to the new data-frame.
        df2[ANN_RETURN] = ann_return - ann_return_subtract

    # Drop all rows with NA.
    df2.dropna(axis=0, how='any', inplace=True)

    # Retrieve the relevant data.
    x = df2[key]
    y = df2[ANN_RETURN]

    return x, y


@jit(forceobj=True)
def mean_std_ann_returns(series, min_years=7, max_years=15,
                         days_per_year=DAYS_PER_YEAR):
    """
    Calculate mean and std.dev. annualized returns for a range
    of investment periods.

    For each day we calculate the annualized returns for a whole
    range of periods between e.g. 7 and 15 years into the future,
    then we take the mean and std.dev. of all those annualized
    returns. This smoothens the effect of random mispricing at
    the time of sale, so it is more obvious if there is a
    relationship between a predictive signal and future returns.

    This function uses "Numba jit" so the for-loop is compiled
    into machine-code which gives a 10x speed increase after the
    function has been called once.

    Note the use of jit with "forceobj=True" which allows for a mix
    of ordinary Python and optimized code, which makes the code easier
    to read. The fastest jit-mode is actually "fallback" which is about
    twice as fast, but it generates several warnings and will be
    deprecated in the future. The slowest mode is "nopython=True" where
    the for-loop is made inside a nested function that is fully
    compatible with Numba jit, but that is actually twice as slow as
    "forceobj=True" in this case. So this is the best compromise and
    still gives a 10x speed-up.

    :param series:
        Pandas Series with e.g. the Total Return of a stock.
    :param min_years:
        Min number of years for investment periods.
    :param max_years:
        Max number of years for investment periods.
    :param days_per_year:
        Number of days in a year for the data in `series`. Use one of these:
        - DAYS_PER_YEAR for daily interpolated data with leap-years.
        - BDAYS_PER_YEAR for the average number of trading-days per year.
    :return:
        Pandas DataFrame where each day has the mean and std.dev. for the
        annualized returns of the future investment periods starting
        that day and for all periods between `min_year` and `max_year`.
    """

    # The idea of this algorithm is to step through the data
    # one day at a time. For each day we lookup an array of
    # e.g. Total Return values in the future and calculate the
    # annualized returns, and then take the mean and std.dev.
    # of that. There may be a faster and more clever way of
    # implementing this, but it is fast enough for our purposes
    # when using Numba jit to speed-up the for-loop.

    # Min / max number of days for the periods we consider.
    # For example, between 7 and 15 years into the future.
    min_days = int(min_years * days_per_year)
    max_days = int(max_years * days_per_year)

    # Ensure series is long enough.
    if len(series) < max_days:
        msg = 'len(series)={0} is too short for max_days={1}'
        msg = msg.format(len(series), max_days)
        raise ValueError(msg)

    # Exponent used for calculating annualized returns.
    exponent = days_per_year / np.arange(min_days, max_days)

    # Number of days in the output arrays.
    num_days = len(series) - max_days

    # Pre-allocate output arrays for the mean and std.dev. ann. returns.
    mean_ann_rets = np.zeros(num_days, dtype=np.float)
    std_ann_rets = np.zeros(num_days, dtype=np.float)

    # Convert the Pandas Series into a numpy array
    # which is supported by the numba jit compiler.
    values = series.to_numpy()

    # For each day do the following.
    # Note: This for-loop will be optimized by the numba jit compiler.
    for i in range(num_days):
        # Get the Total Return value for the i'th day.
        tot_ret_today = values[i]

        # Get array of Total Return values for future days.
        tot_ret_future = values[i + min_days:i + max_days]

        # Annualized Returns between today and those future days.
        ann_rets = (tot_ret_future / tot_ret_today) ** exponent - 1.0

        # Mean annualized returns.
        mean_ann_rets[i] = np.mean(ann_rets)

        # Standard deviation for the annualized returns.
        std_ann_rets[i] = np.std(ann_rets)

    # Create a Pandas DataFrame with the result.
    data = {MEAN_ANN_RETURN: mean_ann_rets, STD_ANN_RETURN: std_ann_rets}
    df_result = pd.DataFrame(data=data, index=series.index[0:num_days])

    return df_result


def prepare_mean_ann_returns(df, min_years=7, max_years=15, key=PSALES):
    """
    Prepare mean annualized returns e.g. for making a scatter-plot.
    The x-axis is given by the key (e.g. PSALES) and the y-axis
    would be the mean annualized returns.

    For each day we calculate the annualized returns for a whole
    range of periods between e.g. 7 and 15 years into the future,
    then we take the mean of all those annualized returns. This
    smoothens the effect of random mispricing at the time of sale,
    so it is more obvious if there is a relationship between the
    predictive signal and future returns.

    :param df:
        Pandas DataFrame with columns named key and TOTAL_RETURN
        both assumed to have daily interpolated data.
    :param min_years:
        Min number of years for investment periods.
    :param max_years:
        Max number of years for investment periods.
    :param key:
        Name of the data-column for x-axis e.g. PSALES or PBOOK.
    :return:
        (x, y) Pandas Series with key and mean ANN_RETURN_MEAN.
    """

    # Get the common start-dates for the data-columns.
    dfs = [df[TOTAL_RETURN].dropna(), df[key].dropna()]
    start_date, _ = data.common_period(dfs=dfs)

    # Get the individual data-columns from their common start-dates.
    # NOTE: We use dropna() on them individually so as to keep as much
    # data as possible when calculating the mean ann. returns.
    # This means we have to sync the array-lengths further below.
    df_key = df[key][start_date:].dropna()
    df_tot_ret = df[TOTAL_RETURN][start_date:].dropna()

    # Calculate both the mean and std.dev. ann. returns.
    # Assume the Total Return has daily interpolated data.
    df_mean_ann_rets = mean_std_ann_returns(series=df_tot_ret,
                                            min_years=min_years,
                                            max_years=max_years,
                                            days_per_year=DAYS_PER_YEAR)

    # Common length for the two arrays.
    common_len = min(len(df_mean_ann_rets), len(df_key))

    # The predictive signal e.g. P/Sales.
    x = df_key[0:common_len]

    # The mean annualized returns.
    y = df_mean_ann_rets[MEAN_ANN_RETURN].iloc[0:common_len]

    return x, y


def bond_annualized_returns(df, num_years):
    """
    Calculate the annualized returns from investing and reinvesting in a bond.

    This results in a list of Pandas Series ann_returns with the annualized
    returns for [1, 2, ..., num_years] investment years.

    For example ann_returns[0] are for 1-year investment periods and
    ann_returns[9] are for 10-year periods.

    :param df:
        Pandas DataFrame with BOND_YIELD data for 1-year maturity.
    :param num_years:
        Max number of investment years.
    :return:
        List of Pandas Series.
    """

    # The idea is to repeatedly shift the bond-yields
    # and update a cumulative product so as to get the
    # compounded return through the years.

    # Init the list of annualized returns. For 1-year
    # investment periods these are just the bond-yields.
    ann_returns = [df[BOND_YIELD].copy()]

    # Init the cumulative product of bond-yields,
    # which will be updated when reinvesting in the
    # bonds through the years.
    cum_prod = df[BOND_YIELD].copy() + 1.0

    # Init the bond-yields shifted one year.
    # These will be shifted 365 steps for each year.
    shifted = cum_prod.copy()

    # For increasing number of investment years.
    # The bond-yields were used as the 1st year above.
    for years in range(2, num_years + 1):
        # Shift the bond-yields one year.
        # Note leap-years are not taken into account so
        # there will be a slight drift for longer periods,
        # but it probably only causes a very small error.
        shifted = shifted.shift(-365)

        # Accumulate the bond-yields so cum_prod holds the
        # cumulative return from reinvesting in the bonds.
        cum_prod *= shifted

        # Remove NA from the end of the series.
        cum_prod.dropna(inplace=True)

        # Calculate the annualized returns.
        ann_ret = cum_prod ** (1 / years) - 1.0

        # Rename the data-column.
        ann_ret.rename(ANN_RETURN)

        # Add to the list of annualized returns for all years.
        ann_returns.append(ann_ret)

    return ann_returns


def daily_returns(df, start_date, end_date):
    """
    Calculate the daily returns for the TOTAL_RETURN of the given
    DataFrame between the given dates.

    :param df: Pandas DataFrame containing TOTAL_RETURN for all days.
    :param start_date: Only use data from this date.
    :param end_date: Only use data to this date.
    :return: None.
    """

    # Get the Total Return for this date-range.
    tot_ret = df[TOTAL_RETURN][start_date:end_date]

    # Calculate the daily returns assuming we have daily data.
    daily_ret = tot_ret.shift(-1) / tot_ret

    return daily_ret


def reinvestment_growth(df, smooth=True):
    """
    Estimate the growth in the Total Return from reinvestment
    of dividends (and ignoring taxes). This is done by subtracting
    the yearly changes in Total Return and Share-Price.

    The resulting growth-rates are quite erratic, possibly
    because of slight changes in the dividend-dates. This
    can be smoothed by a moving average.

    :param df: Pandas DataFrame with SHARE_PRICE and TOTAL_RETURN.
    :param smooth: Boolean whether to smooth the growth-rates.
    :return: Pandas Series with the reinvestment growth.
    """

    # Yearly percentage change in share-price. Assume the data is daily.
    price_change = df[SHARE_PRICE].pct_change(periods=365)

    # Yearly percentage change in Total Return. Assume the data is daily.
    tot_ret_change = df[TOTAL_RETURN].pct_change(periods=365)

    # The difference is the growth from reinvestment of dividends.
    growth = tot_ret_change - price_change

    # Smoothen the growth-rates using moving average?
    if smooth:
        growth = growth.rolling(window=20).mean()

    # Remove empty rows.
    growth = growth.dropna()

    return growth


def dividend_yield(df):
    """
    Calculate the daily Dividend Yield of a stock, as the forward-filled
    TTM Dividend divided by the daily Share-Price.

    :param df: Pandas DataFrame with SHARE_PRICE and DIVIDEND_TTM.
    :return: Pandas Series with the data.
    """

    return (df[DIVIDEND_TTM].ffill() / df[SHARE_PRICE]).rename(DIVIDEND_YIELD)


def max_drawdown(df, window=None):
    """
    Calculate the Maximum Drawdown for all the individual columns in `df`.

    This gives the Max Drawdown for each time-step, calculated either
    from the beginning or from the preceding window of the given length.

    If you want the worst drawdown that has occurred through all time-steps,
    then you should call the `min()` function on the resulting DataFrame,
    for example: `max_drawdown(df=df_prices).min()`

    :param df:
        Pandas DataFrame typically with share-prices but could have any data.
        If the DataFrame contains data for more stocks, then the columns are
        the stock-tickers and the rows are the time-steps.

    :param window:
        If `None` then calculate the Max Drawdown from the beginning.
        If an integer then calculate the Max Drawdown for a rolling window
        of that length.

    :return:
        Pandas DataFrame with the Max Drawdown time-series.
    """
    if window is None:
        # Calculate Max Drawdown from the beginning.
        max_dd = df / df.cummax() - 1.0
    else:
        # Calculate Max Drawdown for a rolling window.
        max_dd = df / df.rolling(window=window).max() - 1.0

    return max_dd


def max_pullup(df, window=None):
    """
    Calculate the Maximum Pullup for all the individual columns in `df`.

    This gives the Max Pullup for each time-step, calculated either
    from the beginning or from the preceding window of the given length.

    If you want the highest pullup that has occurred through all time-steps,
    then you should call the `max()` function on the resulting DataFrame,
    for example: `max_pullup(df=df_prices).max()`

    Unlike the function `max_drawdown` which is typically calculated for the
    entire DataFrame `df` by setting `window=None`, it is often more useful
    to set the `window` parameter when calculating the Max Pullup using this
    function. This is because many stocks tend to have increasing prices over
    time, so the "pullup" or recovery from their historical lows is potentially
    infinite over time. So it may be more useful to only consider the pullup
    over e.g. 1-year periods by setting the `window` parameter accordingly.

    :param df:
        Pandas DataFrame typically with share-prices but could have any data.
        If the DataFrame contains data for more stocks, then the columns are
        the stock-tickers and the rows are the time-steps.

    :param window:
        If `None` then calculate the Max Pullup from the beginning.
        If an integer then calculate the Max Pullup for a rolling window
        of that length.

    :return:
        Pandas DataFrame with the Max Pullup time-series.
    """
    if window is None:
        # Calculate Max Pullup from the beginning.
        max_pu = df / df.cummin() - 1.0
    else:
        # Calculate Max Pullup for a rolling window.
        max_pu = df / df.rolling(window=window).min() - 1.0

    return max_pu


########################################################################
