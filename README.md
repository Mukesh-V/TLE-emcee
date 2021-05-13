### OrbitDeterminator KepElems Estimation by emcee MH-MCMC sampler

I am Mukesh V from IIT-Madras. This repository holds my second idea for **gsoc21-a-od2 : Efficient optimization strategy for orbit determination.**

gibbs and sgp4propagator scripts are cloned from kep_determination and propagation directories of [aerospaceresearch/orbitdeterminator](https://github.com/aerospaceresearch/orbitdeterminator/tree/master/orbitdeterminator)

In case, you are interested in using this repo locally, making a venv is your choice :)
```py
    pip install -r requirements.txt
    # or
    python3 -m pip install -r requirements.txt
```

I propose an emcee-based model which samples from a 6 dimensional space with likelihood calculated by MSE of 
positional state vectors
``` py
    # Difference based on state vectors propagated by sgp4
    python3 mcmc_sgp4.py
```

The datasets were generated from TLEs publicly available at [Celestrak](https://www.celestrak.com/NORAD/elements/) by a Python astronomy library [Skyfield](https://rhodesmill.org/skyfield/). Some of the TLEs are duplicated between categories; Skyfield couldn't generate data for few others. So, I had to remove few of them manually. The final list of TLEs are in the *celestrak* folder : there are totally, 1616 unique satellites!
``` py
    # generates a labels.json file 
    python3 label.py
    # generates data for each satellite in labels.json
    python3 data.py
```