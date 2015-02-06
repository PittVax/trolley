#!/usr/bin/env jython

# NOTE 2.7 compatibility is required (jython 2.7+)

# common java classes should already be in the classpath, so go ahead and
# import them
import java.rmi.RemoteException
import java.net.ConnectException
import java.rmi.ConnectException
import java.util.Collections as JavaCollections
import java.util.HashMap as JavaHashMap
import java.util.Map as JavaMap

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
import os, sys, csv
import hashlib
from xml.etree import ElementTree as ET

###############################################################################

def cat(*args):
    return ''.join([str(i) for i in args])

def csv_key_value_dict(input_dict, key_name='key', value_name='value',
        out=sys.stdout):
    w = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
    w.writerow([key_name, value_name])
    for k,v in input_dict.iteritems():
        w.writerow([k,v])

###############################################################################
class TaoiVariableError(Exception):
    pass

class TaoiVariable(object):
    """ Thin wrapper over TreeAge Variable """
    def __init__(self, variable=None, **kwargs):
        try:
            if variable is None:
                log.debug(cat('No instance variable to copy - instantiating ',
                    'a new one'))
                self.var = TA.Variable()
            elif type(variable) == TA.Variable:
                log.debug('Copying from supplied variable')
                self.var = variable
            elif type(variable) == TaoiVariable:
                msg = cat('Copy-from-instance logic has not been implemented',
                        ' yet.  Please use an instance of TA.Variable')
                log.error(msg)
                raise Exception(msg)
            else:
                msg = '"variable" argument of type %s not allowed!' % (
                        type(variable),)
                log.error(msg)
                raise Exception(msg)
            self.update_from_dict(kwargs)
        except Exception as e:
            if not isinstance(e, TaoiVariableError):
                raise
                
    def __call__(self):
        """ Overload function operator to return the wrapped TA.Variable """
        return self.var

    def properties(self):
        return [k for k,v in self.__class__.__dict__.items() \
                if type(v) is property]
    
    # variable comment
    @property
    def comment(self):
        return self.var.getComment()
    @comment.setter
    def comment(self, v):
        self.var.setComment(v)
    # variable description
    @property
    def description(self):
        return self.var.getDescription()
    @description.setter
    def description(self, v):
        self.var.setDescription(v)
    # variable high value
    @property
    def high(self):
        return self.var.getHighValue()
    @high.setter
    def high(self, v):
        self.var.setHighValue(v)
    # variable low value
    @property
    def low(self):
        return self.var.getLowValue()
    @low.setter
    def low(self, v):
        self.var.setLowValue()
    # variable name
    @property
    def name(self):
        return self.var.getName()
    @name.setter
    def name(self, v):
        self.var.setName(v)

    # root definition getters/setters
    @property
    def root_set(self):
        return self.var.isRootDefinitionSet()
    @property
    def root_definition(self):
        if self.root_set:
            return self.var.getRootDefinition()
        else:
            msg = cat('Root definition does not exist! Check the property ',
                    'TaoiVariable.root_set first!')
            log.error(msg)
            raise TaoiVariableError(msg)
    @root_definition.setter
    def root_definition(self, v):
        if isinstance(v, TA.VariableDefinition):
            self.var.setRootDefinition(v)
        else:
            msg = cat('root_definition must be set to an instance of %s, ',
                    'but an instance of %s was supplied') % (
                    type(TA.VariableDefinition), type(v))
            log.error(msg)
            raise TaoiVariableError(msg)
    @property
    def root_value(self):
        return self.root_definition.getValue()
    @root_value.setter
    def root_value(self, v):
        self.root_definition.setValue(v)


    


    def update_from_dict(self, dictionary):
        props = self.properties()
        for k,v in dictionary.iteritems():
            if k in props:
                try:
                    msg = 'setting [ %s ] to [ %s ]' % (k, v)
                    v_old = self.__getattribute__(k)
                    msg += ' (originally was [ %s ])' % v_old
                    self.__setattr__(k, v)
                    log.debug('Success ' + msg)
                except Exception as e:
                    log.debug('Failure ' + msg)
                    raise

    

class TaoiSession(object):
    def __init__(self, host=None, treefile=None, workspace=None,
            outdir=None, debug=None, auto=None, config=None):

        self._archive = dict()

        self.configfile = config
        self.config_workspace(config, workspace)
        self.setc('outdir', outdir, self.workspace)

        self.setc('debug', debug)
        self.setc('auto', auto)

        self.setc('host', host, 'localhost')
        if self.host != 'localhost':
            self._fail('Only local execution is supported!')
       
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
            self.app = TA.TreeAgeProApplication()
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
                self._variables = {v.getName(): v.getDescription() for v in \
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

###############################################################################

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
    log = logging.getLogger('taoi_main')

    log.info(args)
    
    ts = TaoiSession(host=args.host, treefile=args.treefile, workspace=args.workspace,
            debug=args.debug, auto=True, config=args.config)

    if args.summary:
        ts.print_summary()

if __name__=="__main__":
    main()













