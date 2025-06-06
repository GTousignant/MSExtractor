import numpy
import random
from numpy import arange as xrange  


def selIBEA(population, mu, alpha=None, kappa=.05, tournament_n=4):
    """IBEA Selector"""

    if alpha is None:
        alpha = len(population)

    # Calculate a matrix with the fitness components of every individual
    components = _calc_fitness_components(population, kappa=kappa)

    # Calculate the fitness values
    _calc_fitnesses(population, components)

    # Do the environmental selection
    population[:] = _environmental_selection(population, alpha)

    # Select the parents in a tournament
    parents = _mating_selection(population, mu, tournament_n)

    return parents


def _calc_fitness_components(population, kappa):
    """returns an N * N numpy array of doubles, which is their IBEA fitness """
    # DEAP selector are supposed to maximise the objective values
    # We take the negative objectives because this algorithm will minimise
    population_matrix = numpy.fromiter(
        iter(-x for individual in population
             for x in individual.fitness.wvalues),
        dtype=numpy.float64)
    pop_len = len(population)
    feat_len = len(population[0].fitness.wvalues)
    population_matrix = population_matrix.reshape((pop_len, feat_len))

    # Calculate minimal square bounding box of the objectives
    box_ranges = (numpy.max(population_matrix, axis=0) -
                  numpy.min(population_matrix, axis=0))

    # Replace all possible zeros to avoid division by zero
    # Basically 0/0 is replaced by 0/1
    box_ranges[box_ranges == 0] = 1.0

    components_matrix = numpy.zeros((pop_len, pop_len))
    for i in xrange(0, pop_len):
        diff = population_matrix - population_matrix[i, :]
        components_matrix[i, :] = numpy.max(
            numpy.divide(diff, box_ranges),
            axis=1)

    # Calculate max of absolute value of all elements in matrix
    max_absolute_indicator = numpy.max(numpy.abs(components_matrix))

    # Normalisation
    if max_absolute_indicator != 0:
        components_matrix = numpy.exp(
            (-1.0 / (kappa * max_absolute_indicator)) * components_matrix.T)

    return components_matrix


def _calc_fitnesses(population, components):
    """Calculate the IBEA fitness of every individual"""

    # Calculate sum of every column in the matrix, ignore diagonal elements
    column_sums = numpy.sum(components, axis=0) - numpy.diagonal(components)

    # Fill the 'ibea_fitness' field on the individuals with the fitness value
    for individual, ibea_fitness in zip(population, column_sums):
        individual.ibea_fitness = ibea_fitness


def _choice(seq):
    """Python 2 implementation of choice"""

    return seq[int(random.random() * len(seq))]


def _mating_selection(population, mu, tournament_n):
    """Returns the n_of_parents individuals with the best fitness"""

    parents = []
    for _ in xrange(mu):
        winner = _choice(population)
        for _ in xrange(tournament_n - 1):
            individual = _choice(population)
            # Save winner is element with smallest fitness
            if individual.ibea_fitness < winner.ibea_fitness:
                winner = individual
        parents.append(winner)

    return parents


def _environmental_selection(population, selection_size):
    """Returns the selection_size individuals with the best fitness"""

    # Sort the individuals based on their fitness
    population.sort(key=lambda ind: ind.ibea_fitness)

    # Return the first 'selection_size' elements
    return population[:selection_size]