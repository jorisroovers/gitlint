
:: Use pushd, so we can popd back at the end (directory changes are not contained inside batch file)
PUSHD C:\Windows\Temp

@echo off

:: Determine unique git repo name
:: We use Python to determine to get a datetime stamp since other workarounds in BATCH are locale dependent
:: Note that we double escape the % in the format string to %%
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "import datetime; print(datetime.datetime.now().strftime('%%Y-%%m-%%d_%%H-%%M-%%S'))"`) DO (
SET datetime=%%F
)
echo %datetime%
set Reponame=gitlint-test-%datetime%
echo %Reponame%

:: Create git repo
git init --initial-branch main %Reponame%
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

:: echo. -> the dot allows us to print an empty line
echo.
echo Created C:\Windows\Temp\%Reponame%

:: Move back to original dir
POPD