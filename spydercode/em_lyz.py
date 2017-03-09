#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:10:53 2017

@author: liyizheng
"""

import scipy.stats as sta
import copy
import numpy as np

def init_params_ols(model_list, ret_factor):
    B = []
    Sigma = []
    factor_returns = []
    alpha_mean = []
    alpha_list = []
    for model in model_list:
        B.append(model.params[1:].values)
        resid = model.resid
        Sigma.append((resid**2).sum() / (resid.shape[0] - 2))
        factor_returns.append(ret_factor[model.params[1:].index].values)
        alpha_mean.append((model.params.Intercept + model.resid).mean())
        alpha_list.append(model.params.Intercept)
    B = np.array(B)
    Sigma = np.array(Sigma)
    factor_returns = np.array(factor_returns)
    alpha_mean = np.array(alpha_mean)
    alpha_list=np.array(alpha_list)
    return B, Sigma, factor_returns, alpha_mean,alpha_list


def update_fund_para(g, T, alpha_mean):
	
	Sigma = g[1]
	theta = g[2]
	pi = theta[0]
	u = theta[1]
	sigma = theta[2]
	u_new = [sigma / (sigma + Sigma[i] / T) * alpha_mean[i] + Sigma[i]/T / (sigma + Sigma[i] / T) * u for i in range(len(Sigma))]
	sigma_new = [1 / (1 / sigma + T / Sigma[i]) for i in range(len(Sigma))]
	pi_new = []
	for i in range(len(Sigma)):
		
		alpha_i = alpha_mean[i]
		Demon = 0.0
		pi_i = []
		for j in range(len(sigma)):
			Demon += pi[j] * phi(alpha_i - u[j], 0, sigma[j])
		for j in range(len(sigma)):
			number = pi[j] * phi(alpha_i - u[j], 0, sigma[j])
			if Demon != 0:
				pi_i.append(number / Demon)
			else:
				pi_i.append(0.0)

		pi_new.append(pi_i)
	pi_new = np.array(pi_new)
	return np.array([pi_new, u_new, sigma_new])


def update_B_Sigma(fund_theta, factor_returns, ret_fund):
    T = ret_fund.shape[1]
    B_new = []
    Sigma_new = []
    pi = fund_theta[0]
    u = fund_theta[1]
    sigma = fund_theta[2]
    for i in range(ret_fund.shape[1]):
        alpha_m = pi[i].dot(u[i])
        alpha_var = pi[i].dot(u[i]**2) - 2 * alpha_m * \
            pi[i].dot(u[i]) + alpha_m**2 + pi[i].dot(sigma[i])
        Y_i = ret_fund.ix[:, i].values - alpha_m
        F = factor_returns[i]
        beta_i = np.linalg.inv((F.T).dot(F)).dot(F.T).dot(Y_i)
        sigma_i = 1.0 / T * \
            ((ret_fund.ix[:, i].values - beta_i.dot(F.T) - alpha_m)
             ** 2).sum() + alpha_var
        B_new.append(beta_i)
        Sigma_new.append(sigma_i)
    return B_new, Sigma_new


def get_model_MLE(ret_fund, ret_factor, initial_theta, model_list,epsilon = 0.001, iter_num = 500):
	B, Sigma, factor_returns, alpha_mean, alpha_list = init_params_ols(model_list, ret_factor)
	T = ret_fund.shape[1]
	theta0 = get_theta_MLE(initial_theta,alpha_list)
	g =np.array([B, Sigma, theta0])
	for it in range(iter_num):
		old_g = copy.deepcopy(g)
		fund_theta = update_fund_para(g, T, alpha_mean)
		B_new, Sigma_new = update_B_Sigma(fund_theta, factor_returns, ret_fund)
		M = 100
		xmat = []
		for i in range(fund_theta.shape[1]):
			alpha_i = GMM_generator(fund_theta[:,i,:], M)
			xmat.extend(list(alpha_i))
		xmat = np.array(xmat)
		last_theta = g[-1]
		theta_new = get_theta_MLE(last_theta, xmat)
		g = np.array([B_new, Sigma_new, theta_new])
		if np.abs(g - old_g).sum() < epsilon:
			print "在第%d次迭代中退出" % i
			break
	return g



def GMM_generator(theta, test_num):
	pi = theta[0]
	u = theta[1]
	sigma = theta[2]
	xmat = np.zeros(test_num)
	for i in range(test_num):
		x = np.random.random(1)
		if x < pi[0]:
			xmat[i] = np.random.normal() * np.sqrt(sigma[0]) +u[0]
		elif x < pi[0] + pi[1]:
			xmat[i] =  np.random.normal() * np.sqrt(sigma[1]) +u[1]
		else:
			xmat[i] = np.random.normal() * np.sqrt(sigma[2]) +u[2]
	return xmat

"""
def e_step_theta(initial_theta, alpha_list):
	pi = initial_theta[0]
	u = initial_theta[1]
	sigma = initial_theta[2]
	L = initial_theta.shape[1]
	MN = len(alpha_list)
	P = np.zeros([MN, L])
	alpha_list_ravel = alpha_list.reshape(-1,1)
	para = np.array([u,sigma])
	phi_matrix = np.apply_along_axis(lambda x:row_fill(x[0],0,para), 1, alpha_list_ravel)
	phi_matrix = np.nan_to_num(phi_matrix)
  	P = phi_matrix * pi
	P = P / P.sum(axis=1).reshape(-1,1)
  	P = np.nan_to_num(P)
	return P
"""


def get_theta_MLE(initial_theta, alpha_list, epsilon=0.0001, iter_num=500):
    pi = initial_theta[0]
    u = initial_theta[1]
    sigma = initial_theta[2]
    L = initial_theta.shape[1]
    MN = len(alpha_list)
    P = np.zeros([MN, L])
    alpha_list_ravel = alpha_list.reshape(-1, 1)
    for i in range(iter_num):
        old_mle = copy.deepcopy(np.array([pi, u, sigma]))
        para = np.array([u, sigma])
        phi_matrix = np.apply_along_axis(
            lambda x: row_fill(x[0], 0, para), 1, alpha_list_ravel)
        phi_matrix = np.nan_to_num(phi_matrix)

        P = phi_matrix * pi
        Q = P.sum(axis=1)
        Q[Q == 0] = 1
        Q = Q.reshape(-1, 1)
        P = P / Q
        P = np.nan_to_num(P)
        P = copy.deepcopy(P)
        Q = P.sum(axis=0)
        Q[Q == 0] = 1
        print Q
        u = P.T.dot(alpha_list) / Q
        sigma = (P.T.dot(alpha_list**2) - 2 * u * P.T.dot(alpha_list) +
                 (u**2) * P.T.sum(axis=1)) / Q
        pi = Q / MN
        theta = np.array([pi, u, sigma])
        print theta
        print i
        print "============================="
        if np.sum(abs(theta - old_mle)) < epsilon:
            print "在第%d次迭代中退出" % i
            break
    return theta




def phi(x, u, sigma):
    return np.sqrt(1.0 / (np.pi * 2 * sigma)) * np.exp(-1.0 / (2 * sigma) * (x - u)**2)

def row_fill(x, axis, para):
	return np.apply_along_axis(lambda r:phi(x,r[0],r[-1]), axis, para)





