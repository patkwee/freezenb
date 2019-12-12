import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
from nbformat.v4 import new_markdown_cell
import base64
import copy
import os
import datetime
import math

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


def build_output_filename(input_fn, outext='.html'):
    """Find next unused output filename
    
    Uses v{int} suffix to find next unused output filename.
    
    Arguments:
        input_fn {str} -- input filename
    
    Keyword Arguments:
        outext {str} -- extension of output filename (default: {'.html'})
    
    Returns:
        str -- output filename
    """

    fn, ext = os.path.splitext(input_fn)
    i = 1
    while os.path.exists(f'{fn} v{i}{outext}'):
        i += 1

    return f'{fn} v{i}{outext}'


def pretty_duration(d):
    """Formats a time duration
    
    Formats a time duration in a human readable format
    
    Arguments:
        d {float} -- Duration in seconds
    
    Returns:
        str -- formated duration
    """

    if d < 1:
        return "<1s"

    s = ''
    
    days = math.floor(d / 86400)
    if days:
        s += f'{days}d '
    d = d % 86400

    hours = math.floor(d / 3600)
    if days or hours:
        s += f'{hours}h '
    d = d % 3600

    mins = math.floor(d / 60)
    if days or hours or mins:
        s += f'{mins}m '
    d = d % 60

    secs = round(d)
    if not days:
        s += f'{secs}s'

    return s.strip()


def convert(input_fn, output_fn=None):
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
    starttime = datetime.datetime.today()
    ep.preprocess(nb)
    endtime = datetime.datetime.today()
    _logger.info(f'Executed notebook')

    timestamp = "Executed {} in {}.".format(starttime.strftime('%Y-%m-%d %H:%M:%S'), 
        pretty_duration((endtime-starttime).total_seconds()))

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
    md = f"---\n {timestamp} {ipynb_link} {packages_link}"
    nb['cells'].append(new_markdown_cell(md))

    # Export to html
    _logger.info(f'Exporting to "{output_fn}"')
    exporter = HTMLExporter()
    (body, resources) = exporter.from_notebook_node(nb)

    if not output_fn:
        output_fn = build_output_filename(input_fn)

    writer = FilesWriter()
    resources['output_extension'] = None
    writer.write(output=body, resources=resources, notebook_name=output_fn)

    _logger.info(f'Finished')