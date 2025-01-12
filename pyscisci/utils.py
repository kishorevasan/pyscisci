# -*- coding: utf-8 -*-
"""
.. module:: publication
    :synopsis: The main Publication class

.. moduleauthor:: Alex Gates <ajgates42@gmail.com>
 """
import sys
import pandas as pd
import numpy as np
import requests

# determine if we are loading from a jupyter notebook (to make pretty progress bars)
if 'ipykernel' in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

def groupby_count(df, colgroupby, colcountby, count_unique=True, show_progress=False):
    """
    Group the DataFrame and count the number for each group.

    Parameters
    ----------
    :param df: DataFrame
        The DataFrame.

    :param colgroupby: str
        The column to groupby.

    :param colcountby: str
        The column to count.

    :param count_unique: bool, default True
        If True, count unique items in the rows.  If False, just return the number of rows.

    :param show_progress: bool or str, default False
        If True, display a progress bar for the count.  If str, the name of the progress bar to display.

    Returns
    ----------
    DataFrame
        DataFrame with two columns: colgroupby, colcountby+`Count`
    """

    desc = ''
    if isinstance(show_progress, str):
        desc = show_progress
    # register our pandas apply with tqdm for a progress bar
    tqdm.pandas(desc=desc, disable= not show_progress)

    newname_dict = zip2dict([str(colcountby), '0'], [str(colcountby)+'Count']*2)
    if count_unique:
        count_df = df.groupby(colgroupby, sort=False)[colcountby].progress_apply(lambda x: x.nunique())
    else:
        count_df = df.groupby(colgroupby, sort=False)[colcountby].progress_apply(lambda x: x.shape[0])

    return count_df.to_frame().reset_index().rename(columns=newname_dict)

def groupby_range(df, colgroupby, colrange, show_progress=False):
    """
   Group the DataFrame and find the range between the smallest and largest value for each group.

    Parameters
    ----------
    :param df: DataFrame
        The DataFrame.

    :param colgroupby: str
        The column to groupby.

    :param colrange: str
        The column to find the range of values.

    :param show_progress: bool or str, default False
        If True, display a progress bar for the range.  If str, the name of the progress bar to display.

    Returns
    ----------
    DataFrame
        DataFrame with two columns: colgroupby, colrange+`Range`
    """
    desc = ''
    if isinstance(show_progress, str):
        desc = show_progress
    # register our pandas apply with tqdm for a progress bar
    tqdm.pandas(desc=desc, disable= not show_progress)

    newname_dict = zip2dict([str(colrange), '0'], [str(colrange)+'Range']*2)
    return df.groupby(colgroupby, sort=False)[colrange].progress_apply(lambda x: x.max() - x.min()).to_frame().reset_index().rename(columns=newname_dict)

def groupby_zero_col(df, colgroupby, colrange, show_progress=False):
    """
    Group the DataFrame and shift the column so the minimum value is 0.

    Parameters
    ----------
    :param df: DataFrame
        The DataFrame.

    :param colgroupby: str
        The column to groupby.

    :param colrange: str
        The column to find the range of values.

    :param show_progress: bool or str, default False
        If True, display a progress bar.  If str, the name of the progress bar to display.

    Returns
    ----------
    DataFrame
        DataFrame with two columns: colgroupby, colrange
    """
    desc = ''
    if isinstance(show_progress, str):
        desc = show_progress
    # register our pandas apply with tqdm for a progress bar
    tqdm.pandas(desc=desc, disable= not show_progress)

    return df.groupby(colgroupby, sort=False)[colrange].progress_transform(lambda x: x - x.min())

def groupby_total(df, colgroupby, colcountby, show_progress=False):
    """
    Group the DataFrame and find the total of the column.

    Parameters
    ----------
    :param df: DataFrame
        The DataFrame.

    :param colgroupby: str
        The column to groupby.

    :param colcountby: str
        The column to find the total of values.

    :param show_progress: bool or str, default False
        If True, display a progress bar for the summation.  If str, the name of the progress bar to display.

    Returns
    ----------
    DataFrame
        DataFrame with two columns: colgroupby, colcountby+'Total'
    """
    desc = ''
    if isinstance(show_progress, str):
        desc = show_progress
    # register our pandas apply with tqdm for a progress bar
    tqdm.pandas(desc=desc, disable= not show_progress)

    newname_dict = zip2dict([str(colcountby), '0'], [str(colcountby)+'Total']*2)
    return df.groupby(colgroupby, sort=False)[colcountby].progress_apply(lambda x: x.sum()).to_frame().reset_index().rename(columns=newname_dict)

def groupby_mean(df, colgroupby, colcountby, show_progress=False):
    """
    Group the DataFrame and find the mean of the column.

    Parameters
    ----------
    :param df: DataFrame
        The DataFrame.

    :param colgroupby: str
        The column to groupby.

    :param colcountby: str
        The column to find the mean of values.

    :param show_progress: bool or str, default False
        If True, display a progress bar for the summation.  If str, the name of the progress bar to display.

    Returns
    ----------
    DataFrame
        DataFrame with two columns: colgroupby, colcountby+'Mean'
    """
    desc = ''
    if isinstance(show_progress, str):
        desc = show_progress
    # register our pandas apply with tqdm for a progress bar
    tqdm.pandas(desc=desc, disable= not show_progress)

    newname_dict = zip2dict([str(colcountby), '0'], [str(colcountby)+'Mean']*2)
    return df.groupby(colgroupby, sort=False)[colrange].progress_apply(lambda x: x.mean()).to_frame().reset_index().rename(columns=newname_dict)

