#!/usr/bin/env jython
import java.rmi.RemoteException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import utils.set_classpath

import com.treeage.treeagepro.oi.AnalysisType;
import com.treeage.treeagepro.oi.Report;
import com.treeage.treeagepro.oi.Tree;
from com.treeage.treeagepro.oi import TreeAgeProApplication;


app = TreeAgeProApplication();

if app.isValid():
    print('Success!')
else:
    print("Cannot find TreeAgePro application running locally.");

