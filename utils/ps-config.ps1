$ScriptPath = Split-Path $MyInvocation.MyCommand.Path
#Include docker aliases
Import-Module $ScriptPath\docker_aliases.psm1

# Import Start-jython command
Import-Module $ScriptPath\trolley_aliases.psm1


