"""
File: assignta.py
Author: Rishi Kamtam, Jeffrey Krapf, Alexander Tu
Description: This program optimizes TA assignments to sections by minimizing overallocation, time conflicts,
undersupport, and assignments to unwilling or unpreferred sections using an evolutionary algorithm framework
"""


import random
import pandas as pd
import numpy as np
from jupyter_server.services.config.handlers import section_name_regex
from evo import Evo

import warnings
warnings.filterwarnings("ignore")


# defining global variables

SECTIONS = pd.read_csv("sections.csv")
TAS = pd.read_csv("tas.csv")


SECTION_DICT = {17: 'R 1145-125', 1: 'W 950-1130', 2: 'W 950-1130', 3: 'W 950-1130', 4: 'W 1145-125', 5: 'W 1145-125',
                6: 'W 250-430', 7: 'W 250-430', 8: 'W 250-430', 9: 'W 440-630', 10: 'R 950-1130', 11: 'R 950-1130',
                12: 'R 1145-125', 13: 'R 1145-125', 14: 'R 1145-125', 15: 'R 250-430', 16: 'R 250-430', 0: None}

ASSIGNS = TAS[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]]

def overallocation(tas, test):
    """Minimize overallocation of TAs (overallocation): Each TA specifies how many labs they can
       support (max_assigned column in tas.csv). If a TA requests at most 2 labs and you assign to them 5
       labs, that’s an overallocation penalty of 3. Compute the objective by summing the overallocation
       penalty over all TAs. There is no minimum allocation."""
    row_sums = np.sum(test, axis=1)
    difference = row_sums - tas
    positive_values = difference[difference > 0]
    return sum(positive_values)

def time_conflicts(test, section_dict):
    """
    2. Minimize time conflicts (conflicts): Minimize the number of TAs with one or more time conflicts. A
    time conflict occurs if you assign a TA to two labs meeting at the same time. If a TA has multiple
    time conflicts, still count that as one overall time conflict for that TA. - not finished
    """
    test_copy = test.copy()
    column_indices = np.arange(test_copy.shape[1])
    column_indices[0] = 17
    indices = np.tile(column_indices, (test_copy.shape[0], 1))
    test_copy[test_copy == 1] = indices[test_copy == 1]
    test_copy = test_copy.astype(object)
    test_copy = np.vectorize(section_dict.get, otypes=[object])(test_copy)
    has_duplicates = np.array([len(row[~np.isin(row,
    [None])]) != len(np.unique(row[~np.isin(row, [None])])) for row in test_copy])
    return sum(has_duplicates)




def minimize_under(test, section):
    """3. Minimize Under-Support (undersupport): If a section needs at least 3 TAs and you only assign 1,
    count that as 2 penalty points. Minimize the total penalty score across all sections. There is no
    penalty for assigning too many TAs. You can never have enough TAs. - not finished"""

    row_sums = np.sum(test, axis=0)
    difference = row_sums - section
    positive_values = difference[difference < 0]
    return abs(sum(positive_values))

def minimize_unw(test, tas_unw):
    """Minimize the number of times you allocate a TA to a section they are unwilling to support
    (unwilling). You could argue this is really a hard constraint, but we will treat it as an objective to be
    minimized instead."""

    difference =  tas_unw - test
    count = np.count_nonzero(difference == -1)
    return count

def minimize_nonpref(test, tas_clean):
    """5. Minimize the number of times you allocate a TA to a section where they said “willing” but not
    “preferred”. (unpreferred). In effect, we are trying to assign TAs to sections that they prefer. But we
    want to frame every objective a minimization objective. So, if your solution score has unwilling=0
    and unpreferred=0, then all TAs are assigned to sections they prefer!"""
    difference =  tas_clean - test
    count = np.count_nonzero(difference == -1)
    return count



# Agents to optimize solutions

