import numpy as np 
import matplotlib.pyplot as plt
import emcee
import csv

from sgp4propagator import SGP4

'''
These scripts are from this Jupyter notebook
https://github.com/aerospaceresearch/orbitdeterminator/blob/solving_orbital_elements_using_mcmc/orbitdeterminator/mcmc_doppler_determination/08b_mcmc_with_orbital_parameters.ipynb

For solving this problem by MCMC method,
we need to find the optimum likelihood function
'''

def random_a():
    return 4e3 + 6e3 *abs(np.random.rand())

def random_ecc():
    return np.random.rand()*0.01

def random_inc():
    return np.random.rand()*270

def random_raan():
    return np.random.rand()*360

def random_argp():
    return np.random.rand()*360

def random_nu():
    return np.random.rand()*180

nwalkers = 100
ndim = 6
MCMC_steps = 100

walkers = []
for i in range(nwalkers):
    walker = np.array([random_a(), random_inc(), random_raan(), random_ecc(),  random_argp(), random_nu()])
    walkers.append(walker)
walkers = np.array(walkers)

state_vectors = []
epochs = []
with open('./STARLINK-1401.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        state_vectors.append([ float(i) for i in row[1:] ])
        epochs.append( int(row[0]) )

def lnprob( param ):
    """
    param = [a, inc, raan, ecc, argp, nu]
    """
    a, inc, raan, ecc, argp, nu = param
    ### Limit the parameter space ###
    
    if a < 4e3:
        return -np.inf
    
    if (ecc < -1) or (ecc > 1) :
        return -np.inf
    
    if (inc < 20) or (inc > 270):
        return -np.inf

    if abs(raan) > 360:
        return -np.inf
    
    if abs(argp) > 360:
        return -np.inf
    
    if abs(nu) > 180:
        return -np.inf

    propagator = SGP4()
    propagator.compute_necessary_kep(param, b_star=0)

    # mean absolute percentange error
    mape = 0.0
    for index, time in enumerate(epochs):
        if index == 0:
            continue
        gap = time - epochs[0]
        propagated = propagator.propagate(0, gap)[-1]
        mape += abs((state_vectors[index] - propagated)/state_vectors[index])
    
    mape /= len(epochs)
    mape = sum(mape) / len(mape)
    return 1 - mape

print(" MCMC running with {} walkers, {} Steps".format(nwalkers, MCMC_steps))
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, threads=8)
pos, prob, state = sampler.run_mcmc(walkers, MCMC_steps, progress=True)
print(sum(sampler.chain[-1])/nwalkers)