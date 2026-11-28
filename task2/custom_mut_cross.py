import numpy as np
import random as rd
from utils import Problem



def custom_crossover_func(parents, offsprings_size, ga_instance):
    offspring=[]

    #zanimiva ideja, da izberem za vsak skupek 3 genov enega od starsev
    #ampak ima vecjo verjetnost da bo izbran tisti ki ima vecji fitnes
    #mogoce prevec casovno kompleksno
    k = min(4, len(parents))

    #replace false je brez ponavljanja
    for i in range(offsprings_size[0]):
        parents_chosen=parents[np.random.choice(len(parents),k,replace=False)]
        new_child=[]
        for k in range(len(parents[0])//3):
            chosen_idx = np.random.randint(len(parents_chosen))
            chosen_one = parents_chosen[chosen_idx]
            new_child.append(chosen_one[3*k])
            new_child.append(chosen_one[3*k+1])
            new_child.append(chosen_one[3*k+2])
        offspring.append(np.array(new_child))

    return np.array(offspring)

def custom_mutation_func(offspring, ga_instance):

    for off in offspring:

        for lecture_idx in range(len(off)//3):

            if np.random.random()<0.1:
                #mutiras
                idx=lecture_idx*3
                if np.random.random()<0.3:
                    #mutiras enega
                    num=np.random.randint(3)
                    if num==0:
                        new_room=rd.choice(ga_instance.gene_space[0])
                        off[idx]=new_room
                    elif num==1:
                        new_hour=rd.choice(ga_instance.gene_space[1])
                        off[idx+1]=new_hour
                    else:
                        new_tch=rd.choice(ga_instance.gene_space[2])
                        off[idx+2]=new_tch
                
                else:
                    #mutiras vse tri
                    new_room=rd.choice(ga_instance.gene_space[0])
                    off[idx]=new_room
                    new_hour=rd.choice(ga_instance.gene_space[1])
                    off[idx+1]=new_hour
                    new_tch=rd.choice(ga_instance.gene_space[2])
                    off[idx+2]=new_tch
            
    return offspring
