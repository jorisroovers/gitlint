#!/bin/bash


help(){
    echo "Usage: $0 [OPTION]..."
    echo "Run gitlint's test suite(s) or some convience commands"
    echo "  -h, --help               Show this help output"
    echo "  -c, --clean              Clean the project of temporary files"
    echo "  -p, --pep8               Run pep8 checks"
    echo "  -l, --lint               Run pylint checks"
    echo "  -g, --git                Run gitlint checks"
    echo "  -i, --integration        Run integration tests"
    echo "  -b, --build              Run build tests"
    echo "  -a, --all                Run all tests and checks (unit, integration, pep8, git)"
    echo "  -e, --envs [ENV1],[ENV2] Run tests against specified python environments (envs: 26,27,33,34,35,pypy2)."
    echo "                           Also works for integration, pep8 and lint tests."
    echo "  --all-env                Run all tests against all python environments"
    echo "  --install                Install virtualenvs for the --envs specified"
    echo "  --uninstall              Remove virtualenvs for the --envs specified"
    echo "  --exec [CMD]             Execute [CMD] in the --envs specified"
    echo "  -s, --stats              Show some project stats"
    echo "  --no-coverage            Don't make a unit test coverage report"
    echo ""
    exit 0;
}

RED="\033[31m"
YELLOW="\033[33m"
BLUE="\033[94m"
GREEN="\033[32m"
NO_COLOR="\033[0m"

title(){
    MSG="$BLUE$1$NO_COLOR"
    echo -e $MSG
}

subtitle() {
    MSG="$YELLOW$1$NO_COLOR"
    echo -e $MSG
}

fatal(){
    MSG="$RED$1$NO_COLOR"
    echo -e $MSG
    exit 1
}

assert_root(){
    if [ "$(id -u)" != "0" ]; then
        fatal "$1"
    fi
}

# Utility method that prints SUCCESS if a test was succesful, or FAIL together with the test output
handle_test_result(){
    RESULT="$1"
    if [ -z "$RESULT" ]; then
        echo -e "${GREEN}SUCCESS${NO_COLOR}"
    else
        echo -e "${RED}FAIL\n${RESULT}${NO_COLOR}"
    fi
}

run_pep8_check(){
    # FLAKE 8
    # H307: like imports should be grouped together
    # H405: multi line docstring summary not separated with an empty line
    # H803: git title must end with a period
    # H904: Wrap long lines in parentheses instead of a backslash
    # H802: git commit title should be under 50 chars
    # H701: empty localization string
    FLAKE8_IGNORE="H307,H405,H803,H904,H802,H701"
    # exclude settings files and virtualenvs
    FLAKE8_EXCLUDE="*settings.py,*.venv/*.py"
    echo -ne "Running flake8..."
    RESULT=$(flake8 --ignore=$FLAKE8_IGNORE --max-line-length=120 --exclude=$FLAKE8_EXCLUDE gitlint qa examples)
    local exit_code=$?
    handle_test_result "$RESULT"
    return $exit_code
}

run_unit_tests(){
    clean
    # py.test -s  => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    OMIT="*pypy*"
    if [ -n "$testargs" ]; then
        coverage run --omit=$OMIT -m pytest -rw -s "$testargs"
    else
        coverage run --omit=$OMIT -m pytest -rw -s gitlint
    fi
    TEST_RESULT=$?
    if [ $include_coverage -eq 1 ]; then
        COVERAGE_REPORT=$(coverage report -m)
        echo "$COVERAGE_REPORT"
    fi

    return $TEST_RESULT;
}

run_integration_tests(){
    clean
    # Make sure the version of python used by the git hooks in our integration tests
    # is the same one as the one that is currently active. In order to achieve this, we need to set
    # GIT_EXEC_PATH (https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables) to the current PATH, otherwise
    # the git hooks will use the default PATH variable as defined by .bashrc which doesn't contain the current
    # virtualenv's python binary path.
    export GIT_EXEC_PATH="$PATH"

    # py.test -s => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    if [ -n "$testargs" ]; then
        py.test -s "$testargs"
    else
        py.test -s qa/
    fi
}

