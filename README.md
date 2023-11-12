# MPhys project: Modelling the role of anti-vaccination sentiment in disease outbreaks on a heterogeneous network

## Contents

- [MPhys project: Modelling the role of anti-vaccination sentiment in disease outbreaks on a heterogeneous network](#mphys-project-modelling-the-role-of-anti-vaccination-sentiment-in-disease-outbreaks-on-a-heterogeneous-network)
  - [Contents](#contents)
  - [Background](#background)
  - [Purpose and outcomes of the simulation](#purpose-and-outcomes-of-the-simulation)
    - [Purpose](#purpose)
    - [Outcomes](#outcomes)
  - [How the model works](#how-the-model-works)
  - [How to run the simulation](#how-to-run-the-simulation)
  - [Outputs](#outputs)
  - [Work still to be done](#work-still-to-be-done)

## Background

Hello! Thank you for taking an interest in my MPhys project. I created this code during the 2021/2022 academic year, and used its outputs to write my final Masters dissertation. That said, this repository is absolutely not in its final state - there are many code snippets to tidy, graphs to add, and more. Since my graduation, this has become a side project for me, so please don't expect progress to be swift!

## Purpose and outcomes of the simulation

### Purpose

This simulation was designed to model the interaction between two key facets of disease propagation: transmissability and vaccination uptake. While the simulation is designed to be non-specific to any particular disease, it currently uses some hard-coded parameters (R0 number, post-infection immunity time, etc) which were the best-known approximation of those values for COVID-19 as of March 2022. One application of this project is that this code can be altered for application to other infectious repiratory diseases, though I currently have no intention of adding alternative parameters myself.

### Outcomes

During my Masters project investigations, the simulation produced the following main conclusions:

- Higher anti-vaccination sentiment in the population leads to an exponential increase in the number of disease cases observed during an endemic outbreak
- Higher anti-vaccination sentiment can also increase the likelihood that a disease will become endemic by up to 11%
- Those who do not choose to become vaccinated carry a higher burden of cases than their regularly vaccinated counterparts, the magnitude of which is directly correlated to their number of physical contacts.

## How the model works

There are three main systems which interact to affect disease outcomes in the model:

- A disease transmission model: this is a relatively simple **SIRS model**, where individuals are always in one of three states: *susceptible* to disease, *infected* with disease, or *recovered* from disease (a temporary immunity state which eventually reverts back to susceptible).
- A vaccination system: individuals within the simulation are **regularly offered vaccination**, which they may choose to take up or turn down. If vaccination is accepted, an individual will enter an immune state for an extended period (functionally identical to the *recovered* state in the SIRS model).
- An opinion system: each individual **holds an opinion (either positive or negative) on vaccination**, and can influence their social contacts to adopt their same opinion. If the opinion is negative at the time a vaccination is offered to an individual, they will decline the vaccine. Otherwise, they will become vaccinated.

Each individual in the simulation has a list of social contacts (to whom they can spread their opinion) and a list of physical contacts (to whom they can spread disease). These lists will contain overlap, as is likely in the real world. The data for these contact numbers was taken from the POLYMOD dataset (please see the *Supplementary analysis* folder for more information).

## How to run the simulation

The full model code (used for analysis in my MPhys report and presentation) is accessed by running `main.py`. A pared-down, terminal user-friendly version of the program (the "public summary" component of my Masters Project) is available by running `covid_game.py`.

These scripts will import modules `vaccination.py`, `network.py` and `voter_model.py` from the modules folder, which contain auxillary functions which are used in the main simulation.

The simulation is designed for use from a console or terminal.

## Outputs
The user can see the progression of the simulation in real time, with two output options:
- Realtime statistics provided in a **table**
- Transmission/recovery events in a **list**

There is also the option to turn off terminal output.

## Work still to be done

The following parts of this repository still require work/updating to reach their final state:
- General cleaning of existing code and more in-depth commenting throughout
