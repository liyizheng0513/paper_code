# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 15:36:48 2017

@author: lenovo
"""

import datetime
from list import *
from script import *
#from WindPy import w
import talib
import tushare as ts
import numpy as np
import pandas as pd

#w.start()


class point:
    def __init__(self, num, close):
        self.num = num
        self.close = close

    def __lt__(self, other):
        if self.close < other.close:
            return True
        else:
            return False


class MACD_split:
    def __init__(self, priceSeries):
        self.close = priceSeries
        self.doubtTop = []
        self.doubtBottom = []
        self.doubtPoint = []
        self.comfirm_point_list = []
        self.dea = pd.DataFrame({})
        self.point_situation = pd.DataFrame({})
        self.boduan = pd.DataFrame({})

    def split_price(self):
        DEA = talib.MACD(self.close.values)[1]
        DEA = pd.Series(DEA, index=self.close.index)
        DEA = DEA.dropna()
        DEA_value = DEA.values
        close = self.close[self.close.shape[0] - DEA.shape[0]:]
        self.dea = DEA.copy()
        self.close = close.copy()
        close_value = close.values
        Top = True
        Bottom = True
        for num in range(1, close.shape[0]):
            dea_now = DEA_value[num]
            close_now = close_value[num]

            if dea_now > 0:
                j = num - 1
                flag_L = True
                flag_R = True
                LT, RT = 0, 0
                while flag_L and j > 0:
                    if DEA_value[j] < 0 and close_value[
                        j] == np.min(close_value[j:num + 1]):
                        LT = j
                        flag_L = False
                    if close_value[j] > close_now:
                        flag_L = False
                    '''
                    if self.doubtPoint:
                        if j < self.doubtPoint[-1]:
                            flag_L = False
                         '''
                    j -= 1

                j = num + 1
                while flag_R and j < close.shape[0]:
                    if DEA_value[j] < 0 and close_value[
                        j] == np.min(close_value[num:j + 1]):
                        RT = j
                        flag_R = False

                    if close_value[j] > close_now:
                        flag_R = False
                    j += 1
                # print LT, num, RT
                if LT > 0 and RT > 0 and close_now >= np.max(
                        close_value[LT:RT + 1]):
                    if Top:
                        self.doubtTop.append(num)
                        self.doubtPoint.append(num)
                        Top = False
                        Bottom = True

            if dea_now < 0:
                j = num - 1
                flag_L = True
                flag_R = True
                LT, RT = 0, 0
                while flag_L and j > 0:
                    if DEA_value[j] > 0 and close_value[
                        j] == np.max(close_value[j:num + 1]):
                        LT = j
                        flag_L = False

                    if close_value[j] < close_now:
                        flag_L = False

                    if self.doubtPoint:
                        if j < self.doubtPoint[-1]:
                            flag_L = False

                    j -= 1

                j = num + 1
                while flag_R and j < close.shape[0]:
                    if DEA_value[j] > 0 and close_value[
                        j] == np.max(close_value[num:j + 1]):
                        RT = j
                        flag_R = False

                    if close_value[j] < close_now:
                        flag_R = False

                    j += 1
                # print LT,num,RT
                if LT and RT and close_now <= np.min(close_value[LT:RT + 1]):
                    if Bottom:
                        self.doubtBottom.append(num)
                        self.doubtPoint.append(num)
                        Bottom = False
                        Top = True

    def point_delete(self):
        point_list = self.doubtPoint
        close = self.close
        l = LinkList()
        l.initlist([point(num, close.ix[num]) for num in point_list])
        p = l.head
        close_1 = 1.0 / close

        while p.next != 0:
            g = p
            d = p.next
            p = p.next

            if g > d:

                if close.ix[
                   g.data.num:d.data.num + 1
                   ].max() > close.ix[
                    g.data.num] > close.ix[
                    d.data.num] == close.ix[
                                   g.data.num:d.data.num
                                           + 1].min():
                    print 1
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])

                    if g.prev == 0:
                        l.delete(g)
                        p = g.next

                    elif d.next == 0:
                        d0 = g.prev
                        l.delete(max(d0, d))
                        l.delete(g)
                        p = min(d0, d)

                    else:
                        d0 = g.prev
                        g1 = d.next
                        if g > g1:
                            l.delete(d0)
                            l.delete(g)
                            if d0.prev != 0:
                                p = d0.prev
                            else:
                                p = d

                        if g < g1 and d0 < d:
                            l.delete(g)
                            l.delete(d)
                            p = d0
                            p = d.next
                        if g < g1 and d0 > d:
                            l.delete(d0)
                            l.delete(g)
                            if d0.prev != 0:
                                p = d0.prev
                            else:
                                p = d

                if close.ix[
                   g.data.num:d.data.num + 1
                   ].max() == close.ix[
                    g.data.num] > close.ix[
                    d.data.num] > close.ix[
                                  g.data.num:d.data.num + 1
                                  ].min():
                    print 2
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])

                    if d.next == 0:
                        l.delete(d)
                        break
                    elif g.prev == 0:
                        g1 = d.next
                        l.delete(min(g, g1))
                        l.delete(d)
                        p = max(g, g1)
                    else:
                        d0 = g.prev
                        g1 = d.next

                        if d0 < d and g > g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                        if d0 < d and g < g1:
                            l.delete(d)
                            l.delete(g)
                            p = d0

                        if d0 > d and g < g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                        if d0 > d and g > g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                if close.ix[
                   g.data.num:d.data.num + 1
                   ].max() > close.ix[
                    g.data.num] > close.ix[
                    d.data.num] > close.ix[
                                  g.data.num:d.data.num + 1
                                  ].min():
                    print 3
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])
                    if d.next == 0:
                        l.delete(d)
                        l.delete(g)
                        break
                    elif g.prev == 0:
                        g1 = d.next
                        l.delete(g)
                        l.delete(d)
                        p = g1
                    else:
                        d0 = g.prev
                        g1 = d.next

                        l.delete(g)
                        l.delete(d)
                        p = d0

            if g < d:

                if close_1.ix[
                   g.data.num:d.data.num + 1
                   ].max() > close_1.ix[
                    g.data.num] > close_1.ix[
                    d.data.num] == close_1.ix[
                                   g.data.num:d.data.num + 1
                                   ].min():
                    print 4
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])

                    if g.prev == 0:
                        l.delete(g)
                        p = g.next
                    elif d.next == 0:
                        d0 = g.prev
                        l.delete(min(d0, d))
                        l.delete(g)
                        p = max(d0, d)

                    else:
                        d0 = g.prev
                        g1 = d.next
                        if g < g1:
                            l.delete(d0)
                            l.delete(g)
                            if d0.prev != 0:
                                p = d0.prev
                            else:
                                p = d
                        if g > g1 and d0 > d:
                            l.delete(g)
                            l.delete(d)
                            p = d0
                        if g > g1 and d0 < d:
                            l.delete(d0)
                            l.delete(g)
                            if d0.prev != 0:
                                p = d0.prev
                            else:
                                p = d

                if close_1.ix[
                   g.data.num:d.data.num + 1
                   ].max() == close_1.ix[
                    g.data.num] > close_1.ix[
                    d.data.num] > close_1.ix[
                                  g.data.num:d.data.num +
                                          1].min():
                    print 5
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])

                    if d.next == 0:
                        l.delete(d)
                        break
                    elif g.prev == 0:
                        g1 = d.next
                        l.delete(max(g, g1))
                        l.delete(d)
                        p = min(g, g1)
                    else:
                        d0 = g.prev
                        g1 = d.next

                        if d0 > d and g < g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                        if d0 > d and g > g1:
                            l.delete(d)
                            l.delete(g)
                            p = d0

                        if d0 < d and g > g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                        if d0 < d and g < g1:
                            l.delete(d)
                            l.delete(g1)
                            p = g

                if close_1.ix[
                   g.data.num:d.data.num + 1
                   ].max() > close_1.ix[
                    g.data.num] > close_1.ix[
                    d.data.num] > close_1.ix[
                                  g.data.num:d.data.num +
                                          1].min():
                    print 6
                    print str(close.index[g.data.num]) + " === " + str(close.index[d.data.num])

                    if d.next == 0:
                        l.delete(d)
                        l.delete(g)
                        break
                    elif g.prev == 0:
                        g1 = d.next
                        l.delete(g)
                        l.delete(d)
                        p = g1
                    else:
                        d0 = g.prev
                        g1 = d.next

                        l.delete(g)
                        l.delete(d)
                        p = d0

        p = l.head
        point_list = []
        flag = True
        while flag:
            point_list.append(p.data.num)
            if p.next == 0:
                flag = False
            p = p.next
        point_list.sort()
        self.doubtPoint = point_list

    def split_result(self):
        point = self.doubtPoint
        point_attr = [0 for i in range(len(point))]
        for i in range(len(point)):
            if point[i] in self.doubtTop:
                point_attr[i] = "Top"
            else:
                point_attr[i] = "Bottom"
        point_situation = pd.DataFrame({'point': point,
                                        'point_date': self.close.iloc[point].index,
                                        'point_price': self.close.iloc[point].values,
                                        'point_dea': self.dea.iloc[point].values,
                                        'point_type': point_attr})
        point_situation = point_situation.sort_values("point_date")
        self.point_situation = point_situation

    def comfirm_point(self):
        point_situation = self.point_situation
        startdate = []
        enddate = []
        start_point = []
        end_point = []
        comfirmdate = []
        startprice = []
        endprice = []
        comfirmprice = []
        comfirmpoint = []
        bdtype = []
        prevreturns = []
        afterreturns = []
        continue_ratio = []
        returns = []
        for i in range(len(self.point_situation) - 1):
            start = point_situation.ix[i]
            end = point_situation.ix[i + 1]
            start_date = start.point_date
            end_date = end.point_date
            start_mark = start.point_type
            startprice.append(start.point_price)
            endprice.append(end.point_price)
            start_point.append(start.point)
            end_point.append(end.point)
            if start_mark == "Top":
                bd_mark = "decline"
            else:
                bd_mark = "raise"
            bdtype.append(bd_mark)
            startdate.append(start_date)
            enddate.append(end_date)
            returns.append(end.point_price / start.point_price - 1)
            priceseries = self.close.ix[start_date:end_date]
            dea = self.dea.ix[start_date:end_date]
            des = len(dea) - 1
            for j in range(len(dea)):
                if bd_mark == "decline":
                    if dea[j] < 0 and priceseries[
                        j] == priceseries[:j + 1].min():
                        des = j
                        break

                if bd_mark == "raise":
                    if dea[j] > 0 and priceseries[
                        j] == priceseries[:j + 1].max():
                        des = j
                        break
            comfirmpoint.append(list(self.dea.index).index(dea.index[des]))
            comfirm_date = priceseries.index[des]
            comfirm_price = self.close.ix[priceseries.index[des]]
            comfirmprice.append(comfirm_price)
            comfirmdate.append(comfirm_date)
            prev_returns = comfirm_price / start.point_price - 1
            after_returns = end.point_price / comfirm_price - 1
            prevreturns.append(prev_returns)
            afterreturns.append(after_returns)
            continue_ratio.append(after_returns / prev_returns)
        columns = [
            'start_point',
            'end_point',
            'start_date',
            'end_date',
            'start_price',
            'end_price',
            'comfirmpoint',
            'prevtime',
            'aftertime',
            'timedelta',
            'bd_type',
            'comfirm_date',
            'comfirm_price',
            'returns',
            'prevreturns',
            'afterreturns',
            'continue_ratio']
        self.boduan = pd.DataFrame({'start_point': start_point,
                                    'end_point': end_point,
                                    'start_date': startdate,
                                    'end_date': enddate,
                                    'start_price': startprice,
                                    'end_price': endprice,
                                    'comfirmpoint': comfirmpoint,
                                    'prevtime': np.array(comfirmpoint) - np.array(start_point),
                                    'aftertime': np.array(end_point) - np.array(comfirmpoint),
                                    'timedelta': -np.array(start_point) + np.array(end_point),
                                    'bd_type': bdtype,
                                    'comfirm_date': comfirmdate,
                                    'comfirm_price': comfirmprice,
                                    'returns': returns,
                                    'prevreturns': prevreturns,
                                    'afterreturns': afterreturns,
                                    'continue_ratio': continue_ratio},
                                   columns=columns)

        end_date = enddate[-1]
        bd_type = bdtype[-1]
        lastclose = self.close.ix[end_date:]
        lastdea = self.dea.ix[end_date:]
        date = ""
        if bd_type == "raise":
            for i in range(1,lastclose.shape[0]):
                if lastclose.iloc[i] == lastclose[:i + 1].min() and lastdea.iloc[i] < 0:
                    date = lastclose.index[i]
                    break

        if bd_type == "decline":
            for i in range(1,lastclose.shape[0]):
                if lastclose.iloc[i] == lastclose[:i + 1].max() and lastdea.iloc[i] > 0:
                    date = lastclose.index[i]
                    break
        if date:
            comfirmdate.append(date)
        self.comfirm_point_list = comfirmdate

    def run(self):
        self.doubtTop = []
        self.doubtBottom = []
        self.doubtPoint = []
        self.dea = pd.DataFrame({})
        self.point_situation = pd.DataFrame({})
        self.boduan = pd.DataFrame({})
        self.split_price()
        self.point_delete()
        self.split_result()
        self.comfirm_point()

    def now_situation(self):
        comfirm_point = self.comfirm_point_list[-1]
        boduan = self.boduan
        end_date = boduan.iloc[-1].end_date
        if comfirm_point > end_date:
            return comfirm_point, boduan.iloc[-2].bd_type
        else:
            return comfirm_point, boduan.iloc[-1].bd_type

        
        
    


def get_data(code, field, period, start, end):
    dat = w.wsd(
        code,
        ",".join(field),
        start,
        end,
        "PriceAdj=F;Period=%s" %
        period)
    strtime = map(
        lambda x: x.strftime("%Y-%m-%d") + " 15:00",
        dat.Times)

    df = pd.DataFrame(
        np.array(
            dat.Data).T, index=map(
            lambda x: datetime.datetime.strptime(
                x, "%Y-%m-%d %H:%M"), strtime), columns=field)
    return df


def ts_data(code, start, end, freq):
    data = ts.get_k_data(code, start, end, ktype=freq, index=True)
    data['date'] = (
        data['date'] +
        " 15:00:00").map(
        lambda x: datetime.datetime.strptime(
            x,
            "%Y-%m-%d %H:%M:%S"))
    data = data.set_index("date")
    return data


def summary(code, filepath, outfilefold):
    min_data = pd.read_excel(filepath)
    min_data['time'] = min_data['time'].map(
        lambda x: datetime.datetime.strptime(
            str(x), "%Y-%m-%d %H:%M:%S"))
    min_data = min_data.set_index("time")
    start = min_data.index[0].strftime("%Y-%m-%d")
    end = min_data.index[-1].strftime("%Y-%m-%d")
    code_data = ts_data(code, start, end, "D")
    for s in code_data.index:
        if s not in min_data.index:
            code_data = code_data.drop(s)
    min_data_split = MACD_split(min_data.close)
    code_data_split = MACD_split(code_data.close)
    code_data_split.run()
    min_data_split.run()
    summary_data = min_data_split.close
    summary_data = pd.DataFrame(
        summary_data.values,
        index=summary_data.index,
        columns=['minclose'])
    replace = [np.nan for i in range(summary_data.shape[0])]
    summary_data['day_close'] = replace
    summary_data['min_point'] = replace
    summary_data['day_point'] = replace
    summary_data['day_close'].ix[
        code_data_split.close.index] = code_data_split.close
    summary_data['day_point'].ix[
        code_data_split.point_situation.point_date] = code_data_split.close.ix[
        code_data_split.point_situation.point_date]
    summary_data['min_point'].ix[
        min_data_split.point_situation.point_date] = min_data_split.close.ix[
        min_data_split.point_situation.point_date]

    duan_num, duan_detail = mapping(
        code_data_split.boduan, min_data_split.boduan)
    for i in range(len(duan_detail)):
        ithbd = code_data_split.boduan.ix[i]
        start = ithbd.start_date.strftime("%Y-%m-%d")
        end = ithbd.end_date.strftime("%Y-%m-%d")
        duan_detail[i].to_excel(
            outfilefold +
            "\\%s" %
            code[
                :6] +
            "-%s" %
            start +
            "-%s.xlsx" %
            end)
    code_data_split.boduan.to_excel(
        outfilefold + "\\%s" %
        code[
            :6] + "-dayboduan.xlsx")
    min_data_split.boduan.to_excel(
        outfilefold + "\\%s" %
        code[
            :6] + "-minboduan.xlsx")
    summary_data.to_excel(outfilefold + "\\%s" % code[:6] + "--summary.xlsx")
    return min_data_split, code_data_split
