import matplotlib.pyplot as plt
import numpy as np
import math
import sys
from pid import PID
from bicycle import Bicycle
import multiprocessing
import timeit

# TODO: develope a way to adapt mutation rate as the algorithm converges

class GA():
    def __init__(self, population, mutation, generations, bicycle):
        self.bicycle = bicycle
        self.population_size = population
        self.population = np.empty((self.population_size), dtype=object)
        self.mutation_rate = mutation
        self.crossover_point = 3
        self.chromosome_size = 6
        self.number_parents = int(math.sqrt(population))
        self.generations = generations
        self.eta = 5
        self.fittest = PID(bicycle.k)
        self.fittest.fitness = 1000000

    def setup(self):
        for i in range(self.population_size):
            k = np.empty((self.chromosome_size))
            k[0] = np.random.uniform(low=0, high=2)
            k[1] = np.random.uniform(low=0, high=0.1)
            k[2] = np.random.uniform(low=0, high=0.1)
            k[3] = np.random.uniform(low=0, high=10)
            k[4] = np.random.uniform(low=0, high=0.1)
            k[5] = np.random.uniform(low=0, high=0.1)
            pid = PID(k)

            self.population[i] = pid

    def evolve(self):
        i = self.generations
        while i > 0 and self.fittest.fitness > self.eta:
            print("Generation #%s" % (self.generations - i + 1))
            print("calculate fitness")
            self.fitness()
            print("select parents")
            parents = self.selection()
            print("crossover")
            self.crossover(parents)
            print("mutation")
            self.mutation()
            i = i - 1

        print("done evolving")
        return_dict = [0]
        self.bicycle.driveAlongPath(0, self.fittest, return_dict, 1)

        return self.fittest.k

    def fitness(self):
        # start_time = timeit.default_timer()
        #
        # dict = [0]*self.population.shape[0]
        # for i in range(self.population.shape[0]):
        #     self.bicycle.driveAlongPath(i, self.population[i], dict, 0)
        #
        # elapsed = timeit.default_timer() - start_time
        #
        # print('Finished in %s second(s)' % round((elapsed), 3))
        #
        # for i in range(self.population.shape[0]):
        #     self.population[i].fitness = dict[i]

        start_time = timeit.default_timer()
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        processes = []
        for i in range(self.population.shape[0]):
            p = multiprocessing.Process(target=self.bicycle.driveAlongPath, args=[i, self.population[i], return_dict, 0])
            p.start()
            processes.append(p)

        for process in processes:
            process.join()
        print("done calculating the fitness of this generation")

        elapsed = timeit.default_timer() - start_time

        print('Finished in %s second(s)' % round((elapsed), 3))

        for i in range(self.population.shape[0]):
            self.population[i].fitness = return_dict[i]

    def selection(self):
        self.quickSort(self.population, 0, self.population.shape[0]-1)
        print("\n")
        print("fittest parents")
        parents = self.population[0:self.number_parents]
        for parent in parents:
            print(parent.fitness)

        self.fittest = parents[0]

        return parents

    def crossover(self, parents):
        print(self.number_parents)
        new_population = parents
        new_population = np.reshape(new_population, [self.number_parents, 1])
        print(new_population.shape)

        for i in range(self.number_parents):
            for j in range(i+1, self.number_parents):
                parent1 = parents[i].k
                parent2 = parents[j].k
                offspring1 = [parent1[0], parent1[1], parent1[2], parent2[3], parent2[4], parent2[5]]
                offspring2 = [parent2[0], parent2[1], parent2[2], parent1[3], parent1[4], parent1[5]]
                offspring1 = np.array(offspring1)
                offspring2 = np.array(offspring2)
                offspring1_pid = PID(offspring1)
                offspring2_pid = PID(offspring2)
                new_offspring = np.empty([2,1], dtype=object)
                new_offspring[0,0] = offspring1_pid
                new_offspring[1,0] = offspring2_pid

                new_population = np.concatenate((new_population, new_offspring), axis=0)

        print(new_population.shape[0])
        for i in range(self.population.shape[0]):
            self.population[i].k = new_population[i,0].k

    def mutation(self):
        print("build mutation")
        for i in range(self.population.shape[0]):
            mutate = np.random.uniform(0,1)
            if mutate < self.mutation_rate:
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[0] = np.random.uniform(low=0, high=2)
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[1] = np.random.uniform(low=0, high=0.1)
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[2] = np.random.uniform(low=0, high=0.1)
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[3] = np.random.uniform(low=0, high=10)
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[4] = np.random.uniform(low=0, high=0.1)
                if np.random.uniform(0,1) < 0.5:
                    self.population[i].k[5] = np.random.uniform(low=0, high=0.1)


    def quickSort(self, x, start, end):
        if(start >= end):
            return
        index = self.partition(x, start, end)
        self.quickSort(x, start, index-1)
        self.quickSort(x, index, start)

    def partition(self, x, start, end):
        pivot_index = start
        pivot_value = x[end].fitness
        for i in range(start, end+1):
            if x[i].fitness < pivot_value:
                self.swap(x, i, pivot_index)
                pivot_index = pivot_index + 1
        self.swap(x, pivot_index, end)

        return pivot_index

    def swap(self, x, a, b):
        temp = x[a]
        x[a] = x[b]
        x[b] = temp
