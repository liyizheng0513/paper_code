#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 10:55:24 2017

@author: liyizheng
"""

def n_subset(total, num):

    if total == 1 and num == 1:
        return [[0]]

    elif total == 1 and num > 1:
        return
        print "error"

    elif num == 1:
        result = []
        for s in range(total):
            result.append([s])
        return result

    set_n=n_subset(total -1 , num - 1)
    for i in range(len(set_n)):
        temp = set_n[i]
        temp.append(total)
        set_n[i] = temp

    result = list()
    result.extend(set_n)
    result.extend(n_subset(total - 1, num))
    return result