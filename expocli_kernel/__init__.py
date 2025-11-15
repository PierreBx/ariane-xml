"""
ExpoCLI Jupyter Kernel

A Jupyter kernel for executing ExpoCLI SQL-like XML queries in notebooks.
Enhanced with rich HTML table output.
"""

__version__ = '1.1.0'

from .kernel import ExpoCLIKernel

__all__ = ['ExpoCLIKernel']
