#!/usr/bin/python3
# -------------------------------------------------
# Example script to run neso in easyvvuq framework
# Modify the run.sh script as needed for your enviroment
# ---------------------------------------------------

import os
import easyvvuq as uq
import chaospy as cp
import numpy as np
import matplotlib.pyplot as plt
from easyvvuq.actions import CreateRunDirectory, Encode, Decode, CleanUp, ExecuteLocal, Actions


#Set the parameters that can be modified in two_stream.template 
params = {
    #Number of particles
    #Should be integer but the MC sampler spits out real numbers
    #neso seems to cope regardless"
    'NP' :
    {"type" : "float", "default" : 400000},
    #Number density of particles
    'NUM_DENSITY' :
    {"type" : "float", "default" : 105},
    #Charge and number density
    'DENSITY' :
    {"type" : "float", "default" : 105},
    #PRNG seed
    #mashed keyboard to get a fixed seed, won't vary but convenient to set it here
    'SEED' :
    {"type" :"integer","default" : 284289374},
    #Initial particle velocity
    'VELOCITY' :
    {"type" : "float", "default" : 1.0}
}


#List of variables to vary
vary = {
    'DENSITY':cp.Uniform(94.5,115.5),
    'VELOCITY':cp.Uniform(0.9,1.10)
}


encoder = uq.encoders.GenericEncoder(
    'examples/two_stream/two_stream.template',
    delimiter='$',
    target_filename='neso.xml'
)

decoder = uq.decoders.JSONDecoder('output.json',output_columns=['PHI','X'])

execute = ExecuteLocal('{}/run.sh neso.xml'.format(os.getcwd()))

actions = Actions(CreateRunDirectory('/tmp'),
                  Encode(encoder), execute, Decode(decoder))

campaign = uq.Campaign(name='neso_pce_', params=params, actions=actions)


my_sampler = uq.sampling.PCESampler(vary, polynomial_order=3)

campaign.set_sampler(my_sampler)

#set to sequential or will try to run N in parallel where N=number of hyperthreads
#i.e. too many
campaign.execute(sequential=True).collate()

my_analysis = uq.analysis.PCEAnalysis(sampler=my_sampler, qoi_cols=["PHI","X"])

campaign.apply_analysis(my_analysis)

results = campaign.get_last_analysis()

#Not shure this is the best way
#Assume the X values are the same every time so we only get the first row
#of the dataframe
xvalues = results.samples['X'].iloc[[0]].to_numpy()

#Plot the moments/confidence intervals at each evaluation point of phi
results.plot_moments(qoi='PHI',ylabel="$\phi$",xlabel="$x$",xvalues=xvalues[0])
plt.savefig("moments.png")
#Plot the sobol indicies of each input variable as a function of X
results.plot_sobols_first(qoi='PHI',xlabel="$x$",xvalues=xvalues[0])
plt.savefig("sobols.png")
