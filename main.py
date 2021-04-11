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

nwalkers = 50
ndim = 6
MCMC_steps = 500

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

def lnprob( param, cov ):
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
    error = 0.0
    for index, time in enumerate(epochs):
        if index == 0:
            continue
        # time = epochs[1]
        gap = time - epochs[0]
        propagated = propagator.propagate(0, gap)[-1]
        error += state_vectors[1] - propagated
    
    error /= len(epochs)
    return -0.5 * np.dot(error, np.linalg.solve(cov, error))

np.random.seed(42)
means = np.random.rand(ndim)
cov = 0.5 - np.random.rand(ndim ** 2).reshape((ndim, ndim))
cov = np.triu(cov)
cov += cov.T - np.diag(cov.diagonal())
cov = np.dot(cov, cov)

print(" MCMC running with {} walkers, {} Steps".format(nwalkers, MCMC_steps))
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=[cov], threads=8)
sampler.run_mcmc(walkers, MCMC_steps, progress=True)
samples = sampler.chain[:,0:,:].reshape((-1, ndim))

for i in range(ndim):
    print(samples[:, i].mean())

xpts = range(0, nwalkers * MCMC_steps)
fig, axs = plt.subplots(3,2)
axs[0, 0].plot(xpts, samples[:, 0])
axs[0, 0].set_title('Semi-Major Axis')
axs[0, 1].plot(xpts, samples[:, 1])
axs[0, 1].set_title('Inclination')

axs[1, 0].plot(xpts, samples[:, 2])
axs[1, 0].set_title('Right Ascension of Ascending Node')
axs[1, 1].plot(xpts, samples[:, 3])
axs[1, 1].set_title('Eccentricity')

axs[2, 0].plot(xpts, samples[:, 4])
axs[2, 0].set_title('Argument of Periapsis')
axs[2, 1].plot(xpts, samples[:, 5])
axs[2, 1].set_title('True Anomaly')

plt.show()