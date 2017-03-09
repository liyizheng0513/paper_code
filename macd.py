#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 22:13:06 2017

@author: liyizheng
"""

import pandas as pd
import numpy as np
import talib

class technical_Analysis:
    def __init__(self,data_day,data_week):

        """
        :param data_day: the day data including close,high,low,volume
        :param data_week: the week data including close,high,low,volume
        """
        self.data_day=data_day
        self.data_week=data_week
        self.situation=pd.DataFrame({})
        self.trade_result=pd.DataFrame({})
        self.situ_dic=dict()
        self.situ_performance=dict()
        self.transfer_situation=pd.DataFrame({})

    def situation_detail(self):
        """"
        descri be each situation
        """
        situ=self.situation
        dic = dict()
        sit = list(set(situ.mark.values))
        transfer_sitution=[]
        for s in sit:
            dic[s] = []
        start = 0
        for i in range(1, len(situ.mark)):
            a1 = situ.mark[i - 1]
            a2 = situ.mark[i]
            if a1 != a2:
                temp = situ.iloc[start:i].pct_chg
                r = (temp + 1).prod() - 1
                if start > 0:
                    presitu = situ.mark[start - 1]
                else:
                    presitu = np.nan
                dic[situ.mark[i - 1]].append(
                    [situ.index[start], situ.index[i], r, presitu, situ.mark[i - 1], i - start])
                transfer_sitution.append([situ.index[start], situ.index[i], r, presitu, situ.mark[i - 1], i - start])
                start = i
        for s in dic.keys():
            dic[s] = pd.DataFrame(dic[s], columns=['startdate', 'enddate', 'returns', 'premark', 'mark', 'length'])

        situation=pd.DataFrame(transfer_sitution,columns=['startdate', 'enddate', 'returns', 'premark', 'mark', 'length'])
        situation=situation[1:]
        situation['changepoint'] = situation.apply(lambda x: int(x.mark) - int(x.premark), axis=1)
        self.transfer_situation=situation
        self.situ_dic=dic



    def situation_premark(self,limit):
        """"
        :param limit: filter the situation which length bigger than limit
        """
        situ=self.situation
        dic = self.situ_dic
        dic_pre = dict()
        for s in dic.keys():
            dic[s]=dic[s][dic[s].length>=limit]
        for s in dic.keys():
            grouped = dic[s].groupby('premark')
            dic_pre[s] = grouped.agg({'length': lambda x: x.sum(), 'returns': lambda x: (x + 1).prod() - 1})
            ff = grouped.agg({'returns': lambda x: x.map(lambda y: 1 if y > 0 else 0).sum() / (x.shape[0] + 0.0)})
            gg = grouped.agg({'length': lambda x: x.shape[0]})
            dic_pre[s]['win_rate'] = ff['returns']
            dic_pre[s]['num'] = gg['length']
            dic_pre[s]['mean_return'] = dic_pre[s].apply(lambda x: np.power(1 + x.returns, 1 / (0.0 + x.num)) - 1,
                                           axis=1)
            dic_pre[s]['mean_length'] = dic_pre[s].apply(lambda x: x.length / (x.num + 0.0), axis=1)

        self.situ_performance=dic_pre






    def situation_define(self):
        pass

    def trade(self):
        pass




class MACD(technical_Analysis):

    def __init__(self,data_day,data_week):
        technical_Analysis.__init__(self,data_day,data_week)

    def situation_define(self):
        """
        generate the original table from the input data, mark each situation with '0' or '1'
        """
        dif_d, dea_d, macd_d = talib.MACD(self.data_day.values)
        dif_w, dea_w, macd_w = talib.MACD(self.data_week.values)
        d_data = pd.DataFrame({'macd_d': macd_d, 'dif_d': dif_d}, index=self.data_day.index)
        w_data = pd.DataFrame({'macd_w': macd_w, 'dif_w': dif_w}, index=self.data_week.index)
        d_data = d_data.dropna()
        w_data = w_data.dropna()
        situation = pd.DataFrame({}, columns=['macd_w', 'dif_w', 'macd_d', 'dif_d'], index=d_data.index)
        situation[['macd_d', 'dif_d']] = d_data[['macd_d', 'dif_d']]
        situation['macd_w'].ix[w_data.index] = w_data['macd_w']
        situation['dif_w'].ix[w_data.index] = w_data['dif_w']
        situation = situation.fillna(method='pad')
        situation = situation.dropna()
        sign = lambda x: '1' if x > 0 else '0'
        situation['mark'] = situation.applymap(sign).apply(np.sum, axis=1)
        pct = list(self.data_day.pct_change().ix[situation.index].values)[1:]
        pct.append(0)
        situation['pct_chg'] = pct
        self.situation=situation


    def situation_change(self,situaton_set):
        """"
        :param situaton_set: the feature you want to choose from the original table
        """
        situation=self.situation[situaton_set]

        sign = lambda x: '1' if x > 0 else '0'
        situation['mark'] = situation.applymap(sign).apply(np.sum, axis=1)
        pct = list(self.data_day.pct_change().ix[situation.index].values)[1:]
        pct.append(0)
        situation['pct_chg'] = pct

        self.situation=situation


    def run(self,sitution_set,limit):
        """"
        :param sitution_set: the feature you want to choose from the original table
        :param  limit:filter the situation which length bigger than limit
        do all of the action we need at one time
        """
        self.situation_define()
        self.situation_change(sitution_set)
        self.situation_detail()
        self.situation_premark(limit)
        self.power()


    def power(self):
        situation=self.transfer_situation
        situation['power']=situation['mark'].apply(lambda x:reduce(lambda y,z:int(y)+int(z),list(x)))
        self.transfer_situation=situation





    def trade(self):
        pass






