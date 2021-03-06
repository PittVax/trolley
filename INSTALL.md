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
      * Tick boxes for available projects
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
    Possibly located at `/Applications/TreeAgePro/TreeAgePro.app/Contents/MacOS/TreeAgePro.ini` OR  
    `C:\Program Files\TreeAgePro\TreeAgePro.ini`
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
There are three configuration options.  

1. Install dependencies to your machine (not awesome)
    * [jython](http://www.jython.org/)  
    * [PyYAML](http://pyyaml.org/wiki/PyYAML)  
    * A python virtual environment is recommended for jython dependencies  
1. Use trolley in a virtual machine (a little awesome)
    * Install [Virtual Box](https://www.virtualbox.org/wiki/Downloads)  
    * Install [Vagrant](https://www.vagrantup.com/)  
    * Open a shell in the root of this repo `./trolley`  
    * Run `vagrant up`
    * Mount virtual machine with `vagrant ssh`  
1. Use trolley as a docker container (very awesome)
    * Install [docker](https://docs.docker.com/)  
    * `Makefile` provides useful commands in the format `make <command>`  
    * Open a shell in the root of this repo `./trolley`
    * Run `make up` to build the app

# Trolley cli
Help is available with `trolley.py -help`  

## Usage
`trolley.py` must be called from jython. The syntax will vary based on how jython 
is installed. 
  * For locally installed dependencies use:  
  `jython <path to trolley>/taoi/trolley.py <args>`  

  * For Trolley on Virtual Box:
    * Mount virtual machine with `vagrant ssh`
    * `cd ~/trolley`
    * Run `taoi/trolley.py <args>`
    * Files in `~/trolley` are shared with the host
    * Exit virtual machine with `exit`
    * Shut down virtual machine with `vagrant down`
    * Delete virtual machine with `vagrant destroy`
    
  * For Trolley on Docker use:  
  `Make trolley -- <args>`  
    The extra `--` is mandatory EG: `make trolley -- --help`
    Consider setting an alias as 
    ```
    # nix
    alias trolley="make trolley -- "
    
    # PowerShell
    function Start-Trolley {make trolley -- $args}
    Set-Alias trolley Start-Trolley
    
    # example command with alias set
    trolley --help
    ```


## Examples
#TODO
