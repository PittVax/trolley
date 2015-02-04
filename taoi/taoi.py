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
import yaml
import os

class TaoiSession(object):
    def __init__(self, host=None, treefile=None, workspace=None,
            debug=None, auto=None, config=None):

        self.configfile = config
        self.config_workspace(config, workspace)

#        self.debug = debug
#        self.auto = auto
#        
#        if host != 'localhost':
#            msg = 'only local execution is supported'
#            log.error(msg)
#            raise Exception(msg)
#        
#        self.set_workspace(workspace)
#        self.set_treefile(treefile)
#        
#        if self.auto:
#            self.connect()
#            self.open_tree()

    def config_workspace(self, config, workspace):
        """ Reads the config and workspace options and sets class members """
        try:
            self.workspace = os.getcwd() if workspace is None else workspace
            with open(os.path.join(self.workspace,config)) as f:
                self.c = yaml.safe_load(f)
            log.debug('successfully parsed yaml config file')
        except Exception as e:
            if workspace is None:
                msg = 'No workspace provided and unable to parse supplied' \
                    ' config file (%s)' % config
                log.error(msg)
                e.args += (msg,)
                raise
            else:
                self.c = dict(workspace=self.workspace)
                log.debug('attempting to use supplied workspace without yaml config')
        finally:
            if not os.access(self.workspace, os.R_OK):
                msg = 'No read access to workspace path: %s' % self.workspace
                log.error(msg)
                raise Exception(msg)
            if workspace is not None and workspace in self.c:
                log.warn('workspace specified in config and as argument; '\
                        'using supplied argument: %s' % workspace)
        print(self.c)




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
    
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('-t', '--tree', default=None,
            help='Tree file (xml)')
    parser.add_argument('-H', '--host', default='localhost',
            help='Host running TreeAgePro')
    parser.add_argument('-o', '--outdir', default=None,
            help='Output directory')
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
    
    ts = TaoiSession(args.host, args.tree, args.outdir,
            debug=args.debug, auto=True, config=args.config)

if __name__=="__main__":
    main()