def swap_tas(array, ta_data=TAS, max_assigned='max_assigned'):
    """
    Agent 1: Randomly swaps TA sections if TA is over max preferred with one that is under max preferred.
    """
    arrays = array[0]
    section_counts = np.sum(arrays, axis=1)

    # Identify over- and under-allocated TAs
    overallocated = [i for i in range(len(section_counts)) if section_counts[i] > ta_data.iloc[i][max_assigned]]
    underallocated = [i for i in range(len(section_counts)) if section_counts[i] < ta_data.iloc[i][max_assigned]]

    # If no over-allocated or under-allocated TAs exist, do nothing
    if not overallocated:
        print("No over-allocated TAs. No swaps needed.")
        return arrays
    if not underallocated:
        print("No under-allocated TAs. No swaps possible.")
        return arrays

    # Pick random over- and under-allocated TAs
    over_ta = random.choice(overallocated)
    under_ta = random.choice(underallocated)

    # Find sections assigned to the over-allocated TA
    over_ta_sections = np.where(arrays[over_ta] == 1)[0]  # Indices of sections assigned to over_ta

    for section in over_ta_sections:
        # Check if the under-allocated TA can take this section
        if arrays[under_ta, section] == 0:  # Ensure no duplication in assignment
            arrays[over_ta, section] = 0  # Remove section from over-allocated TA
            arrays[under_ta, section] = 1  # Assign section to under-allocated TA
            print(f"Swapped section {section} from TA {over_ta} to TA {under_ta}")
            return arrays

    print("No valid swaps found.")
    return arrays




def balance_sections(array, section_data = SECTIONS, min_ta_col='min_ta', max_ta_col='max_ta'):
    """
    Agent 2: Balances sections by reassigning TAs from randomly selected over-allocated sections to
    randomly selected under-allocated sections
    """

    arrays = array[0]

    # Counting number of TAs in each section manually (as a list)
    ta_counts = np.sum(arrays, axis=0)

    # identifying over and under allocation sections (within range)
    overallocated_sec = [i for i in range(len(ta_counts)) if ta_counts[i] > section_data.iloc[i][max_ta_col]]
    underallocated_sec = [i for i in range(len(ta_counts)) if ta_counts[i] < section_data.iloc[i][min_ta_col]]

    print("TA Counts:", ta_counts)
    print("Under-allocated Sections:", underallocated_sec)

    if not underallocated_sec:
        print("No under-allocated sections. Rebalancing not needed.")
        return arrays

        # If no over-allocated sections, attempt to redistribute from correctly allocated sections
    if not overallocated_sec:
        print("No over-allocated sections. Attempting redistribution from correctly allocated sections.")
        potential_donors = [i for i in range(len(ta_counts)) if ta_counts[i] > 0]
    else:
        potential_donors = overallocated_sec

    # randomly selecting an overallocated and underallocated section
    over_section = random.choice(overallocated_sec)
    under_section = random.choice(underallocated_sec)

    # finding a TA assigned to the over-allocated section

    over_section_tas = np.where(arrays[:, over_section] == 1)[0]

    for ta in over_section_tas:
        if arrays[ta, under_section] == 0:  # Ensure the TA isn't already assigned to the under-allocated section
            arrays[ta, over_section] = 0
            arrays[ta, under_section] = 1
            print(f"Moved TA {ta} from section {over_section} to section {under_section}")
            return arrays

        # If no valid TA was found to move
    print(f"No valid swaps found between section {over_section} and section {under_section}")
    return arrays





def ta_swap_will(array, tas = TAS):
    """
    # Agent 3
    Parameters:
    array - a 2d array solution
    tas - 2d array of preferences for each ta
    Does: Finds tas who are in sections that they are willing to ta for but are not preferred,
          swaps them with a ta who is assigned to a section they prefer
    """
    arrays = array[0]

    for row, ta_row in enumerate(tas.values):
        if 'W' in ta_row:
            indexes = np.where(arrays[row] == 1)[0]
            for i in indexes:
                if tas.iloc[row, i] == 'W':
                    unassigned_tas = tas[tas[str(i)] == 'P'].index
                    if len(unassigned_tas) > 0:
                        # Picking random TA
                        random_ta_index = np.random.choice(unassigned_tas)

                        # Swapping rows
                        arrays[[row, random_ta_index]] = arrays[[random_ta_index, row]]
                        print(f"Swapped TA {row} (willing) with TA {random_ta_index} (preferred) in section {i}.")
                        break

    return arrays




