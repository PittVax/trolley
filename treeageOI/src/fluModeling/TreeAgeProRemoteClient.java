/**************************************************************************
 *   File: TreeAgeProRemoteClient.java
 *
 *   Version 1.0
 *   Date            Author          Changes
 *   09.06.2010      Ilya Kanonirov  Created
 *
 *   Copyright (c) 2010 TreeAge Software, Inc.
 *   All rights reserved.
 ****************************************************************************/
package fluModeling;

import java.rmi.RemoteException;

import com.treeage.treeagepro.oi.Tree;
import com.treeage.treeagepro.oi.TreeAgeProApplication;

/**
 * This example uses Object Interface for Java to remotely connect to TreeAge Pro.
 * 
 * @author Ilya Kanonirov
 * @version 1.0 09.06.2010
 */
public class TreeAgeProRemoteClient {

    /**
     * The default main method called on application start.
     * @param args
     */
    public static void main(String[] args) {
        new TreeAgeProRemoteClient();
    }

    private TreeAgeProRemoteClient() {
        // Connects locally to TP2011. For remote use see TreeAgeProApplication constructors
        // such as TreeAgeProApplication(host).
        TreeAgeProApplication app = new TreeAgeProApplication();
        if (!app.isValid()) {
            System.out.println("Cannot find TP2011 application running locally.");
            return;
        }

        try {
            Tree tree = app.getTopTree();
            if (tree.isValid()) {
                System.out.println("The currently opened top tree is: " + tree.getTreeName());
            } else {
                System.out.println("No one tree document is opened in TP2011.");
            }
        } catch (RemoteException re) {
            System.out.println("Connection to TP2011 application is lost.");
        }
    }
}
