
@echo off
cd %~dp0
set DOCKER_HOST=tcp://docker:2375
set DOCKER_REMOTE=1
call deploy.cmd
