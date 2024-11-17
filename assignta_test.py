import pytest
import assignta as at
import pandas as pd
import numpy as np





@pytest.fixture
def test1():
    x = np.loadtxt("test1.txt", delimiter=",", skiprows=0)
    print(x)
    return x


@pytest.fixture
def test2():
    y = np.loadtxt("test2.txt", delimiter=",", skiprows=0)
    return y


@pytest.fixture
def test3():
    z = np.loadtxt("test3.txt", delimiter=",", skiprows=0)
    return z


@pytest.fixture()
def tasunw():
    tas = pd.read_csv("tas.csv")
    assigns = tas[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]]
    tas_1 = assigns.replace("U", 0)
    tas_2unw = tas_1.replace("W", 1)
    tas_unw = tas_2unw.replace("P", 1)
    return tas_unw


@pytest.fixture()
def tasunp():
    tas = pd.read_csv("tas.csv")
    assigns = tas[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]]
    tas1_unp = assigns.replace("U", 1)
    tas2_unp = tas1_unp.replace("W", 0)
    tas_unp = tas2_unp.replace("P", 1)
    return tas_unp


@pytest.fixture()
def tasmax():
    tas = pd.read_csv("tas.csv")
    tas_max = np.array(tas["max_assigned"]).reshape(1, -1)
    return tas_max


@pytest.fixture()
def tasmin():
    sections = pd.read_csv("sections.csv")
    tas_min = np.array(sections["min_ta"]).reshape(1, -1)
    return tas_min


@pytest.fixture()
def section_dict():
    return {17: 'R 1145-125', 1: 'W 950-1130', 2: 'W 950-1130', 3: 'W 950-1130', 4: 'W 1145-125',
            5: 'W 1145-125',
            6: 'W 250-430', 7: 'W 250-430', 8: 'W 250-430', 9: 'W 440-630', 10: 'R 950-1130', 11: 'R 950-1130',
            12: 'R 1145-125', 13: 'R 1145-125', 14: 'R 1145-125', 15: 'R 250-430', 16: 'R 250-430', 0: None}


def test_overallocation(test1, test2, test3, tasmax):
    assert at.overallocation(tasmax, test1) == 37, "Overallocation failed for test 1"
    assert at.overallocation(tasmax, test2) == 41, "Overallocation failed for test 2"
    assert at.overallocation(tasmax, test3) == 23, "Overallocation failed for test 3"


def test_time_conflicts(test1,test2, test3, section_dict):
    assert at.time_conflicts(test1, section_dict) == 8, "time conflicts failed for test 1"
    assert at.time_conflicts(test2, section_dict) == 5, "time conflicts failed for test 2"
    assert at.time_conflicts(test3, section_dict) == 2, "time conflicts failed for test 3"


def test_minimize_under(test1, test2, test3, tasmin):
    assert at.minimize_under(test1,tasmin) == 1, "minimize under failed for test 1"
    assert at.minimize_under(test2, tasmin) == 0, "minimize under failed for test 2"
    assert at.minimize_under(test3, tasmin) == 7, "minimize under failed for test 3"


def test_unw(test1, test2, test3, tasunw):
    assert at.minimize_unw(test1, tasunw) == 53, "minimize unwilling failed for test 1"
    assert at.minimize_unw(test2, tasunw) == 58, "minimize unwilling failed for test 2"
    assert at.minimize_unw(test3, tasunw) == 43, "minimize unwilling failed for test 3"


def test_unp(test1, test2, test3, tasunp):
    assert at.minimize_unw(test1, tasunp) == 15, "minimize unpreferred failed for test 1"
    assert at.minimize_unw(test2, tasunp) == 19, "minimize unpreferred failed for test 2"
    assert at.minimize_unw(test3, tasunp) == 10, "minimize unpreferred failed for test 3"
