# Data coupling LOW COUPLING


def power(base: int, exponent: int) -> int:
    return pow(base, exponent)


def power_of_2(exponent: int) -> int:
    return power(2, exponent)


###########################################

# Stamp coupling
import dataclasses


@dataclasses.dataclass
class DataObject:
    a: int
    b: int
    c: int


def func_1(data_object: DataObject):
    print(data_object.a)


def func_2(data_object: DataObject):
    print(data_object.c)