run_git_check(){
    echo -ne "Running gitlint...${RED}"
    RESULT=$(gitlint 2>&1)
    local exit_code=$?
    handle_test_result "$RESULT"
    # FUTURE: check if we use str() function: egrep -nriI "( |\(|\[)+str\(" gitlint | egrep -v "\w*#(.*)"
    return $exit_code
}

run_lint_check(){
    echo -ne "Running pylint...${RED}"

    # Skip pylint for python 3.6, since it's not supported
    if [[ $(python --version 2>&1) == 'Python 3.6'* ]]; then
        echo -e "${YELLOW}SKIPPING${NO_COLOR} (See https://github.com/PyCQA/pylint/issues/1072)"
        return 0
    fi

    RESULT=$(pylint gitlint qa --rcfile=".pylintrc" -r n)
    local exit_code=$?
    handle_test_result "$RESULT"
    return $exit_code
}

run_build_test(){
    clean
    echo -n "Making sure wheel is installed..."
    pip install "$(grep --color=never wheel requirements.txt)" > /dev/null
    echo -e "${GREEN}DONE${NO_COLOR}"

    datestr=$(date +"%Y-%m-%d-%H-%M-%S")
    temp_dir="/tmp/gitlint-build-test-$datestr"

    # Copy gitlint to a new temp dir
    echo -n "Copying gitlint to $temp_dir..."
    mkdir "$temp_dir"
    rsync -az --exclude ".vagrant" --exclude ".git" --exclude ".venv*" . "$temp_dir"
    echo -e "${GREEN}DONE${NO_COLOR}"

    # Update the version to include a timestamp
    echo -n "Writing new version to file..."
    version_file="$temp_dir/gitlint/__init__.py"
    version_str="$(cat $version_file)"
    version_str="${version_str:0:${#version_str}-1}-$datestr\""
    echo "$version_str" > $version_file
    echo -e "${GREEN}DONE${NO_COLOR}"
    # Attempt to build the package
    echo "Building package ..."
    pushd "$temp_dir"
    # Copy stdout file descriptor so we can both print output to stdout as well as capture it in a variable
    # https://stackoverflow.com/questions/12451278/bash-capture-stdout-to-a-variable-but-still-display-it-in-the-console
    exec 5>&1
    output=$(python setup.py sdist bdist_wheel | tee /dev/fd/5)
    local exit_code=$?
    popd
    # Cleanup :-)
    rm -rf "$temp_dir"

    # Check for deprecation message in python 2.6
    if [[ $(python --version 2>&1) == 'Python 2.6'* ]]; then
        echo -n "[Python 2.6] Checking for deprecation warning..."
        echo "$output" | grep "A future version of gitlint will drop support for Python 2.6" > /dev/null
        exit_code=$((exit_code + $?))
        if [ $exit_code -gt 0 ]; then
            echo -e "${RED}FAIL${NO_COLOR}"
        else
            echo -e "${GREEN}SUCCESS${NO_COLOR}"
        fi
    fi

    # Print success/no success
    if [ $exit_code -gt 0 ]; then
        echo -e "Building package...${RED}FAIL${NO_COLOR}"
    else
        echo -e "Building package...${GREEN}SUCCESS${NO_COLOR}"
    fi

    return $exit_code
}

run_stats(){
    clean # required for py.test to count properly
    echo "*** Code ***"
    radon raw -s gitlint | tail -n 6
    echo "*** Docs ***"
    echo "    Markdown: $(cat docs/*.md | wc -l | tr -d " ") lines"
    echo "*** Tests ***"
    nr_unit_tests=$(py.test gitlint/ --collect-only | grep TestCaseFunction | wc -l)
    nr_integration_tests=$(py.test qa/ --collect-only | grep TestCaseFunction | wc -l)
    echo "    Unit Tests: ${nr_unit_tests//[[:space:]]/}"
    echo "    Integration Tests: ${nr_integration_tests//[[:space:]]/}"
    echo "*** Git ***"
    echo "    Commits: $(git rev-list --all --count)"
    echo "    Commits (master): $(git rev-list master --count)"
    echo "    First commit: $(git log --pretty="%aD" $(git rev-list --max-parents=0 HEAD))"
    echo "    Contributors: $(git log --format='%aN' | sort -u | wc -l | tr -d ' ')"
    echo "    Releases (tags): $(git tag --list | wc -l | tr -d ' ')"
}

