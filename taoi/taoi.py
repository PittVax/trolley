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


class TaoiSession(object):
    def __init__(self, host='localhost', treefilename=None, workingdir=None,
            debug=False, auto=True):
        if host != 'localhost':
            msg = 'only local execution is supported'
            log.error(msg)
            raise Exception(msg)
        self.workingdir = workingdir
        self.treefilename = treefilename
        if auto:
            self.connect()
            self.open_tree()
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
            self.tree = self.app.getTree(self.treefilename)
            if self.tree.isValid():
                log.info('opened tree: %s' % self.tree.getTreeName())
            else:
                msg = 'tree %s opened from file %s is not valid' % (
                        self.tree.getTreeName(), self.treefilename)
                log.error(msg)
                raise Exception(msg)
        except JavaRemoteException as e:
            log.error('Unable to open tree %s' % self.treefilename)

def main():

    parser = argparse.ArgumentParser(description='TreeAge Object Interface Wrapper')
    
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('-t', '--tree',
            help='Tree file (xml)')
    parser.add_argument('-H', '--host', default='localhost',
            help='Host running TreeAgePro')
    parser.add_argument('-o', '--output_directory', default='output',
            help='Output directory')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
    global log
    log = logging.getLogger('taoi_main')

    log.info(args)
    
    ts = TaoiSession(args.host, args.tree, args.output_directory,
            args.debug, auto=True)

if __name__=="__main__":
    main()













