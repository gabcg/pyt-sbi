#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import arguments
import interface
import utils
import exceptions
import copy
import random
import pickle
from global_vars import *
# STEP 1: parse the arguments
options = arguments.read_args()
if options.gui:
    options = interface.gui()

input_files = arguments.get_input_files(options.input)
stoichiometry = None
if options.stoichiometry is not None:
    stoichiometry = arguments.parse_stoichiometry(options.stoichiometry)
if options.verbose:
    utils.options = options
    sys.stderr.write("Input correctly parsed.\nFiles used as input:\n")
    for file in input_files:
        sys.stderr.write("\t"+file+"\n")
    sys.stderr.write("\n")

# Step 2: get possible structures for macrocomplex construction and skip others
if options.resume:
    (chains, pairs, similar_chains, structures) = utils.resume(options)
else:
    (chains, pairs, similar_chains, structures) = utils.get_information(input_files, options)


complexes_found = []
temp = None
if options.verbose:
    sys.stderr.write("\n# Beginning to construct the complex\n\n")
# STEP4: Begin Macrocomplex reconstruction!
def construct_complex(current_complex_real,
                      similar_chains, stoichiometry,
                      structures, used_pairs_real, clashing_real,old_complex_real):
    # bruteforce ending!
    current_complex = copy.deepcopy(current_complex_real)
    used_pairs = copy.deepcopy(used_pairs_real)
    clashing = copy.deepcopy(clashing_real)
    old_complex = copy.deepcopy(old_complex_real)
    print("SIMILAR CHAINS::" + str(similar_chains))
    global temp
    print("HOLA")
    # for the first round its going to be a random pair of chains.
    if current_complex is None:
        random_choice_id = random.choice(list(structures.keys()))
        random_choice = structures[random_choice_id]
        used_pairs.append(random_choice_id)
        if options.verbose:
            sys.stderr.write("Selecting starting pair: "+str(random_choice_id)
                             + "\n")
        construct_complex(random_choice,
                          similar_chains, stoichiometry,
                          structures, used_pairs,clashing, old_complex )
        return
    else:
        for chain_in_current_complex in utils.get_chain_ids_from_structure(current_complex):
            a = utils.get_chains_from_structure(current_complex)
            b = utils.get_chains_from_structure(old_complex)
            new_chain = set(a).difference(set(b))
            print("new chain "+ str(new_chain))
            ps = utils.get_possible_structures(chain_in_current_complex,
                                               similar_chains, structures, used_pairs, clashing, new_chain)
            print("Possible structures : "+str(ps))
            if len(ps) == 0 and options.stoichiometry is None:
                if options.verbose:
                    sys.stderr.write("Complex built!! :)\n")
                    sys.stderr.write("If you are not satisfied with the number"+
                                     "chains used you can use the stoichiometry"+
                                     "parameter.\n")
                    sys.stderr.write("Do not forget to use --resume to avoid "+
                                     "unnecessary computation.\n")
                complexes_found.append(current_complex)
                return
            elif len(ps) == 0:
                    if len(utils.get_chain_ids_from_structure(current_complex)) == len(utils.get_chain_ids_from_structure(old_complex)):
                        #complexes_found.append(current_complex)
                        utils.print_chain_in_structure(current_complex)
                        utils.print_chain_in_structure(old_complex)
                        print("Already found!")
                        temp = current_complex
                        return
                    old_complex = current_complex
                    #if temp
                    clashing = []
                    print("calling myself again")
                    construct_complex(current_complex,
                                      similar_chains, stoichiometry,
                                      structures, [], clashing, old_complex)
                    return
                    # ps = utils.get_possible_structures(chain_in_current_complex,
                    #                                    similar_chains, structures, used_pairs, clashing)

            for similar_chain_id in ps:
                if stoichiometry is not None and utils.complex_fits_stoich(current_complex,stoichiometry):
                    "2!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                    break
                    return
                structure_id = ps[similar_chain_id]
                print('chain in current complex '+ str(chain_in_current_complex))
                print("similar_chain_id "+ str(similar_chain_id))
                utils.print_chain_in_structure(current_complex)
                print(used_pairs)
                structure_to_superimpose = structures[structure_id]
                other = [tuple_id for tuple_id in structure_id if tuple_id != similar_chain_id][0]
                if options.verbose:
                    sys.stderr.write("\nTrying to add: "+str(other)+"\n")
                    sys.stderr.write("Superimposing structure: "+str(structure_id)+"\n")
                    print("-------------------")
                    utils.print_chain_in_structure(structure_to_superimpose)
                matrix = utils.superimpose_chains_test(utils.get_chain(current_complex,chain_in_current_complex)
                                                      ,utils.get_chain_permissive(structure_to_superimpose, similar_chain_id))
                print("other "+ str(other))
                print(used_pairs)
                matrix.apply(utils.get_chain(structure_to_superimpose,other))
                chain_to_add = utils.get_chain_permissive(structure_to_superimpose,other)
                print(chain_to_add)
                if not utils.are_clashing(current_complex,chain_to_add):
                    if options.verbose:
                        sys.stderr.write("Not clashing -- adding chain! \n")
                    utils.add_chain(current_complex, chain_to_add)
                    #current_complex[0].add(utils.get_chain(structure_to_superimpose,other))
                    used_pairs.append(structure_id)
                else:
                    clashing.append(structure_id)
                ## Check if finished!
                if current_complex is not None:
                    if stoichiometry is not None and utils.complex_fits_stoich(current_complex,stoichiometry):
                        if options.verbose:
                            sys.stderr.write("Complex built!! :) \n")
                        for chain in utils.get_chains_from_structure(current_complex):
                            print(chain)
                        complexes_found.append(current_complex)
                        print("jkdfsjklfjhljhfdkslsdhjklsdfhjkl")
                        break
                        return
                    else:
                        #elif --> add repeated!
                        if len(complexes_found) == 1:
                            print("skldjhgsalfjhgskdjhfgkajsdhfgkasdhjfgsdafkjhsad!!!!!222!")
                            return

                        construct_complex(current_complex,
                                          similar_chains, stoichiometry,
                                          structures, used_pairs, clashing, old_complex)
                        if len(complexes_found) == 1:
                            print("skldjhgsalfjhgskdjhfgkajsdhfgkasdhjfgsdafkjhsad!!!!!!")
                            return


test_complex = construct_complex(None, similar_chains,
                                 stoichiometry, structures, [], [], [])
# Step5: Filter the good ones



# Step 6: write output file
index_file = 0
if len(complexes_found) == 0:
    print("Entering, temp:"+str(temp))
    complexes_found.append(temp)
for complex in complexes_found:
    print(complex)
    index_file += 1
    if options.output is None:
        outputfile = "results/output"
    else:
        outputfile = "results/"+str(options.output)
    utils.write_structure_into_file(complex,
                                    outputfile+str(index_file)+".cif",
                                    "mmcif")

# Step 7 (optional): open models in Chimera
if options.open_chimera:
    utils.open_in_chimera(options.output)
