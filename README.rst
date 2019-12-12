========
freezenb
========


Execute and convert Jupyter notebooks to html with embedded environment specifications.


Description
===========

Inspired by the kaggle commit function, this script executes a Jupyter notebook, attaches
package specfications from the conda environment and exports everything as a single html file.
Jupyter nbconvert is used to execute and convert the notebook. 


Install
-------
Install from test.pypi
    
    pip install --index-url https://test.pypi.org/simple/ freezenb


Use
---
The commend 'freezenb' will be installed in your environment.

  freezenb my_notebook.ipynb my_notebook


Note
====

This project has been set up using PyScaffold 3.2.2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
