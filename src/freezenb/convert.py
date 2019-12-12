import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
from nbformat.v4 import new_markdown_cell
import base64
import copy
import os

import logging
_logger = logging.getLogger(__name__)


def scrub_output(nb):
    """Removes output cells from notebook
       
    Arguments:
        nb {notebook} -- Notebook
    
    Returns:
        notebook -- Notebook with scrubbed output cells
    """
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        cell['outputs'] = []
        cell['execution_count'] = None
    return nb


def get_package_list():
    """Get list of currently installed packages
    
    Runs 'conda list -e' to get the currently installed
    packages.
    
    Returns:
        bytes -- Output of 'conda list -e'
    """
    try:
        import conda.cli.python_api as cli
        return cli.run_command('list', "-e")[0].encode('utf-8')

    except ModuleNotFoundError:
        
        import subprocess
        
        try:
            result = subprocess.run(['conda','list','-e'], stdout=subprocess.PIPE)
            return result.stdout
        except FileNotFoundError:
            return None


def create_embedded_link(filename, data, mediatype='text/plain'):
    """Create html link with data URI
    
    Create an html link with embedded data as data URI
    
    Arguments:
        filename {str} -- Download filename
        data {bytes} -- Data for data URI
    
    Keyword Arguments:
        mediatype {str} -- media type of data (default: {'text/plain'})
    
    Returns:
        str -- html link
    """
    data_uri = 'data:' + mediatype + ';base64,' + base64.b64encode(data).decode('utf-8')
    return f"<a download='{filename}' href='{data_uri}'>{filename}</a>"


def convert(input_fn, output_fn):
    """Execute and save notebook as html
    
    Executes notebook, extracts packagelist and saves everything to html
    
    Arguments:
        input_fn {str} -- Input filename of notebook
        output_fn {str} -- Output filename for html file
    """

    _logger.info(f'Reading notebook "{input_fn}"')
    with open(input_fn, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Execute notebook
    _logger.info(f'Executing notebook...')
    ep = ExecutePreprocessor(timeout=-1)
    ep.preprocess(nb)
    _logger.info(f'Executed notebook')

    # Extract .ipynb file
    scrubbed_nb = scrub_output(copy.deepcopy(nb))
    ipynb_data = nbformat.writes(scrubbed_nb).encode('utf-8')
    ipynb_link = create_embedded_link(os.path.basename(input_fn), ipynb_data)

    # Get package list
    _logger.info(f'Getting package list...')
    packages_data = get_package_list()
    if packages_data:
        packages_link = create_embedded_link('packages.txt', packages_data)
    else:
        packages_link = ''

    # Add files / links
    md = f"---\n {ipynb_link} {packages_link}"
    nb['cells'].append(new_markdown_cell(md))

    # Export to html
    _logger.info(f'Exporting to "{output_fn}"')
    exporter = HTMLExporter()
    (body, resources) = exporter.from_notebook_node(nb)

    writer = FilesWriter()
    writer.write(output=body, resources=resources, notebook_name=output_fn)

    _logger.info(f'Finished')