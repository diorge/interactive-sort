"""
Interactive Sort
================
Sorts a collection of objects without native ordering, by asking someone
the order of some elements and applying transitivity to find out the total
ordering for the set.
"""


class TransitivityTable(object):
    """
    Transitivity table stores the order between every member of a set.
    It can be operated to fill vacant slots according to the transivity rule.
    """

    def __init__(self, data):
        """ Creates a new empty transitivity table using elements from
        a supplied dataset """
        pass
