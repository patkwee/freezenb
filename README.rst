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
You can install the package directly from github via pip:
    
    conda install git pip
    pip install git+https://github.com/patkwee/freezenb



Usage from command line
-----------------------
The command 'freezenb' will be installed in your environment.

    $ freezenb --help
    usage: freezenb [-h] [--version] [-v] [-vv] filename [out]

    Execute and convert a jupyter notebook to html

    positional arguments:
      filename             Jupyter notebook filename
      out                  Output filename

    optional arguments:
      -h, --help           show this help message and exit
      --version            show program's version number and exit
      -v, --verbose        set loglevel to INFO
      -vv, --very-verbose  set loglevel to DEBUG

To convert the notebook 'my_notebook.ipynb' run:

    $ freezenb my_notebook.ipynb


Documentation
-------------
See https://freezenb.readthedocs.io