clean(){
    echo -n "Cleaning the site, build, dist, *.pyc and all __pycache__directories..."
    find gitlint -type d  -name "*.pyc" -exec rm -rf {} \; 2> /dev/null
    find qa -type d  -name "*.pyc" -exec rm -rf {} \; 2> /dev/null
    find gitlint -type d  -name "__pycache__" -exec rm -rf {} \; 2> /dev/null
    find qa -type d  -name "__pycache__" -exec rm -rf {} \; 2> /dev/null
    rm -rf "site" "dist" "build"
    echo -e "${GREEN}DONE${NO_COLOR}"
}

run_all(){
    local exit_code=0
    subtitle "# UNIT TESTS ($(python --version 2>&1), $(which python)) #"
    run_unit_tests
    exit_code=$((exit_code + $?))
    subtitle "# INTEGRATION TESTS ($(python --version 2>&1), $(which python)) #"
    run_integration_tests
    exit_code=$((exit_code + $?))
    subtitle "# BUILD TEST ($(python --version 2>&1), $(which python)) #"
    run_build_test
    exit_code=$((exit_code + $?))
    subtitle "# STYLE CHECKS ($(python --version 2>&1), $(which python)) #"
    run_pep8_check
    exit_code=$((exit_code + $?))
    run_lint_check
    exit_code=$((exit_code + $?))
    run_git_check
    exit_code=$((exit_code + $?))
    return $exit_code
}

uninstall_virtualenv(){
    version="$1"
    venv_name=".venv$version"
    echo -n "Uninstalling $venv_name..."
    deactivate 2> /dev/null # deactivate any active environment
    rm -rf "$venv_name"
    echo -e "${GREEN}DONE${NO_COLOR}"
}

install_virtualenv(){
    version="$1"
    venv_name=".venv$version"

    # For regular python: the binary has a dot between the first and second char of the version string
    python_binary="/usr/bin/python${version:0:1}.${version:1:1}"

    # For pypy: custom path + fetch from the web if not installed (=distro agnostic)
    if [[ $version == *"pypy"* ]]; then
        python_binary="/opt/pypy2-v5.6.0-linux64/bin/pypy"
        # download
        if [ ! -f $python_binary ]; then
            assert_root "Must be root to install pypy, use sudo"
            title "### DOWNLOADING PYPY ($pypy_archive) ###"
            pushd "/opt"
            pypy_archive="pypy2-v5.6.0-linux64.tar.bz2"
            wget "https://bitbucket.org/pypy/pypy/downloads/$pypy_archive"
            title "### EXTRACTING PYPY TARBALL ($pypy_archive) ###"
            tar xvf $pypy_archive
            popd
        fi
    fi

    title "### INSTALLING $venv_name ($python_binary) ###"
    deactivate 2> /dev/null # deactivate any active environment
    virtualenv -p "$python_binary" "$venv_name"
    source "${venv_name}/bin/activate"
    # easy_install -U pip # Commenting out for now, since this gives issues with python 2.6
    pip install --ignore-requires-python -r requirements.txt
    pip install --ignore-requires-python -r test-requirements.txt
    deactivate  2> /dev/null
}

assert_specific_env(){
    if [ -z "$1" ] || [ "$1" == "default" ]; then
        fatal "ERROR: Please specify one or more valid python environments using --envs: 26,27,33,34,35,pypy2"
        exit 1
    fi
}

