# Ctrl+C exits interactive terminals and destroys container.
# All unsaved data will be lost
# at the jython prompt, exit() exits the jython shell and returns to bash in the container

# Launches bash in jython containter
function Start-Container {docker run -it --rm --name trolley --mount type=bind,source=$(pwd),target=/root/trolley --workdir="/root/trolley" pittvax/trolley:latest}

# Launches jython in interactive mode in jython containter
function Start-jython {docker run -it --rm --name trolley --mount type=bind,source=$(pwd),target=/root/trolley --workdir="/root/trolley" pittvax/trolley:latest jython}

# Launches jython and runs trolley.py
function Start-Trolley {docker run -it --rm --name trolley --mount type=bind,source=$(pwd),target=/root/trolley --workdir="/root/trolley" pittvax/trolley:latest jython taoi/trolley.py $args}