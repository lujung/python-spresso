@ECHO OFF

pushd %~dp0

if "%1" == "" goto help
if "%1" == "init" goto init
if "%1" == "test" goto test
if "%1" == "coverage" goto coverage
if "%1" == "apidoc" goto apidoc
goto help

:init
pip3 install requirements.txt
goto end

:test
python tests/__init__.py test
goto end

:coverage
python tests/__init__.py coverage
goto end

:help
echo Supported commands are:
echo init
echo test
echo coverage

:end
popd
