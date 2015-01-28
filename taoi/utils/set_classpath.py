#!/usr/bin/env jython

import sys, os

java_lib_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../java/lib')
java_lib_jars = ['treeagepro.oi.jar',]
java_classpath = [os.path.join(java_lib_dir, j) for j in java_lib_jars]

sys.path.extend(java_classpath)