def isin_range(values2check, min_value, max_value):
    """
    Check if the values2check are in the inclusive range [min_value, max_value].

    Parameters
    ----------
    :param values2check: numpy array
        The values to check.

    :param min_value: float
        The lowest value of the range.

    :param max_value: float
        The highest value of the range.

    :param show_progress: bool or str, default False
        If True, display a progress bar for the count.  If str, the name of the progress bar to display.

    Returns
    ----------
    Numpy Array
        True if the value is in the range.
    """
    return np.logical_and(values2check >= min_value, values2check <= max_value)

def isin_sorted(values2check, masterlist):
    """
    Check if the values2check are in the sorted masterlist.

    Parameters
    ----------
    :param values2check: numpy array
        The values to check.

    :param masterlist: numpy array
        The sorted list of master values.

    Returns
    ----------
    Numpy Array
        True if the value is in the masterlist.
    """
    index = np.searchsorted(masterlist, values2check, side = 'left')
    index[index >= masterlist.shape[0]] = masterlist.shape[0] - 1
    return values2check == masterlist[index]

def argtopk(a, k=5):
    return np.argpartition(a, -k)[-k:][::-1]

def changepoint(a):
    return np.concatenate([[0], np.where(a[:-1] != a[1:])[0] + 1, [a.shape[0]]])

def zip2dict(keys, values):
    return dict(zip(keys, values))

def series2df(ser):
    return ser.to_frame().reset_index()

def load_int(v):
    try:
        return int(v)
    except ValueError:
        return None

def load_float(v):
    try:
        return float(v)
    except ValueError:
        return None

def check4columns(df, column_list):
    # TODO: make proper error messages
    for col in column_list:
        if not col in list(df):
            print("Must pass column {0}".format(col))

def rolling_window(a, window, step_size = 1):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def forward_rolling_window(a, window, step_size = 1):
    a = np.pad(a.astype(float), (0,int(window)), 'constant', constant_values=(np.nan, np.nan))
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def hard_rolling_window(a, window, step_size = 1):
    a = np.pad(a.astype(float), (int((window - 1)/2),int((window - 1)/2) + 1), 'constant', constant_values=(np.nan, np.nan))
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return  np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def past_window(a, window, step_size = 1):
    a = np.pad(a.astype(float), (window - 1, 0), 'constant', constant_values=(np.nan, np.nan))
    shape = a.shape[:-1] + (a.shape[-1] - window + 2 - step_size, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return  np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def kl(p,q):
    """
    Kullback–Leibler divergence (KL-divergence)
    """
    return -np.nansum(p[p>0]*np.log2(p[p>0]/q[p>0]))

def jenson_shannon(p,q):
    """
    Jensen–Shannon divergence
    """
    m = 0.5 * (p+q)
    return 0.5 * (kl(p,m) + kl(q,m))

def rank_array(a, ascending=True, normed=False):
    """
    Rank elements in the array.  
    ascending=> lowest=0, highest=1
    descending=> lowest=1, highest=0

    Parameters
    ----------
    :param a : numpy array or list
        Object to rank

    :param ascending : bool, default True
        Sort ascending vs. descending.

    :param normed : bool, default False
        False : rank is from 0 to N -1
        True : rank is from 0 to 1

    Returns
    ----------
    Ranked array.

    """
    idx = np.argsort(a)
    ranks = np.empty_like(idx)

    if ascending:
        ranks[idx] = np.arange(idx.shape[0])
    else:
        ranks[idx] = np.arange(idx.shape[0])[::-1]

    if normed:
        ranks = ranks/(ranks.shape[0]-1)
    return ranks

def holder_mean(a, rho=1):
    """
    Holder mean

    Parameters
    ----------
    :param a : numpy array or list
        array of values

    :param rho : float
        holder parameter
        arithmetic mean (rho=1)
        geometric mean (rho=0)
        harmonic mean (rho=-1)
        quadratic mean (rho=2)
        max (rho-> infty)
        min (rho-> -infty)

    """
    return (a**rho).sum()**(1.0/rho) / a.shape[0]

def uniquemap_by_frequency(df, colgroupby='PublicationId', colcountby='FieldId', ascending=False):
    """
    Reduce a one-to-many mapping to a selection based on frequency of occurence in the dataframe  
    (either to the largest, most common or smallest, least common).
    
    Parameters
    ----------
    :param ascending : bool, default False
        False: larger counts dominate--map defaults to the most common
        True: smaller counts dominate--map defaults to the least common
    """
    countkeydict = {countid:i for i, countid in enumerate(df[colcountby].value_counts(ascending=ascending).index.values)}
    def countkey(a):
        if isinstance(a, pd.Series):
            return [countkeydict[c] for c in a]
        else:
            return countkeydict[a]
    return df.sort_values(by=[colcountby], key=countkey).drop_duplicates(subset=[colgroupby], keep='first')


def download_file_from_google_drive(file_id, destination=None):
    """
    Download data files from the google Drive.

    Modified from: from https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
    """
    CHUNK_SIZE = 32768

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : file_id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : file_id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    if destination is None:
        return response
    else:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        return None   

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None