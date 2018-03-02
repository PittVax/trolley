# Ctrl+C exits interactive terminals and destroys container.
# All unsaved data will be lost
# at the jython prompt, exit() exits the jython shell and returns to bash in the container

# Launches jython interactive interpreter in containter
function Start-jython {docker run -it --rm -v ${PWD}:/scratch -w /scratch mcandre/docker-jython:latest jython}
# Launches bash shell in containter
function Start-bash {docker run -it --name docker_jython -v ${PWD}:/scratch -w /scratch mcandre/docker-jython:latest }