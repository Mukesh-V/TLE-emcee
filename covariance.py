import os
import csv
import json
import math
import numpy as np

def kep_covariance_matrix():
    file = open('labels.json', 'r')
    satellites = json.load(file)
    file.close()

    whole_data = []
    for satellite in satellites:
        row = [satellite['a'], satellite['inc'], satellite['raan'], satellite['ecc'], satellite['argp'], satellite['nu']]
        whole_data.append(row)

    ndim = len(row)
    ndata = len(whole_data)
    whole_data = np.array(whole_data)
    means = np.mean(whole_data, axis=0)

    covariance = np.zeros(ndim ** 2).reshape(ndim, ndim)
    for i in range(ndim):
        for j in range(ndim):
            for k in range(ndata):
                if math.isnan(whole_data[k][i]):
                    print(satellites[k]['name'])
                covariance[i][j] += ( (whole_data[k][i] - means[i]) * (whole_data[k][j] - means[j]) ) / (ndata - 1)

    print('Covariance matrix')
    with np.printoptions(precision=3, suppress=True):
        print(covariance)
          
    return covariance

def state_vector_covariance_matrix():

    files_list = os.listdir('./data')
    whole_data = []
    for satellite in files_list:
        r = open('./data/' + satellite, 'r')
        reader = csv.reader(r)
        for row in reader:
            whole_data.append([ float(value) for value in row[1:] ])
        r.close()

    ndim = len(row[1:])
    ndata = len(whole_data)
    whole_data = np.array(whole_data)
    means = np.nanmean(whole_data, axis=0)
    
    covariance = np.zeros(ndim ** 2).reshape(ndim, ndim)
    for i in range(ndim):
        for j in range(ndim):
            for k in range(ndata):
                if math.isnan(whole_data[k][i]):
                    break
                covariance[i][j] += ( (whole_data[k][i] - means[i]) * (whole_data[k][j] - means[j]) ) / (ndata - 1)

    print('Covariance matrix')
    with np.printoptions(precision=3, suppress=True):
        print(covariance)
          
    return covariance
        