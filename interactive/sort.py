#!/usr/bin/env python3
"""
Interactive Sort
================
Sorts a collection of objects without native ordering, by asking someone
the order of some elements and applying transitivity to find out the total
ordering for the set.
"""


from enum import Enum
from collections import deque
import sys


class Ordering(Enum):
    Unknown = 0
    Lower = 1
    Higher = 2

    def opposite(self):
        """ Returns the opposite ordering. >.op(<), <.op(>), ?.op(?) """
        return {Ordering.Unknown: Ordering.Unknown,
                Ordering.Lower: Ordering.Higher,
                Ordering.Higher: Ordering.Lower}[self]


class TransitivityTable(object):
    """
    Transitivity table stores the order between every member of a set.
    It can be operated to fill vacant slots according to the transivity rule.
    """

    def __init__(self, data):
        """ Creates a new empty transitivity table using elements from
        a supplied dataset """
        self.data = {(x, y): Ordering.Unknown
                     for x in data for y in data
                     if x != y}
        self._datadim = len(data)
        self._dataset = tuple(data)
        self._elements = frozenset(data)

    def orderof(self, origin, target):
        """ Return the ordering between origin and target """
        return self.data[(origin, target)]

    def ishigher(self, origin, target):
        """ Returns if origin is higher than target """
        return self.orderof(origin, target) == Ordering.Higher

    def islower(self, origin, target):
        """ Returns if origin is lower than target """
        return self.orderof(origin, target) == Ordering.Lower

    def order(self, origin, target, value):
        """ The ordering between origin and target becomes value """
        if not isinstance(value, Ordering):
            raise TypeError('Only Ordering is supported')
        if origin not in self._elements:
            raise ValueError('origin is not in the dataset')
        if target not in self._elements:
            raise ValueError('target is not in the dataset')
        if (self.data[(origin, target)] != Ordering.Unknown and
                self.data[(origin, target)] != value):
            raise ValueError('Ordering already assigned')
        if (self.data[(target, origin)] != Ordering.Unknown and
                self.data[(target, origin)] != value.opposite()):
            raise ValueError('Ordering already assigned')
        self.data[(origin, target)] = value
        self.data[(target, origin)] = value.opposite()
        self.transitivity_set(origin)
        self.transitivity_set(target)

    def transitivity_set(self, pivot):
        """ Uses the pivot to provide transitivity rules """
        lowers = [x for x in self._dataset
                  if x != pivot and self.islower(x, pivot)]
        highers = [x for x in self._dataset
                   if x != pivot and self.ishigher(x, pivot)]
        for l in lowers:
            for h in highers:
                if self.orderof(l, h) != Ordering.Lower:
                    self.order(l, h, Ordering.Lower)

    dimension = property(fget=lambda self: self._datadim)


class Sort(object):
    """ Provides the interface for sorting a non-natural orderable dataset """

    def __init__(self, dataset):
        """ Creates a sorting object for the given dataset """
        self.dataset = dataset
        self.done = False
        self.table = TransitivityTable(dataset)
        self.buckets = deque([[x] for x in dataset])
        self.result = None
        self.question = None

    def sort(self):
        """ Tries to sort the data, halting if missing info """
        if len(self.buckets) == 0:
            self.done = True
            self.result = []
        elif len(self.buckets) == 1:
            self.done = True
            self.result = self.buckets[0]
        else:
            ongoing = True
            while ongoing and len(self.buckets) > 1:
                ongoing = self.merge()
            if len(self.buckets) == 1:
                self.done = True
                self.result = self.buckets[0]

    def merge(self):
        """ Merges two existing top buckets """
        a = self.buckets[0]
        b = self.buckets[1]
        sort = []
        while len(a) > 0 and len(b) > 0:
            order = self.table.orderof(a[0], b[0])
            if order == Ordering.Unknown:
                self.question = (a[0], b[0])
                return False
            elif order == Ordering.Lower:
                sort.append(a[0])
                a = a[1:]
            else:
                sort.append(b[0])
                b = b[1:]
        if len(a) > 0:
            sort.extend(a)
        if len(b) > 0:
            sort.extend(b)
        self.buckets.popleft()
        self.buckets.popleft()
        self.buckets.append(sort)
        return True


class BaseAgent(object):
    """ General interface for talking with the user for asking orderings """

    def __init__(self, dataset):
        """ Creates an agent for a given dataset """
        self.sort = Sort(dataset)

    def process(self):
        """ Sort operation, will use ask and retrieve_ordering methods """
        while not self.sort.done:
            self.sort.sort()
            if self.sort.question is not None:
                a, b = self.sort.question
                self.ask(a, b)
                order = self.retrieve_ordering()
                self.sort.table.order(a, b, order)
            self.sort.question = None
        return self.sort.result

    def ask(self, a, b):
        """ Base implementation, does nothing """
        pass

    def retrieve_ordering(self):
        """ Base implementation, returns Unknown """
        return Ordering.Unknown


class ConsoleAgent(BaseAgent):
    """ Agent for console interface, using input function """

    def ask(self, a, b):
        print('Is ', a, ' lower than ', b, '? (y/n)')

    def retrieve_ordering(self):
        r = input()
        while r not in ['y', 'n']:
            print('Invalid answer, use "y" or "n"')
            r = input()
        return {'y': Ordering.Lower, 'n': Ordering.Higher}[r]


class PreferenceConsoleAgent(BaseAgent):
    """ Agent for console interface about preferences """

    def ask(self, a, b):
        print('Do you prefer {a} or {b}?'.format(a=a, b=b))
        self.question = (a, b)

    def retrieve_ordering(self):
        r = input()
        while r not in self.question:
            print('Invalid answer, try again')
            r = input()
        a, b = self.question
        return {a: Ordering.Higher, b: Ordering.Lower}[r]


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('No dataset provided')
        exit(1)
    with open(sys.argv[1]) as f:
        data = list(map(str.strip, f.readlines()))
    ag = PreferenceConsoleAgent(data)
    result = ag.process()
    result = reversed(result)
    result = [str(idx + 1) + '. ' + x for (idx, x) in enumerate(result)]
    print('\n'.join(result))
