
@echo off
cd %~dp0
set DOCKER_HOST=tcp://docker:2375
set DOCKER_REMOTE=1
echo Calling deploy for %DOCKER_HOST%
call deploy.cmd