def ta_swap_nonpref(array, tas = TAS):
    """
    # Agent 4
    Parameters:
        sol - a 2D array solution
        tas - 2D array of preferences for each TA
    Finds TAs that are assigned to unpreferred sections and swaps with a TA
    that has that section as preferred but isn't assigned to it.
    """
    arrays = array[0]

    for row, ta_row in enumerate(tas.values):
        if 'U' in ta_row:
            print(f"TA {row} has unpreferred sections: {ta_row}")
            indexes = np.where(arrays[row] == 1)[0]
            for i in indexes:
                if tas.iloc[row, i] == 'U':  # Check if assigned to an unpreferred section
                    unassigned_tas = tas[tas[str(i)] == 'P'].index
                    if len(unassigned_tas) > 0:
                        # Picking a random TA
                        random_ta_index = np.random.choice(unassigned_tas)

                        # Swapping rows
                        arrays[[row, random_ta_index], :] = arrays[[random_ta_index, row], :]
                        print(f"Swapped TA {row} (unpreferred) with TA {random_ta_index} (preferred) in section {i}.")
                        break
    return arrays





def main():

    # Prepare data for fitness evaluation and agents

    tas_min = np.array(SECTIONS["min_ta"]).reshape(1, -1)
    tas_1 = ASSIGNS.replace("U", 0)
    tas_2unw = tas_1.replace("W", 1)
    tas_unw = tas_2unw.replace("P", 1)
    tas1_unp = ASSIGNS.replace("U", 1)
    tas2_unp = tas1_unp.replace("W", 0)
    tas_unp = tas2_unp.replace("P", 1)
    tas_max = np.array(TAS["max_assigned"]).reshape(1, -1)

    # Load initial solution from CSV
    data = np.loadtxt("test1.csv", delimiter=",", skiprows=0)

    # Initialize Evo environment
    E = Evo()

    # adding objectives
    E.add_fitness_criteria("Overallocation", lambda sol: overallocation(tas_max, sol))
    E.add_fitness_criteria("Time Conflicts", lambda sol: time_conflicts(sol, SECTION_DICT))
    E.add_fitness_criteria("Undersupport", lambda sol: minimize_under(sol, tas_min))
    E.add_fitness_criteria("Unwilling Allocations", lambda sol: minimize_unw(sol, tas_unw))
    E.add_fitness_criteria("Unpreferred Allocations", lambda sol: minimize_nonpref(sol, tas_unp))

    # adding agents
    E.add_agent("Swap TAs", swap_tas, k=1)
    E.add_agent("Balance Sections", balance_sections, k=1)
    E.add_agent('ta_swap_will', ta_swap_will, k=1)
    E.add_agent('ta_swap_nonpref', ta_swap_nonpref, k=1)


    # adding solution
    E.add_solution(data)

    # starting evolution process
    print("Starting evolution process...")
    E.evolve(time_limit=300, status=100, dom=50)


    # collect and save pareto-optimal solutions
    summary = []
    for eval, sol in E.pop.items():
        result = {
            "groupname": 'AJK',
            "overallocation": eval[0][1],  # Score for overallocation
            "conflicts": eval[1][1],  # Score for conflicts
            "undersupport": eval[2][1],  # Score for undersupport
            "unwilling": eval[3][1],  # Score for unwilling allocations
            "unpreferred": eval[4][1],  # Score for unpreferred allocations
        }
        summary.append(result)


    # saving summary to CSV
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv("summary_solutions.csv", index=False)
    print("Summary saved to 'summary_solutions.csv'.")


main()

