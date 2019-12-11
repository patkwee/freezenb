import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
from nbformat.v4 import new_markdown_cell
import subprocess
import base64
import copy
import os

def scrub_output(nb):
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        cell['outputs'] = []
        cell['execution_count'] = None
    return nb


def convert(input_fn, output_fn):

    with open(input_fn, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor() # kernel_name='python3'
    ep.preprocess(nb) #, {'metadata': {'path': '.'}})

    nb_scrubbed = scrub_output(copy.deepcopy(nb))

    ipynb = nbformat.writes(nb_scrubbed)
    ipynb_uri = 'data:text/plain;base64,' + base64.b64encode(ipynb.encode('utf-8')).decode('utf-8')


    result = subprocess.run(['conda','env','export'], stdout=subprocess.PIPE)
    env = result.stdout
    env_uri = 'data:text/plain;base64,' + base64.b64encode(env).decode('utf-8')


    basename = os.path.basename(input_fn)
    envname = 'environment.yml'
    nb['cells'].append(new_markdown_cell(f"---\n <a download='{basename}' href='{ipynb_uri}'>{basename}</a> <a download='{envname}' href='{env_uri}'>{envname}</a>"))

    exporter = HTMLExporter()
    (body, resources) = exporter.from_notebook_node(nb)

    writer = FilesWriter()
    writer.write(output=body, resources=resources, notebook_name=output_fn)