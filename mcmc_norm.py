import numpy as np 
import emcee
import csv
import math
import corner
from numpy.lib.function_base import cov

from covariance import state_vector_covariance_matrix
from sgp4propagator import SGP4

'''
The structure of this script is from this Jupyter notebook:
https://github.com/aerospaceresearch/orbitdeterminator/blob/solving_orbital_elements_using_mcmc/orbitdeterminator/mcmc_doppler_determination/08b_mcmc_with_orbital_parameters.ipynb

For solving this problem by MCMC method,
we need to find the optimum likelihood function and fair approximation of parameter space.
'''

'''
all distances are in kilometers.
with reference to data from ESA:
https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits#:~:text=A%20low%20Earth%20orbit%20(LEO,very%20far%20above%20Earth's%20surface.
Most of the satellites in celestrak folder are in LEO. 
'''
radius_earth = 6378.1
leo_min_altitude = 160
leo_max_altitude = 1000
geostationary_altitude = 35786

a_min = radius_earth + leo_min_altitude
a_max = radius_earth + leo_max_altitude
# a_max = radius_earth + geostationary_altitude
'''
We can parse arguments from the user for switching a_max
in case, the satellite is expected to be in a Molniya/Geostationary orbit.
'''

nwalkers = 50
ndim = 6
MCMC_steps = 1000

state_vectors = []
epochs = []
'''
each row has [timestamp, pos_x, pos_y, pos_z]
'''
with open('./1998-067PN.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        state_vectors.append([ float(i) for i in row[1:] ])
        epochs.append( int(row[0]) )

ndim_state_vectors = len(state_vectors[0])
ndata = len(state_vectors)

def scale(param):

    a, inc, raan, ecc, argp, nu = param
    a = a_min + ( a_max - a_min ) * a
    inc  *= 90
    raan *= 360
    ecc  *= 0.001
    argp *= 360
    nu   *= 360
    param = [a, inc, raan, ecc, argp, nu]

    return param

def lnprob( param, covariance ):
    """
    param = [a, inc, raan, ecc, argp, nu]
    """
    for value in param:
        if value < 0 or value > 1:
            return -np.inf

    param = scale(param)

    '''
    SGP4 script is from master branch of our orbitdeterminator repository 
    First attempt is SGP4 propagation with b_star coefficient = 0
    '''
    propagator = SGP4()
    propagator.compute_necessary_kep(param, b_star=0)

    error = 0.0
    for index, time in enumerate(epochs):
        '''
        The first row is considered as a reference : we use its timestamp as time = 0
        The nth row data has a significant gap in time.
        The SGP4 object propagates the orbit by time = nth row's time - row1's time
        We then compare the state vectors obtained from SGP4 and the state vectors 
        generated by data.py ( where Skyfield.api is used for generating state vectors from TLEs) 
        '''
        try:
            propagated = np.array(propagator.propagate(epochs[0], time)[-1][0:ndim_state_vectors]).reshape(1, ndim_state_vectors)
        except:
            return -np.inf
            
        error += np.array(state_vectors[index]).reshape(1, ndim_state_vectors) - propagated
    
    error /= len(epochs)
    error = error.T
    likelihood = -0.5 * np.dot(error.T, np.linalg.solve(covariance, error))
    
    if np.sum(abs(error.T)) < 100 or np.exp(likelihood) > 0.97:
        print(error.T[0])
        print(np.exp(likelihood))

    return likelihood

try:
    covariance = state_vector_covariance_matrix()
except:
    '''
        I have calculated the covariance matrix with help of data generated by data.py
        This covariance matrix is for Gaussian distribution of (x, y, z)
    '''
    covariance = [
                    [1413939.001, 351792.778, 190925.253], 
                    [351792.778, 1464920.216, -341469.837],
                    [190925.253, -341469.837, 2086747.891]
                 ]
    covariance = np.array(covariance)


# walkers holds the initial state of emcee walkers
walkers = []
for i in range(nwalkers):
    walker_state = []
    for index in range(ndim):
        walker_state.append( abs(np.random.rand()) )
    walkers.append(walker_state)
walkers = np.array(walkers)

print(" MCMC running with {} walkers, {} Steps".format(nwalkers, MCMC_steps))
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=[ covariance ], threads=8)
sampler.run_mcmc(walkers, MCMC_steps, progress=True)
samples = sampler.chain[:,0:,:].reshape((-1, ndim))

max_probability_points = np.where(sampler.lnprobability == sampler.lnprobability.max())
print('Exp( max lnprobability ) :', np.exp(sampler.lnprobability.max()))
best_sample = np.mean(sampler.chain[max_probability_points[0], max_probability_points[1]], axis=0)

parameter_labels = ['a', 'inc', 'raan', 'ecc', 'argp', 'nu']
best_sample = scale(best_sample)

for index, value in enumerate(best_sample):
    print(parameter_labels[index], ':', value)
fig = corner.corner(samples, labels=parameter_labels, show_titles=True, plot_datapoints=True, quantiles=[0.16,0.5, 0.84])
fig.savefig('corner.png')