switch_env(){
    if [ "$1" != "default" ]; then
        deactivate 2> /dev/null # deactivate any active environment
        set -e # Let's error out if you try executing against a non-existing env
        source "/vagrant/.venv${1}/bin/activate"
        set +e
    fi
    title "### PYTHON ($(python --version 2>&1), $(which python)) ###"
}
##############################################################################
# The magic starts here: argument parsing and determining what to do


# default behavior
just_pep8=0
just_lint=0
just_git=0
just_integration_tests=0
just_build_tests=0
just_stats=0
just_all=0
just_clean=0
just_install=0
just_uninstall=0
just_exec=0
include_coverage=1
envs="default"
cmd=""
testargs=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) shift; help;;
        -c|--clean) shift; just_clean=1;;
        -p|--pep8) shift; just_pep8=1;;
        -l|--lint) shift; just_lint=1;;
        -g|--git) shift; just_git=1;;
        -b|--build) shift; just_build_tests=1;;
        -s|--stats) shift; just_stats=1;;
        -i|--integration) shift; just_integration_tests=1;;
        -a|--all) shift; just_all=1;;
        -e|--envs) shift; envs="$1"; shift;;
        --exec) shift; just_exec=1; cmd="$1"; shift;;
        --install) shift; just_install=1;;
        --uninstall) shift; just_uninstall=1;;
        --all-env) shift; envs="all";;
        --no-coverage)shift; include_coverage=0;;
        *) testargs="$1"; shift;
   esac
done

old_virtualenv="$VIRTUAL_ENV" # Store the current virtualenv so we can restore it at the end

trap exit_script INT # Exit on interrupt (i.e. ^C)
exit_script(){
    echo -e -n $NO_COLOR # make sure we don't have color left on the terminal
    exit
}

exit_code=0

# If the users specified 'all', then just replace $envs with the list of all envs
if [ "$envs" == "all" ]; then
    envs="26,27,33,34,35,36,pypy2"
fi
envs=$(echo "$envs" | tr ',' '\n') # Split the env list on comma so we can loop through it


for environment in $envs; do

    if [ $just_pep8 -eq 1 ]; then
        switch_env "$environment"
        run_pep8_check
    elif [ $just_stats -eq 1 ]; then
        switch_env "$environment"
        run_stats
    elif [ $just_integration_tests -eq 1 ]; then
        switch_env "$environment"
        run_integration_tests
    elif [ $just_build_tests -eq 1 ]; then
        switch_env "$environment"
        run_build_test
    elif [ $just_git -eq 1 ]; then
        switch_env "$environment"
        run_git_check
    elif [ $just_lint -eq 1 ]; then
        switch_env "$environment"
        run_lint_check
    elif [ $just_all -eq 1 ]; then
        switch_env "$environment"
        run_all
    elif [ $just_clean -eq 1 ]; then
        switch_env "$environment"
        clean
    elif [ $just_exec -eq 1 ]; then
        switch_env "$environment"
        eval "$cmd"
    elif [ $just_uninstall -eq 1 ]; then
        assert_specific_env "$environment"
        uninstall_virtualenv "$environment"
    elif [ $just_install -eq 1 ]; then
        assert_specific_env "$environment"
        install_virtualenv "$environment"
    else
        switch_env "$environment"
        run_unit_tests
    fi
    # We add up all the exit codes and use that as our final exit code
    # While we lose the meaning of the exit code per individual environment by doing this, we do ensure that the end
    # exit code reflects success (=0) or failure (>0).
    exit_code=$((exit_code + $?))
done

# reactivate the virtualenv if we had one before
if [ ! -z "$old_virtualenv" ]; then
    source "$old_virtualenv/bin/activate"
fi

# Report some overall status
if [ $exit_code -eq 0 ]; then
    echo -e "\n${GREEN}### OVERALL STATUS: SUCCESS ###${NO_COLOR}"
else
    echo -e "\n${RED}### OVERALL STATUS: FAILURE ###${NO_COLOR}"
fi

exit $exit_code
