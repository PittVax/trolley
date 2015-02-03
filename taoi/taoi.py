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


class TaoiSession(object):
    def __init__(self, host='localhost', treefilename=None, workingdir=None):
        if host != 'localhost':
            raise Exception('only local execution is supported')
        self.workingdir = workingdir
        self.treefilename = treefilename
    def connect(self):
        try:
            self.ta_app = TreeAgeProApplication()
            if not self.ta_app.isValid():
                raise Exception('The TreeAge Pro Application is not valid')
        except Exception as e:
            print('Unable to connect to TreeAge Pro Application')
            raise
    def open_tree(self):
        try:
            self.tree = self.ta_app.openTree(self.treefilename)
        except JavaRemoteException as e:
            print('Unable to open tree %s' % self.treefilename)

def main():

    parser = argparse.ArgumentParser(description='TreeAge Object Interface Wrapper')
    
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-t', '--tree',
            help='Tree file (xml)')
    parser.add_argument('-H', '--host', default='localhost',
            help='Host running TreeAgePro')
    parser.add_argument('-o', '--output_directory', default='output',
            help='Output directory')

    args = parser.parse_args()

    print(args)
    
    ts = TaoiSession(args.host, args.tree, args.output_directory)

if __name__=="__main__":
    main()













