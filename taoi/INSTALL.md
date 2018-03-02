# Installation
Download or clone this repo to your local machine.

## TreeAge configuration
1. Place TreeAge projects in `./Trees`"
1. Import existing projects into TreeAge OR turn `./trees` into a project
    * Import existing projects
      * Launch TreeAge
      * Right click in the projects panel
      * Select `Import...`
      * Select `General>Existing Projects into Workspace`
      * Click `Next`
      * Choose `root directory` option and navigate to `./Trees`
      * Tick boxes by available projects
      * **DO NOT** select `Copy projects into workspace`
      * Click `Finish`
      * Selected projects should now appear in the projects panel. 
    * Turn `./trees` into a project
      * Launch TreeAge  
      * Select `File>Projects>New Project`
      * Navigate to and select `./trees`
      * Click `Ok`
      * The Project `trees` should now appear in the project panel
              
1. Optionally increase memory available to TreeAge
      * Launch TreeAge as an administrator
      * Select `Window>Application Preferences`
      * Select `General>Startup settings`
      * Increase `Maximum Java heap space:`
      * Alternatively, alter settings directly in the TreeAgePro.ini file
        Possibly located at `/Applications/TreeAgePro/TreeAgePro.app/Contents/MacOS/TreeAgePro.ini`
        * Original settings were:  
        ```
        -XX:MaxPermSize=256m  
        -Xms128m  
        -Xmx1024m
        ```  
        * Doubling these gives:  
        ```
        -XX:MaxPermSize=512m  
        -Xms256m  
        -Xmx2048m  
        ```
1. Open the desired tree in TreeAge

## Trolley configuration
The TreeAge Object Interface (taoi) requires jython  
Trolley requires PyYAML  

1. Install dependencies to your machine (not awesome)
  * [jython](http://www.jython.org/)  
  * [PyYAML](http://pyyaml.org/wiki/PyYAML)  
  * A python virtual environment is recommended for jython dependencies
1. Use trolley as a docker container (very awesome)
  * Install [docker](https://docs.docker.com/)  
  * Open a shell in the root of this repo `./trolley`
  * Run the following command in PowerShell or OSX terminal  
  `docker run -it --rm --name trolley --mount type=bind,source=$(pwd),target=/root/trolley pittvax/trolley:latest`
  * Run the following command in Git-Bash  
    `winpty docker run -it --rm --name trolley --mount type=bind,source=$(pwd),target=/root/trolley pittvax/trolley:latest`
1. Use trolley in a virtual machine (maybe awesome?)
  * Install [Virtual Box](https://www.virtualbox.org/wiki/Downloads)  
  * Install [Vagrant](https://www.vagrantup.com/)  
  * Open a shell in the root of this repo `./trolley`  
  * Run `vagrant up`

# My notes
`

trolley.py -help 
