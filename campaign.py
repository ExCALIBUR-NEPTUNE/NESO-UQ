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


#Set the parameters that can be modified in two_streams.template 
params = {
    #Number of particles
    #Should be integer but the MC sampler spits out real numbers
    #neso seems to cope regardless"
    'NP' :
    {"type" : "float", "default" : 7500},
    #Number density of particles
    'NUM_DENSITY' :
    {"type" : "float", "default" : 52.637890139143245},
    #Charge density
    'DENSITY' :
    {"type" : "float", "default" : 52.637890139143245},
    #PRNG seed
    #mashed keyboard to get a fixed seed, won't vary but convenient to set it here
    'SEED' :
    {"type" :"integer","default" : 284289374}
}


#List of variables to vary
vary = {
    'NP': cp.DiscreteUniform(5000,10000),
    'NUM_DENSITY':cp.Uniform(20,90.0)
}


encoder = uq.encoders.GenericEncoder(
    'two_streams.template',
    delimiter='$',
    target_filename='neso.xml'
)


decoder = uq.decoders.JSONDecoder('output.json',output_columns=['Gradient'])

execute = ExecuteLocal('{}/run.sh neso.xml'.format(os.getcwd()))

actions = Actions(CreateRunDirectory('/tmp'),
                  Encode(encoder), execute, Decode(decoder))

campaign = uq.Campaign(name='neso_mc_', params=params, actions=actions)


n_samps=256

my_sampler = uq.sampling.QMCSampler(vary, n_mc_samples = n_samps)

campaign.set_sampler(my_sampler)

#set to sequential or will try to run N in parallel where N=number of hyperthreads
#i.e. too many
campaign.execute(sequential=True).collate()

my_analysis = uq.analysis.QMCAnalysis(sampler=my_sampler, qoi_cols=["Gradient"])

campaign.apply_analysis(my_analysis)

results = campaign.get_last_analysis()


#Get some statistics - don't really know what I am doing here

mean = results.describe("Gradient", "mean")
var = results.describe("Gradient", "var")

print(mean)
print(var)

samples = results.samples

plt.hist(samples['Gradient'], 4)
plt.title(f"N_samples: {n_samps}")
plt.xlabel("Gradient")
plt.ylabel("freq")
plt.savefig("histogram.png")

samples_sort = np.sort(np.array(samples['Gradient']).squeeze())
iis = np.linspace(0,1,samples_sort.size)

plt.step(samples_sort, iis)
plt.title(f"N_samples: {n_samps}")
plt.xlabel("Gradient")
plt.ylabel("ecdf")
plt.savefig("ecdf.png")

results.plot_sobols_treemap('Gradient', figsize=(10, 10))
plt.axis('off');
plt.savefig("sobols.png")

sobols = results.sobols_first('Gradient')
print(sobols)
