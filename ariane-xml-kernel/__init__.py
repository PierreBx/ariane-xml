"""
Ariane-XML Jupyter Kernel

A Jupyter kernel for executing Ariane-XML SQL-like XML queries in notebooks.
Enhanced with rich HTML table output.
"""

__version__ = '1.1.0'

from .kernel import ArianeXMLKernel

__all__ = ['ArianeXMLKernel']
