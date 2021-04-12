import numpy as np 
import emcee
import csv
import corner

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

def random_a():
    return radius_earth + leo_max_altitude * abs(np.random.rand())

def random_ecc():
    return np.random.rand()*0.1

def random_inc():
    return abs(np.random.rand()*180)

def random_raan():
    return abs(np.random.rand()*360)

def random_argp():
    return abs(np.random.rand()*360)

def random_nu():
    return abs(np.random.rand()*360)

nwalkers = 50
ndim = 6
MCMC_steps = 500

# walkers holds the initial state of emcee walkers
walkers = []
for i in range(nwalkers):
    walker = np.array([random_a(), random_inc(), random_raan(), random_ecc(),  random_argp(), random_nu()])
    walkers.append(walker)
walkers = np.array(walkers)

state_vectors = []
epochs = []
'''
as of now, the csv holds 2 rows of data 
each row has [timestamp, pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
'''
with open('./STARLINK-1401.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        state_vectors.append([ float(i) for i in row[1:] ])
        epochs.append( int(row[0]) )

def lnprob( param, covariance ):
    """
    param = [a, inc, raan, ecc, argp, nu]
    """
    a, inc, raan, ecc, argp, nu = param
    ### Limit the parameter space ###
    
    if a < a_min or a > a_max:
        return -np.inf
    
    if ecc < -1 or ecc > 1 :
        return -np.inf
    
    if inc < 0 or inc > 180:
        return -np.inf

    if raan < 0 or raan > 360:
        return -np.inf
    
    if argp < 0 or argp > 360:
        return -np.inf
    
    if nu < 0 or nu > 360:
        return -np.inf

    '''
    SGP4 script is from master branch of our orbitdeterminator repository 
    First attempt is SGP4 propagation with b_star coefficient = 0
    '''
    propagator = SGP4()
    propagator.compute_necessary_kep(param, b_star=0)

    error = 0.0
    for index, time in enumerate(epochs):
        '''
        I have decided to use second row data for calculating error
        The first row is considered as a reference : we use its timestamp as time = 0
        The second row data has a significant gap in time.
        The SGP4 object propagates the orbit by time = row2's time - row1's time
        We then compare the state vectors obtained from SGP4 and the state vectors 
        generated by data.py ( where Skyfield.api is used for generating state vectors from TLEs) 
        '''
        if index == 0:
            continue
        gap = time - epochs[0]
        propagated = propagator.propagate(0, gap)[-1]
        '''
        Since value of semi-major axis is much larger than the other values,
        it might have a strong influence on the error. yet to research more on this.
        '''
        error += state_vectors[index] - propagated
    
    error /= len(epochs)
    return -0.5 * np.dot(error, np.linalg.solve(covariance, error))

'''
Started off by picking samples from n-dimensional Gaussian
Fortunately, there was a snippet in emcee docs as well :
https://emcee.readthedocs.io/en/stable/tutorials/quickstart/
'''
np.random.seed(1401)
means = np.random.rand(ndim)
covariance = 0.5 - np.random.rand(ndim ** 2).reshape((ndim, ndim))
covariance = np.triu(covariance)
covariance += covariance.T - np.diag(covariance.diagonal())
covariance = np.dot(covariance, covariance)

print(" MCMC running with {} walkers, {} Steps".format(nwalkers, MCMC_steps))
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=[covariance], threads=8)
sampler.run_mcmc(walkers, MCMC_steps, progress=True)
samples = sampler.chain[:,0:,:].reshape((-1, ndim))

parameter_labels = ['a', 'inc', 'raan', 'ecc', 'argp', 'nu']
for i in range(ndim):
    print(parameter_labels[i], ':', samples[:, i].mean())
fig = corner.corner(samples, labels=parameter_labels, show_titles=True, plot_datapoints=True, quantiles=[0.16,0.5, 0.84])
fig.savefig('corner.png')