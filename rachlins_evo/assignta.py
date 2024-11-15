"""
Minimize overallocation of TAs (overallocation): Each TA specifies how many labs they can
support (max_assigned column in tas.csv). If a TA requests at most 2 labs and you assign to them 5
labs, that’s an overallocation penalty of 3. Compute the objective by summing the overallocation
penalty over all TAs. There is no minimum allocation.

2. Minimize time conflicts (conflicts): Minimize the number of TAs with one or more time conflicts. A
time conflict occurs if you assign a TA to two labs meeting at the same time. If a TA has multiple
time conflicts, still count that as one overall time conflict for that TA.

3. Minimize Under-Support (undersupport): If a section needs at least 3 TAs and you only assign 1,
count that as 2 penalty points. Minimize the total penalty score across all sections. There is no
penalty for assigning too many TAs. You can never have enough TAs.

4. Minimize the number of times you allocate a TA to a section they are unwilling to support
(unwilling). You could argue this is really a hard constraint, but we will treat it as an objective to be
minimized instead.

5. Minimize the number of times you allocate a TA to a section where they said “willing” but not
“preferred”. (unpreferred). In effect, we are trying to assign TAs to sections that they prefer. But we
want to frame every objective a minimization objective. So, if your solution score has unwilling=0
and unpreferred=0, then all TAs are assigned to sections they prefer!
"""
import random
import pandas as pd
import numpy as np
from jupyter_server.services.config.handlers import section_name_regex

SECTION_DICT = {17: 'R 1145-125', 1: 'W 950-1130', 2: 'W 950-1130', 3: 'W 950-1130', 4: 'W 1145-125', 5: 'W 1145-125',
                6: 'W 250-430', 7: 'W 250-430', 8: 'W 250-430', 9: 'W 440-630', 10: 'R 950-1130', 11: 'R 950-1130',
                12: 'R 1145-125', 13: 'R 1145-125', 14: 'R 1145-125', 15: 'R 250-430', 16: 'R 250-430', 0: None}

def overallocation(tas, test):
    """Minimize overallocation of TAs (overallocation): Each TA specifies how many labs they can
       support (max_assigned column in tas.csv). If a TA requests at most 2 labs and you assign to them 5
       labs, that’s an overallocation penalty of 3. Compute the objective by summing the overallocation
       penalty over all TAs. There is no minimum allocation."""
    row_sums = np.sum(test, axis=1)
    print(row_sums.shape)
    difference = row_sums - tas
    positive_values = difference[difference > 0]
    return sum(positive_values)

def time_conflicts(test, section_dict):
    """
    2. Minimize time conflicts (conflicts): Minimize the number of TAs with one or more time conflicts. A
    time conflict occurs if you assign a TA to two labs meeting at the same time. If a TA has multiple
    time conflicts, still count that as one overall time conflict for that TA. - not finished
    """
    column_indices = np.arange(test.shape[1])
    column_indices[0] = 17
    indices = np.tile(column_indices, (test.shape[0], 1))
    test[test == 1] = indices[test == 1]
    test = test.astype(object)
    test = np.vectorize(section_dict.get, otypes=[object])(test)
    has_duplicates = np.array([len(row[~np.isin(row,
    [None])]) != len(np.unique(row[~np.isin(row, [None])])) for row in test])
    return sum(has_duplicates)




def minimize_under(test, section):
    """3. Minimize Under-Support (undersupport): If a section needs at least 3 TAs and you only assign 1,
    count that as 2 penalty points. Minimize the total penalty score across all sections. There is no
    penalty for assigning too many TAs. You can never have enough TAs. - not finished"""

    row_sums = np.sum(test, axis=0)
    print(row_sums)
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

def swap_tas(array, ta_data, max_assigned = 'max_assigned'):
    """
    Agent 1: Randomly swaps TA sections if TA is over max preferred with one that is under max preferred
    """

    # sums the count of TAs assigned for each row
    section_counts = np.sum(array, axis = 1)

    # identify over and under allocated TAs
    overallocated = [i for i in range(len(section_counts)) if section_counts[i] > ta_data.iloc[i][max_assigned]]
    underallocated = [i for i in range(len(section_counts)) if section_counts[i] < ta_data.iloc[i][max_assigned]]

    if len(overallocated) == 0 and len(underallocated) == 0:
        print('TAs allocated correctly, no changes needed')

    # picking random TA in over and under allocated lists
    over_ta = random.choice(overallocated)
    under_ta = random.choice(underallocated)

    # finding a section assigned to the over-allocated TA
    over_ta_sections = np.where(array[over_ta] == 1)[0]

    # randomly selecting a section to transfer
    for section in over_ta_sections:
        if array[under_ta, section] == 0:
            array[over_ta, section] = 0
            array[under_ta, section] = 1
            print(f"Swapped section {section} from TA {over_ta} to TA {under_ta}")
            return array

    print('No swaps were made')
    return array




def balance_sections(array, section_data, min_ta_col='min_ta', max_ta_col='max_ta'):
    """
    Agent 2: Balances sections by reassigning TAs from randomly selected over-allocated sections to
    randomly selected under-allocated sections
    """

    # counting number of TAs in each section
    ta_counts = np.sum(array, axis = 0)

    # identifying over and under allocation sections (within range)
    overallocated_sections = [i for i in range(len(ta_counts)) if ta_counts[i] > section_data.iloc[i][max_ta_col]]
    underallocated_sections = [i for i in range(len(ta_counts)) if ta_counts[i] < section_data.iloc[i][min_ta_col]]

    if len(overallocated_sections) == 0 and len(underallocated_sections) == 0:
        print('All sections are correctly allocated. No changes needed.')
        return array

    # randomly selecting an overallocated and underallocated section
    over_section = random.choice(overallocated_sections)
    under_section = random.choice(underallocated_sections)

    # finding a TA assigned to the over-allocated section

    over_section_tas = np.where(array[:, over_section] == 1)[0]





def main():


   sections = pd.read_csv("sections.csv")
   tas_min = np.array(sections["min_ta"]).reshape(1, -1)
   tas = pd.read_csv("tas.csv")
   assigns = tas[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16" ]]
   tas_1 = assigns.replace("U", 0)
   tas_2unw = tas_1.replace("W", 1)
   tas_unw = tas_2unw.replace("P", 1)
   tas1_unp = assigns.replace("U", 1)
   tas2_unp = tas1_unp.replace("W", 0)
   tas_unp = tas2_unp.replace("P", 1)
   tas_max = np.array(tas["max_assigned"]).reshape(1, -1)

   data = np.loadtxt("test1.csv", delimiter=",", skiprows=0)
  
   print("Non pref", minimize_nonpref(data, tas_unp))
   print("Unw", minimize_unw(data, tas_unw))
   print("Under", minimize_under(data, tas_min))
   print("Over", overallocation(tas_max, data))
   #test2 = np.loadtxt()
   #test3 = np.loadtxt()
   print("TC", time_conflicts(data, SECTION_DICT))



main()

