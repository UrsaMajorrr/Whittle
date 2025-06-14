from enum import Enum, auto

class SolverType(Enum):
    """Enum representing different supported CFD solvers"""
    OPENFOAM = auto()
    # Future solvers can be added here
    # FLUENT = auto()
    # SU2 = auto()
    # etc. 