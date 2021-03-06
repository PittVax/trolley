#!/usr/bin/env jython

# NOTE 2.7 compatibility is required (jython 2.7+)

""" The Trolley interface to the TreeAge Java API

Makes use of the wrapper classes in taoi module to simplify the specification
and execution of factorial experiments expressed using a YAML input
configuration file.

Provides both a module and a CLI interface script
"""

try:
    import utils.set_classpath
    # import the treeage pro object interface
    import com.treeage.treeagepro.oi as TA
except Exception as e:
    raise

import logging
try:
    __main__

except NameError as e:
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

import argparse
import yaml, json
import os
import hashlib
from xml.etree import ElementTree as ET
from collections import defaultdict

from utils.utility_functions import cat, csv_key_value_dict
from taoi import TaoiTable, TaoiVariable

###############################################################################
################################################################### TrolleySession

class TrolleySession(object):
    def __init__(self, host=None, treefile=None, workspace=None,
            outdir=None, debug=None, auto=None, config=None):

        self._tables = []
        self._archive = dict()

        self.configfile = config
        self.config_workspace(config, workspace)
        self.setc('outdir', outdir, self.workspace)

        self.setc('debug', debug)
        self.setc('auto', auto)

        self.setc('host', host, 'localhost')
        if self.host != 'localhost':
            log.info('Remote execution is still experiemental!')
       
        self.setc('treefile', treefile)
        if self.treefile is None:
            self._fail('A treefile is required to run!')
        else:
            self._archive_tree()
        
        if self.auto:
            self._autorun()

    def _autorun(self):
        self.connect()
        self.open_tree()
        self.initialize_tables()

    def _fail(self, msg):
        log.error(msg)
        raise Exception(msg)

    def _archive_tree(self):
        filepath = os.path.join(self.workspace, self.treefile)
        with open (filepath, 'rb') as f:
            self._archive['tree_string'] = f.read()
        self._archive['tree_string_md5'] = hashlib.md5(
                self._archive['tree_string'])

    @property
    def auto(self):
        """ Automatically connect to TreeAge and run analyses """
        return self.c['auto']
    @property
    def debug(self):
        """ More deatiled logging and finer-grained exception handling """
        return self.c['debug']
    @property
    def host(self):
        """ The host running the TreeAge application server """
        return self.c['host']
    @property
    def treefile(self):
        """ The relative or absolute path to the XML treefile """
        return self.c['treefile']
    @property
    def workspace(self):
        """ The directoy containing the input files """
        return self.c['workspace']
    @property
    def outdir(self):
        """ Where to write output (defaults to same value as workspace """ 
        return self.c['outdir']

    def config_workspace(self, config, workspace):
        """ Reads the config and workspace options and sets class members
        
        Somewhat convoluted logic searches for config file as a path relative
        to the workspace (if supplied), otherwise ???????????????????????? """
        # TODO this doesn't support absolute paths !!!!!!!!!!!!!!!!!!!!!!!
        _workspace = os.getcwd() if workspace is None else workspace
        self.c = dict()
        self._c = dict()
        try:
            if config is None:
                raise Exception('no config file supplied')
            with open(os.path.join(_workspace,config)) as f:
                self._c.update(yaml.safe_load(f))
            log.debug('successfully parsed yaml config file')
        except Exception as e:
            if workspace is None:
                log.debug(cat('No workspace provided, attempt to use current ',
                    'directory'))
            else:
                log.debug(cat('attempting to use supplied workspace without ',
                    'yaml config'))
        finally:
            if not os.access(_workspace, os.R_OK):
                msg = 'No read access to workspace path: %s' % _workspace
                log.error(msg)
                raise Exception(msg)
            if workspace is not None and workspace in self.c:
                log.warn(cat('workspace specified in config and as argument; ',
                    'using supplied argument: %s') % workspace)
        # when debugging log the original config dicts
        log.debug('supplied config = %s' % json.dumps(self._c))
        # update the workspace param in the master config
        self.setc('workspace',_workspace)

    def setc(self, name, value, default=None):
        """ Utility method that updates internal configuration dictionary

        Logs cases when values from the original config file are overridden by
        command line arguments or defaults (in the case of missing optional
        parameters. """
        assert(hasattr(self,'c'))
        assert(type(self.c) == dict)
        assert(hasattr(self,'_c'))
        assert(type(self._c) == dict)
        try:
            if (value is not None 
                    and json.dumps(self._c[name]) != json.dumps(value)):
                msg = cat('config value [ %s ] for [ %s ] overwritten with ',
                        '[ %s ]') % (self._c[name], name, json.dumps(value))
                self.c[name] = value
                log.warn(msg)
            elif name in self._c:
                self.c[name] = self._c[name]
        except KeyError as e:
            assert(e.args[0]==name)
            log.debug('[ %s ] not in config, setting [ %s = %s ]' % (
                e.args[0], name, json.dumps(value)))
            self.c[name] = value
        if name not in self.c:
            if default is not None:
                self.c[name] = default
                log.warn(cat('no value available for [ %s ], using default: ',
                    '[ %s ]') % (name, json.dumps(default)))
            else:
                log.warn(cat('no value available for [ %s ] and no default ',
                    'supplied; setting to [ None ]') % name)
                self.c[name] = None

    def connect(self):
        """ Attempt to connect to the TreeAgePro application """
        try:
            self.app = TA.TreeAgeProApplication(self.host)
            if not self.app.isValid():
                raise Exception('The TreeAge Pro Application is not valid')
            log.info(self.app.getWorkspacePath())
        except Exception as e:
            msg = 'Unable to connect to TreeAge Pro Application!'
            if self.debug:
                log.error(msg)
            else:
                log.info('%s %s' % (msg,
                    'For a more detailed error message run in debug mode.'))
            raise

    def validate_treefile_xml(self, filepath):
        """ Basic XML validation

        Checks only that the xml parses and that the Tree tag is found in
        namespace {http://www.treeage.com/modeldefs/tree} """
        try:
            xml_root = ET.parse(filepath)
            namespace = '{http://www.treeage.com/modeldefs/tree}'
            treetag = 'Tree'
            if not xml_root.findall(namespace + treetag):
                msg = 'No %s tag in namespace %s in %s' % (treetag, namespace,
                        filepath)
                log.error(msg)
                raise Exception(msg)
        except Exception as e:
            msg = 'Tree xml did not pass basic validation!'
            if self.debug:
                log.info(msg)
            else:
                log.error(msg)
            # TODO raise only when not in debug mode after debug mode is
            # itself debugged; NOTE should always raise on ParseError, need to 
            # specialize this and other exceptions...
            raise

    def open_tree(self):
        """ Opens Treefile and stores tree object as instance member """
        try:
            filepath = os.path.join(self.workspace, self.treefile)
            self.validate_treefile_xml(filepath)    
            self.tree = self.app.getTree(filepath)
            if self.tree.isValid():
                log.info('opened tree: %s' % self.tree.getTreeName())
            else:
                msg = 'tree %s opened from file %s is not valid' % (
                        self.tree.getTreeName(), filepath)
                log.error(msg)
                raise Exception(msg)
        except Exception as e:
            log.error('Unable to open tree %s' % filepath)
            raise

    @property
    def variables(self):
        """ A dictionary with key = variable names and value = variable value

        This is memoized and only populated once (upon first access) unless
        using debug mode. """
        try:
            if (not hasattr(self, '_archive') 
                    or 'variables' not in self._archive):
                self._archive['variables'] = {v.getName(): v.getDescription() \
                        for v in self.tree.getVariables()}
            if self.debug or not hasattr(self, '_variables'):
                self._variables = {v.getName(): TaoiVariable(v) for v in \
                    self.tree.getVariables()}
            #if self.debug:
            #    for d in diff_dicts(self._archive['variables'],
            #            self._variables):
            #        log.debug(d)
        except Exception as e:
            log.error('Unable to read variables from tree') 
        return self._variables

    @property
    def basic_summary(self):
        """ A dictionary with key = item and value = item value
        
        `item` contains a variety of summary statistics for the tree.  This is
        memoized and only populated once (upon first access) unless using 
        debug mode. """
        if self.debug or not hasattr(self, '_basic_summary'):
            try:
                t = self.tree
                self._basic_summary = {
                       'file name': t.getFileName(),
                       'calculation method': t.getCalculationMethod(),
                       'variable count': len(t.getVariables()),
                       'trackers count': len(t.getTrackers()),
                       'tables count': len(t.getTables()),
                       'distributions count': len(t.getDistributions()),
                       }
            except Exception as e:
                log.error('Unable to generate basic summary')
        return self._basic_summary

    def print_summary(self):
        """ CSV formatted summaries of Tree properties """
        log.info('Printing basic summary as CSV')
        csv_key_value_dict(input_dict=self.basic_summary,
                key_name='item', value_name='value')
        log.info('Printing variables summary as CSV')
        csv_key_value_dict(input_dict=self.variables,
                key_name='variable_id', value_name='variable_description')

    def initialize_tables(self):
        """ Extracts all tables from the tree and initializes Taoi wrappers
        around them """

        for t in self.tree.getTables():
            self._tables.append(TaoiTable(t))

    def run_cost_effectiveness(self):
        """ Runs the cost-effectiveness anaysis in the tree and returns a
        dict of the columns """
        if self.tree.getCalculationMethod() != 'ct_costEff':
            msg = cat('Attempted to run cost-effectiveness analysis on a ',
                    'tree that does not support it!')
            log.error(msg)
            raise TaoiError(msg)
        report = self.tree.runAnalysis(TA.AnalysisType.costEffectivenes,
                None, self.tree.getRoot()).getTextReport()
        headers = report.getHeaders()
        rows = report.getRows()
        d = defaultdict(list)
        for r in rows:
            i = 0
            for h in headers:
                d[h].append(r[i])
                i += 1
        return d

    def run_experiment(self):
        e = self._c['experiment']
        log.info('Running experiment: %s' % e['name'])
        log.debug(self.variables)
        if ('variables' in e['root'] and 
                isinstance(e['root']['variables'], list) and
                len(e['root']['variables']) > 0):
            for v in e['root']['variables']:
                log.info('Updating root variable %s' % (
                    v['name'],))
                if 'comment' in v:
                    log.info('%s: %s' % (v['name'], v['comment']))
                if v['name'] not in self.variables:
                    msg = '%s not present in tree!'
                    log.error(msg)
                    raise TaoiError(msg)
                

                    
            
        

