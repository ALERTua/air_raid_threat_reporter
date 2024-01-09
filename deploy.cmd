@echo off
set DOCKER_BUILDKIT=1
set DOCKER_REGISTRY=registry.alertua.duckdns.org
echo DOCKER_REGISTRY: %DOCKER_REGISTRY%

for %%I in ("%~dp0.") do set "IMAGE_NAME=%%~nxI"
echo IMAGE_NAME: %IMAGE_NAME%

set IMAGE_TAG=latest
echo IMAGE_TAG: %IMAGE_TAG%

set BUILD_TAG=%DOCKER_REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%
echo BUILD_TAG: %BUILD_TAG%

set "BUILD_PATH=%~dp0"
echo BUILD_PATH: %BUILD_PATH%

set DOCKER_EXE=docker
rem set DOCKER_OPTS=--insecure-registry=%DOCKER_REGISTRY%
set DOCKER_OPTS=--max-concurrent-uploads=10 --max-concurrent-downloads=10

echo DOCKER_REMOTE: %DOCKER_REMOTE%

choice /C YN /m "Proceed?"
if ["%errorlevel%"] NEQ ["1"] (
	exit /b
)


if not defined DOCKER_REMOTE (
    set DOCKER_SERVICE=com.docker.service
    where %DOCKER_EXE% >nul || (
        set "DOCKER_EXE=%ProgramFiles%\Docker\Docker\resources\bin\docker.exe"
    )

    pushd %~dp0
    sc query %DOCKER_SERVICE% | findstr /IC:"running" >nul || (
        echo starting Docker service %DOCKER_SERVICE%
        sudo net start %DOCKER_SERVICE% || (
            echo "Error starting docker service %DOCKER_SERVICE%
            exit /b
        )
    )

    tasklist | findstr /IC:"Docker Desktop.exe" >nul || (
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
        :loop
            call docker info >nul 2>nul || (
                timeout /t 1 >nul
                goto loop
            )
        rem timeout /t 60
    )
)

"%DOCKER_EXE%" build -t %BUILD_TAG% %BUILD_PATH% || exit /b
"%DOCKER_EXE%" push %DOCKER_REGISTRY%/%IMAGE_NAME% || exit /b

@REM net stop %DOCKER_SERVICE% || exit /b
