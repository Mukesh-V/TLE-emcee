import json
import math
import numpy as np

def covariance_matrix():
    file = open('labels.json', 'r')
    satellites = json.load(file)
    file.close()

    whole_data = []
    for satellite in satellites:
        # For Gibbs 
        # [a, ecc, inc, argp, raan, nu]
        row = [satellite['sma'], satellite['ecc'], satellite['inc'], satellite['aop'], satellite['ran'], satellite['man']]
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