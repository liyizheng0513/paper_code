#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 12:21:23 2017

@author: liyizheng
"""

import statsmodels.formula.api as smf
import statsmodels.api as sm
import itertools
import pandas as pd


def forward_selected(data, response, n):
    """Linear model designed by forward selection.

    Parameter:
    -----------
    data : pandas DataFrame with all possible predictors and response

    response: string, name of response column in data

    Returns:
    --------
    model: an "optimal" fitted statsmodels linear model
           with an intercept
           selected by forward selection
           evaluated by adjusted R-squared
    """
    remaining = set(data.columns)
    remaining.remove(response)
    selected = []
    current_score, best_new_score = 0.0, 0.0
    while len(selected) <= n and current_score == best_new_score:
        scores_with_candidates = []
        for candidate in remaining:
            formula = "{} ~ {} + 1".format(response,
                                           ' + '.join(selected + [candidate]))
            score = smf.ols(formula, data).fit().rsquared_adj
            scores_with_candidates.append((score, candidate))
        scores_with_candidates.sort()
        best_new_score, best_candidate = scores_with_candidates.pop()
        if current_score < best_new_score:
            remaining.remove(best_candidate)
            selected.append(best_candidate)
            current_score = best_new_score
    formula = "{} ~ {} + 1".format(response,
                                   ' + '.join(selected))
    model = smf.ols(formula, data).fit()
    return model


def alpha_factor(factor_ret, fund_ret, n):
    """get alpha and the most significant factors explain the fund returns

    Parameters:
    -----------
    factor_ret : the returns of style factors

    fund_ret: the returns of fund

    n: the num used to explain the returns of fund 

    Returns:
    --------
    model_list: an "optimal" fitted statsmodels linear model
           with an intercept
           selected by forward selection
           evaluated by adjusted R-squared∏
    """
    model_list = []
    for fund in fund_ret.columns:
        temp_panel = factor_ret.copy()
        temp_panel[fund] = fund_ret[fund]
        model = forward_selected(temp_panel, fund, n)
        model_list.append(model)
    return model_list


def get_alpha_rsquare(model_list):
    """
    get alpha,rsquared_adj,tvalues
    """
    alpha_rsquare_tvalues = []
    for model in model_list:
        alpha = model.params.Intercept
        rsquare = model.rsquared_adj
        tvalues = model.tvalues.Intercept
        alpha_rsquare_tvalues.append([alpha, rsquare, tvalues])
    return alpha_rsquare_tvalues


def get_fund_value(art):
    ar = pd.DataFrame(art, columns=['alpha', 'rsquared_adj', 'tvalues'])
    ar.rsquared_adj = 1.0 / ar.rsquared_adj
    ar_std = (ar - ar.mean()) / ar.std()
    importance = ar_std * pd.Series([0.25, 0.25, 0.5], index=ar.columns)
    importance = importance.sum(axis=1)
    importance = importance.sort_values(ascending=False)
    return importance

def circle_ols(fund_ret, factor_ret, n):
    '''
    Parameters:
    -----------
    factor_ret : the returns of style factors

    fund_ret: the returns of fund

    n: the num used to explain the returns of fund 
    '''
    factors_num = factor_ret.shape[1]
    circle_elements = itertools.combinations(range(factors_num), n)
    alpha_rsquare_tvalues = []
    for sub in circle_elements:
        factor_use = factor_ret.iloc[:,list(sub)]
        model = sm.OLS(fund_ret, sm.add_constant(factor_use)).fit()
        alpha = model.params.const
        rsquare = model.rsquared_adj
        tvalues = model.tvalues.const
        alpha_rsquare_tvalues.append([alpha, rsquare, tvalues])
    return pd.DataFrame(alpha_rsquare_tvalues, columns=['alpha', 'rsquared_adj', 'tvalues'])





    


    

