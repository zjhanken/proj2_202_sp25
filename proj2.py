from __future__ import annotations
import sys
import csv
from typing import *
from dataclasses import dataclass
import unittest
import math

expected_headers: list[str] = [
    "country",
    "year",
    "electricity_and_heat_co2_emissions",
    "electricity_and_heat_co2_emissions_per_capita",
    "energy_co2_emissions",
    "energy_co2_emissions_per_capita",
    "total_co2_emissions_excluding_lucf",
    "total_co2_emissions_excluding_lucf_per_capita"
]

header_dict: dict[str, int] = {
    "country": 0,
    "year": 1,
    "electricity_and_heat_co2_emissions": 2,
    "electricity_and_heat_co2_emissions_per_capita": 3,
    "energy_co2_emissions": 4,
    "energy_co2_emissions_per_capita": 5,
    "total_co2_emissions_excluding_lucf": 6,
    "total_co2_emissions_excluding_lucf_per_capita": 7
}

@dataclass(frozen=True)
class Row:
    country: str
    year: int
    electricity_and_heat_co2_emissions: Optional[float]
    electricity_and_heat_co2_emissions_per_capita: Optional[float]
    energy_co2_emissions: Optional[float]
    energy_co2_emissions_per_capita: Optional[float]
    total_co2_emissions_excluding_lucf: Optional[float]
    total_co2_emissions_excluding_lucf_per_capita: Optional[float]

@dataclass(frozen=True)
class Node:
    value: Row
    next: Node | None

# converts a CSV string to float, returns None if the field is empty
def parse_float(s: str) -> Optional[float]:
    if s == '' or s is None:
        return None
    return float(s)

# takes a raw list of strings from one CSV row and builds a typed Row
def parse_row(values: list[str]) -> Row:
    return Row(
        country=values[0],
        year=int(values[1]),
        electricity_and_heat_co2_emissions=parse_float(values[2]),
        electricity_and_heat_co2_emissions_per_capita=parse_float(values[3]),
        energy_co2_emissions=parse_float(values[4]),
        energy_co2_emissions_per_capita=parse_float(values[5]),
        total_co2_emissions_excluding_lucf=parse_float(values[6]),
        total_co2_emissions_excluding_lucf_per_capita=parse_float(values[7]),
    )

# recursively builds a linked list from a list of raw CSV rows starting at index
def make_list(rows: list[list[str]], index: int) -> Optional[Node]:
    if index >= len(rows):
        return None
    return Node(value=parse_row(rows[index]), next=make_list(rows, index + 1))

# opens the CSV file, skips the header, and returns the data as a linked list
def read_csv_lines(filename: str) -> Optional[Node]:
    f = open(filename)
    reader = csv.reader(f)
    header = next(reader)
    if header != expected_headers:
        raise ValueError("header not expected header")
    data_rows: list[list[str]] = list(reader)
    return make_list(data_rows, 0)





# recursively counts the number of nodes in a linked list
def listlen(data: Optional[Node]) -> int:
    if data is None:
        return 0
    return 1 + listlen(data.next)



expected_comparisons: list[str] = [
    'less_than',
    'greater_than',
    'equal'
]

# checks if a single row's field satisfies the given comparison against value
def compare(row: Row, field_name: str, comparison: str, value: Union[str, float, int]) -> bool:
    if row is None:
        return False
    if field_name not in expected_headers:
        raise ValueError('column doesnt exist')
    if comparison not in expected_comparisons:
        raise ValueError('comparison doesnt exist')
    if field_name == "country" and comparison != "equal":
        raise ValueError("only equal allowed for country")
    curr_val: Union[str, float, int, None] = getattr(row, field_name)
    if curr_val is None:
        return False
    if comparison == 'equal':
        return curr_val == value
    if comparison == 'less_than':
        return curr_val < value
    if comparison == 'greater_than':
        return curr_val > value
    else:
        raise ValueError('comparison not found')

# recursively filters the linked list, keeping only rows that pass compare
def filter_rows(
    data: Optional[Node],
    field_name: str,
    comparison: str,
    value: Union[str, float, int]) -> Optional[Node]:
    if data is None:
        return None
    rest: Optional[Node] = filter_rows(data.next, field_name, comparison, value)
    if compare(data.value, field_name, comparison, value):
        return Node(value=data.value, next=rest)
    else:
        return rest
