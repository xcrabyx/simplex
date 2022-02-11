from typing import List
from simplex.Product import *
from copy import deepcopy
import numpy as np

class Constraint:
    def __init__(self,
                 name: str,
                 resource_index: int,
                 total_resources: int,
                 products: List[Product],
                 limit: float):
        self.name = name 
        self.display_name = name 
        self.products = products

        self.resource_index = resource_index
        self.total_resources = total_resources
        self.consumptions = dict([(product.name, product.resources_required[self.name]) for product in products] + [("s%d" % (i + 1), float(i == resource_index)) for i in range(self.total_resources)])

        self.limit = limit

    @property
    def coefficient(self):
        for product in self.products:
            if product.name == self.display_name:
                return product.unit_profit

        # not found: i.e. slack
        return 0

    @property
    def unit_profit(self):
        return 0;

    def __iadd__(self, other: "Constraint") -> "Constraint":
        for key in self.consumptions:
            self.consumptions[key] += other.consumptions[key]

        self.limit += other.limit
        return self

    def __add__(self, other: "Constraint") -> "Constraint":
        self = deepcopy(self)
        self += other
        return self

    def __isub__(self, other: "Constraint") -> "Constraint":
        for key in self.consumptions:
            self.consumptions[key] -= other.consumptions[key]

        self.limit -= other.limit
        return self

    def __sub__(self, other: "Constraint") -> "Constraint":
        self = deepcopy(self)
        self -= other
        return self

    def __imul__(self, other: float) -> "Constraint":
        for key in self.consumptions:
            self.consumptions[key] *= other

        self.limit *= other
        return self

    def __mul__(self, other: "Constraint") -> "Constraint":
        self = deepcopy(self)
        self *= other
        return self

    def __itruediv__(self, other: float) -> "Constraint":
        for key in self.consumptions:
            self.consumptions[key] /= other

        self.limit /= other
        return self

    def __truediv__(self, other: "Constraint") -> "Constraint":
        self = deepcopy(self)
        self /= other
        return self

    def eliminate(self, other: "Constraint", pivot_column: str) -> None:
        self -= other * self.consumptions[pivot_column]

    def normalize(self, pivot_column: str) -> None:
        self /= self.consumptions[pivot_column]

    @property
    def rhs(self) -> float:
        return self.limit

    def rhs_pivot_column_ratio(self, pivot_column: str) -> float:
        try:
            return self.rhs / self.consumptions[pivot_column]
        except ZeroDivisionError:
            if self.rhs == 0:
                raise ValueError("0/0 is undefined")

            return float("inf") if self.rhs > 0 else float("-inf")

    def __str__(self):
        return self.display_name + "\t" + "\t".join("% 7.1f" % value for value in (self.coefficient, *self.consumptions.values(), self.rhs))

    @property
    def objective_function_breakdown(self) -> "np.ndarray[float]":
        return self.coefficient * np.fromiter(self.consumptions.values(), dtype=np.float64)