###############################################################################
########################################################################## main

def main():

    parser = argparse.ArgumentParser(description='TreeAge Object Interface')
    
    parser.add_argument('-d', '--debug', action='store_true', default=False,
            help='Enables debugging logic and logging')
    parser.add_argument('-t', '--treefile', default=None,
            help='Tree file (xml)')
    parser.add_argument('-H', '--host', default='localhost',
            help='Host running TreeAgePro')
    parser.add_argument('-o', '--outdir', default=None,
            help=cat('Output directory (defaults to workspace if it is ',
                'supplied, current working directory otherwise)'))
    parser.add_argument('-w', '--workspace', default=None,
            help=cat('Path prefix for workspace (defaults to current working ',
                'directory)'))
    parser.add_argument('-p', '--prefix', default=None,
            help='Prefix used for all output files (defaults to a timestamp)')
    parser.add_argument('-c', '--config', default=None,
            help='YAML-format config file (command line args override config)')
    parser.add_argument('-s', '--summary', action='store_true', default=False,
            help='prints a summary of tree attributes')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    global log
    log = logging.getLogger('trolley')

    log.info(args)
    
    ts = TrolleySession(host=args.host, treefile=args.treefile, workspace=args.workspace,
            debug=args.debug, auto=True, config=args.config)

    if args.summary:
        ts.print_summary()

if __name__=="__main__":
    main()













