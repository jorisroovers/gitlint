
:: Use pushd, so we can popd back at the end (directory changes are not contained inside batch file)
PUSHD C:\Windows\Temp

:: Determine unique git repo name
:: Note that date/time parsing on windows is locale dependent, so this might not work on every windows machine
:: (see https://stackoverflow.com/questions/203090/how-do-i-get-current-date-time-on-the-windows-command-line-in-a-suitable-format)
@echo off
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
For /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a-%%b)
echo %mydate%_%mytime%

set Reponame=gitlint-test-%mydate%_%mytime%
echo %Reponame%

:: Create git repo
git init %Reponame%
cd %Reponame%

:: Do some basic config
git config user.name gïtlint-test-user
git config user.email gitlint@test.com
git config core.quotePath false
git config core.precomposeUnicode true

:: Add a test commit
echo "tëst 123" > test.txt
git add test.txt
git commit -m "test cömmit title" -m "test cömmit body that has a bit more text"

:: echo. -> the dot allows us to print and empty line
echo.
echo Created C:\Windows\Temp\%Reponame%
:: Move back to original dir
POPD
