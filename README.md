# asfpm2020-demo

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Objectives

- Discuss Deterministic and Probabilistic Systems
- Discuss the limits of what we can claim to know
- Discuss how we can make decisions inlight of not knowing something now or in the future

## Deterministic
A deterministic system has no randomness at all, for a given input, there is a known output.
![](images/Deterministic.jpg)

## An example Deterministic System
In this process for a 100 year precip (if we actually could say we knew what that was) we compute a flow (which is not likely to be the 100 year flow) which produces a stage, and then a damage...

![](images/DeterministicProcess2.jpg)

## Probabilistic
A probabilistic system introduces randomness into the system by varying things like initial conditions, and as a comparitive definition to our deterministic definition: In a probabilistic system, for a given input and a set of random initial conditions, we produce a distribution of outputs. 

![](images/Probabilistic.jpg)

## An example Probabilistic System

### Rainfall Runoff

This series of images helps to show more what a truthful representation of a system might be - firstly, for the same precipitation above, which we called the 100 year rainfall, we specifiy it as a given peak precip. We can talk more about what it might represent later, maybe we could say here "our best estimate peak 100 year precipitation..."

![](images/RainfallRunoff_Probabilistic3.jpg)

### Hydraulics

That precipitation as you might imagine above could realistically producs a range of flows. If we were to take the same flow as produced before in the deterministic model and imagine using a probabilistic model for the computation of stage (or water depth at a structure) we would see a range of depths because we dont really know the initial conditions or behaviors of the system.

![](images/Hydraulics_Probabilistic3.jpg)

### Damages

As you see above, the deterministic flow could really produce a range of depths at the structure, if we were to take that same deterministic depth and compute a probabilistic damage, we see there could really be a range of damages because we dont really know everything about what would result in damages in an "average" house.

![](images/Economics_Probabilistic3.jpg)

## Getting back to that "we dont really know the 100 year flow" bit...
Examples in Jupyter Notebooks for how we can use bootstrapping methods used in Probabilistic Flood Hazards Studies to express our limited knowledge due to limited observations:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Dewberry/asfpm2020-demo/master)

![](images/bootstraps.gif)

# Combining It all together with Event Sampling and Monte Carlo
You might be wondering, how do we get this right? There are so many possible outcomes, how can we combine this correctly? The answer is simple, composition of functions with Riemann Integration obviously... (mathematicians think they are cool). The common language for this is A Systems Event Based Monte Carlo. 

![](images/sampling.gif)

In this type of modeling framework, a series of deterministic runs, each with a randomized initial condition (which can be correlated or the same across models e.g. starting pool in the reservoirs if they are represented in many models) with each simulated event within a realization we are evaluating natural variability, with each realization we are evaluating our knowledge uncertainties. This gives us the ability to express our inability to know,and the natural variability of our sytems and combine the models into a singular system model that can support decision making.

![](images/gridded_compute.gif)

Through this type of modeling each event is equally likely to occur, so the resulting floodplains and damages can be utilized to describe the distribution of expected losses through simple computations like the one shown above.

# An Example Study

## Study Area
In this example, we had a study area on a regulated river with a levee providing risk mitigation to an area with many buildings. An empirical frequency curve with uncertainty was developed and utilized to describe the flow in the river and how the regulation of the upstream dam impacts the flow boundary condition. A few historic shapesets were leveraged for scaling the flod hydrograph. 

![](images/bootstrapped_HS.jpg)

The area had two locations that were modeled as likely breach locations (these are signified by the yellow dots in the image below). The breach locations included fragility curves to describe the likelihood that the levee might breach when loaded. These were one of the initial conditions sampled within the hydrauilcs model. We computed 10,000 events using HEC-WAT with the Hydrologic Sampler, HEC-RAS, the Fragility Curve Sampler, a consequence engine, and the AEP_Grid to produce the results shown in the images that follow.

![](images/StudyArea.jpg)

As we showed in the images above, we can create a summary grid from each sampled event to produce a database that stores how many times a gridcell gets depth above ground. The image below is a map that represents that database. As you can see, there is variation in the number of times the cells behind a levee get wet. This is due to the presence or absence of a breach, which location breached, if one breached before the other, the peak flow, the shape of the hydrograph, topographical relief, and many other conditions governing the way flow gets converted into depth. Even though the levee may have a specified overtopping frequency for its design, all cells within the leveed area will not necessarily get wet the same number of times, that depends on the characteristics of the events themselves.

![](images/timesWet.jpg)

This grid can be easily converted into an Annual Exceedance Probability grid by simply dividing by the number of events that were used to create it. in out case there were 10,000 events. The cells now represent a likelihood of getting water above the ground elevation. Similar grids can be constructed from any sort of output parameter and threshold criteria (e.g. a Annual Velocity Exceedance Grid which represents likelihood of Velocity over some threshold).

![](images/AEP_WithBreaches.jpg)

![](images/AEP_Structure.jpg)
![](images/EAD_Structure.jpg)
