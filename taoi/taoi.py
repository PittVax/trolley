#!/usr/bin/env jython

# NOTE 2.7 compatibility is required (jython 2.7+)

# common java classes should already be in the classpath, so go ahead and
# import them
import java.rmi.RemoteException as JavaRemoteException;
import java.util.Collections as JavaCollections;
import java.util.HashMap as JavaHashMap;
import java.util.Map as JavaMap;

try:
    import utils.set_classpath
    # import the treeage pro object interface classes
    from com.treeage.treeagepro.oi import AnalysisType
    from com.treeage.treeagepro.oi import Report
    from com.treeage.treeagepro.oi import Tree
    from com.treeage.treeagepro.oi import TreeAgeProApplication
except Exception as e:
    raise

import argparse
import logging
log = logging.getLogger(__name__)
import yaml, json
import os

class TaoiSession(object):
    def __init__(self, host=None, treefile=None, workspace=None,
            outdir=None, debug=None, auto=None, config=None):

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
        
        if self.auto:
            self.connect()
            self.open_tree()

    def _fail(self, msg):
        log.error(msg)
        raise Exception(msg)

    @property
    def auto(self):
        return self.c['auto']
    @property
    def debug(self):
        return self.c['debug']
    @property
    def host(self):
        return self.c['host']
    @property
    def treefile(self):
        return self.c['treefile']
    @property
    def workspace(self):
        return self.c['workspace']

    def config_workspace(self, config, workspace):
        """ Reads the config and workspace options and sets class members """
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
                log.debug('No workspace provided, attempt to use current directory')
            else:
                log.debug('attempting to use supplied workspace without yaml config')
        finally:
            if not os.access(_workspace, os.R_OK):
                msg = 'No read access to workspace path: %s' % _workspace
                log.error(msg)
                raise Exception(msg)
            if workspace is not None and workspace in self.c:
                log.warn('workspace specified in config and as argument; '\
                        'using supplied argument: %s' % workspace)
        # when debugging log the original config dicts
        log.debug('supplied config = %s' % json.dumps(self._c))
        # update the workspace param in the master config
        self.setc('workspace',_workspace)

    def setc(self, name, value, default=None):
        assert(hasattr(self,'c'))
        assert(type(self.c) == dict)
        assert(hasattr(self,'_c'))
        assert(type(self._c) == dict)
        try:
            if value is not None and json.dumps(self._c[name]) != json.dumps(value):
                msg = 'config value [ %s ] for [ %s ] overwritten with [ %s ]' % (
                    self._c[name], name, json.dumps(value))
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
                log.warn('no value available for [ %s ], using default: [ %s ]' % (
                    name, json.dumps(default)))
            else:
                log.warn('no value available for [ %s ] and no default ' \
                        'supplied; setting to [ None ]' % name)
                self.c[name] = None

    def connect(self):
        try:
            self.app = TreeAgeProApplication()
            if not self.app.isValid():
                raise Exception('The TreeAge Pro Application is not valid')
            log.info(self.app.getWorkspacePath())
        except Exception as e:
            log.error('Unable to connect to TreeAge Pro Application')
            raise
    def open_tree(self):
        try:
            _treefile = os.path.join(self.workspace, self.treefile)
            self.tree = self.app.getTree(_treefile)
            if self.tree.isValid():
                log.info('opened tree: %s' % self.tree.getTreeName())
            else:
                msg = 'tree %s opened from file %s is not valid' % (
                        self.tree.getTreeName(), _treefile)
                log.error(msg)
                raise Exception(msg)
        except JavaRemoteException as e:
            log.error('Unable to open tree %s' % _treefile)
    def tree_summary(self):
        pass

def main():

    parser = argparse.ArgumentParser(description='TreeAge Object Interface Wrapper')
    
    parser.add_argument('-d', '--debug', action='store_true', default=False,
            help='Enables debugging logic and logging')
    parser.add_argument('-t', '--treefile', default=None,
            help='Tree file (xml)')
    parser.add_argument('-H', '--host', default='localhost',
            help='Host running TreeAgePro')
    parser.add_argument('-o', '--outdir', default=None,
            help='Output directory (defaults to workspace if it is supplied, '\
                    'current working directory otherwise)')
    parser.add_argument('-w', '--workspace', default=None,
            help='Path prefix for workspace (defaults to current working directory)')
    parser.add_argument('-p', '--prefix', default=None,
            help='Prefix used for all output files (defaults to a timestamp)')
    parser.add_argument('-c', '--config', default=None,
            help='YAML-format config file (command line args override config)')


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

if __name__=="__main__":
    main()













