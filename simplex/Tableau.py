from typing import List, Tuple, Mapping
from copy import deepcopy

from simplex.Product import *
from simplex.Constraint import *
from simplex.utils import *

import itertools
import functools
import numpy as np

class Tableau:
    def __init__(self,
                 products: List[Product],
                 resources: Mapping[str, int]):
        self.products = products
        self.constraints = [Constraint(resource, i, len(resources), self.products, count) for i, (resource, count) in enumerate(resources.items())]
        self.index = 0

    @functools.cached_property
    def column_names(self) -> List[str]:
        return access_attributes(self.products + self.constraints, "name") + ["RHS"]

    @property
    def coefficients(self) -> "np.ndarray[float]":
        # NOTE: constraint.unit_profit is always 0
        return np.array(access_attributes(self.products + self.constraints, "unit_profit"), dtype=np.float64)

    @property
    def objective_functions(self) -> "np.ndarray[float]":
        return np.array(access_attributes(self.constraints, "objective_function_breakdown"), dtype=np.float64).sum(axis = 0)

    @property
    def pivot_row(self) -> int:
        # argmin
        return self.rows.argmin()

    @property
    def rows(self) -> "np.ndarray[float]":
        pivot_column = self.column_names[self.pivot_column]
        return np.array([constraint.rhs_pivot_column_ratio(pivot_column) for constraint in self.constraints])

    @property
    def pivot_column(self) -> int:
        return np.argmax(self.coefficients - self.objective_functions)

    def __str__(self, normalized = False):
        return "\n".join([
            # Objective Function Coefficients: C
            format_row("\tC\t", self.coefficients, "% 7.1f"),
            # Header
            format_row("Basis\t\t", self.column_names),
            # Constrants with ratios
            *[str(constraint) + (("\t% 7.1f" % ratio + (bool(i == self.pivot_row) and " <" or "")) if bool(normalized) else "") for i, (constraint, ratio) in enumerate(zip(self.constraints, self.rows))],
            # Objective Functions: Z
            format_row("\tZ\t", self.objective_functions.tolist() + [sum(constraint.coefficient * constraint.rhs for constraint in self.constraints)], "% 7.1f"),
            # C - Z
            format_row("\tC-Z\t", self.coefficients - self.objective_functions, "% 7.1f"),
            # pivot_column indication
            format_row("\t\t", [""] * self.pivot_column + ["^"]),
        ])

    @property
    def report(self) -> Mapping[str, float]:
        report = dict([(constraint.name, 0) for constraint in self.constraints] + [(product.name, 0) for product in self.products])
        for constraint in self.constraints:
            report[constraint.display_name] = constraint.rhs

        return report

    def __iter__(self):
        return self; # deepcopy(self)

    def __next__(self):
        if not np.any(self.coefficients - self.objective_functions > 0):
            raise StopIteration

        pivot_row = self.pivot_row
        pivot_column = self.pivot_column

        tableau = [
            "==================== Tableau %d  / (%s Tableau) ====================" % (self.index, ordinal(self.index + 1)),
            str(self),
        ]

        report = [
            "====== Report ======",
            *list(map(str, self.report.items())),
            "\n",
        ]

        self.constraints[pivot_row].normalize(self.column_names[pivot_column])
        scaling = [
            "Scaling Pivot row",
            self.__str__(normalized = True),
        ]

        eliminations = list(map(str, itertools.chain.from_iterable(
            ("Eliminating row: %d" % i,
                constraint.eliminate(self.constraints[pivot_row], self.column_names[pivot_column]) or str(self))
                for i, constraint in enumerate(self.constraints)
                    if i != pivot_row
        )))

        post_elimination_report = [
            "====== Report ======",
            *list(map(str, self.report.items())),
        ]

        # replace the product with constraint
        self.constraints[pivot_row].display_name = self.products[pivot_column].name
        self.index += 1

        return "\n".join([
            *tableau,
            *report,
            *scaling,
            *eliminations,
            *post_elimination_report,
        ])
