from pint import UnitRegistry
ureg = UnitRegistry('./composites/my_units.txt')
Q_ = ureg.Quantity