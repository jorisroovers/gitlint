#!/bin/bash


help(){
    echo "Usage: $0 [OPTION]..."
    echo "Run gitlint's test suite(s) or some convience commands"
    echo "  -h, --help               Show this help output"
    echo "  -c, --clean              Clean the project of temporary files"
    echo "  -f, --format             Run format checks"
    echo "  -l, --lint               Run pylint checks"
    echo "  -g, --git                Run gitlint checks"
    echo "  -i, --integration        Run integration tests"
    echo "  -b, --build              Run build tests"
    echo "  -a, --all                Run all tests and checks (unit, integration, formatting, git)"
    echo "  -e, --envs [ENV1],[ENV2] Run tests against specified python environments"
    echo "                           (envs: 36,37,38,39,pypy37)."
    echo "                           Also works for integration, formatting and lint tests."
    echo "  -C, --container          Run the specified command in the container for the --envs specified"
    echo "  --all-env                Run all tests against all python environments"
    echo "  --install                Install virtualenvs for the --envs specified"
    echo "  --uninstall              Remove virtualenvs for the --envs specified"
    echo "  --install-container      Build and run Docker container for the --envs specified"
    echo "  --uninstall-container    Kill Docker container for the --envs specified"
    echo "  --exec [CMD]             Execute [CMD] in the --envs specified"
    echo "  -s, --stats              Show some project stats"
    echo "  --no-coverage            Don't make a unit test coverage report"
    echo ""
    exit 0
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

subtitle(){
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

# Utility method that prints SUCCESS if a test was successful, or FAIL together with the test output
handle_test_result(){
    EXIT_CODE=$1
    RESULT="$2"
    # Change color to red or green depending on SUCCESS
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}SUCCESS"
    else
        echo -e "${RED}FAIL"
    fi
    # Print RESULT if not empty
    if [ -n "$RESULT" ] ; then
        echo -e "\n$RESULT"
    fi
    # Reset color
    echo -e "${NO_COLOR}"
}

run_formatting_check(){
    # BLACK
    target=${testargs:-"."}
    echo -ne "Running black --check..."
    RESULT=$(black --check --diff $target)
    local exit_code=$?
    handle_test_result $exit_code "$RESULT"
    return $exit_code
}

run_unit_tests(){
    clean
    # py.test -s  => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    target=${testargs:-"gitlint-core"}
    coverage run -m pytest -rw -s $target
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

    echo ""
    gitlint --version
    echo -e "Using $(which gitlint)\n"

    # py.test -s => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    target=${testargs:-"qa/"}
    py.test -s $target
}

run_git_check(){
    echo -ne "Running gitlint...${RED}"
    RESULT=$(gitlint $testargs 2>&1)
    local exit_code=$?
    handle_test_result $exit_code "$RESULT"
    # FUTURE: check if we use str() function: egrep -nriI "( |\(|\[)+str\(" gitlint | egrep -v "\w*#(.*)"
    return $exit_code
}

run_lint_check(){
    echo -ne "Running pylint...${RED}"
    target=${testargs:-"gitlint-core/gitlint qa"}
    RESULT=$(pylint $target --rcfile=".pylintrc" -r n)
    local exit_code=$?
    handle_test_result $exit_code "$RESULT"
    return $exit_code
}

run_build_test(){
    clean
    datestr=$(date +"%Y-%m-%d-%H-%M-%S")
    temp_dir="/tmp/gitlint-build-test-$datestr"

    # Copy gitlint to a new temp dir
    echo -n "Copying gitlint to $temp_dir..."
    mkdir "$temp_dir"
    rsync -az --exclude ".vagrant" --exclude ".git" --exclude ".venv*" . "$temp_dir"
    echo -e "${GREEN}DONE${NO_COLOR}"

    # Update the version to include a timestamp
    echo -n "Writing new version to file..."
    version_file="$temp_dir/gitlint-core/gitlint/__init__.py"
    version_str="$(cat $version_file)"
    version_str="${version_str:0:${#version_str}-1}-$datestr\""
    echo "$version_str" > $version_file
    echo -e "${GREEN}DONE${NO_COLOR}"
    # Attempt to build the package
    echo "Building package ..."
    pushd "$temp_dir/gitlint-core"
    # Copy stdout file descriptor so we can both print output to stdout as well as capture it in a variable
    # https://stackoverflow.com/questions/12451278/bash-capture-stdout-to-a-variable-but-still-display-it-in-the-console
    exec 5>&1
    output=$(python setup.py sdist bdist_wheel | tee /dev/fd/5)
    local exit_code=$?
    popd
    # Cleanup :-)
    rm -rf "$temp_dir"

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
    radon raw -s gitlint | tail -n 11
    echo "*** Docs ***"
    echo "    Markdown: $(cat docs/*.md | wc -l | tr -d " ") lines"
    echo "*** Tests ***"
    nr_unit_tests=$(py.test gitlint-core/ --collect-only | grep TestCaseFunction | wc -l)
    nr_integration_tests=$(py.test qa/ --collect-only | grep TestCaseFunction | wc -l)
    echo "    Unit Tests: ${nr_unit_tests//[[:space:]]/}"
    echo "    Integration Tests: ${nr_integration_tests//[[:space:]]/}"
    echo "*** Git ***"
    echo "    Commits: $(git rev-list --all --count)"
    echo "    Commits (main): $(git rev-list main --count)"
    echo "    First commit: $(git log --pretty="%aD" $(git rev-list --max-parents=0 HEAD))"
    echo "    Contributors: $(git log --format='%aN' | sort -u | wc -l | tr -d ' ')"
    echo "    Releases (tags): $(git tag --list | wc -l | tr -d ' ')"
    latest_tag=$(git tag --sort=creatordate | tail -n 1)
    echo "    Latest Release (tag): $latest_tag"
    echo "    Commits since $latest_tag: $(git log --format=oneline HEAD...$latest_tag | wc -l | tr -d ' ')"
    echo "    Line changes since $latest_tag: $(git diff --shortstat $latest_tag)"
    # PyPi API: https://pypistats.org/api/
    echo "*** PyPi ***"
    info=$(curl -Ls https://pypi.python.org/pypi/gitlint/json)
    echo "    Current version: $(echo $info | jq -r .info.version)"
    echo "*** PyPi (Downloads) ***"
    overall_stats=$(curl -s https://pypistats.org/api/packages/gitlint/overall)
    recent_stats=$(curl -s https://pypistats.org/api/packages/gitlint/recent)
    echo "    Last 6 Months: $(echo $overall_stats | jq -r '.data[].downloads' | awk '{sum+=$1} END {print sum}')"
    echo "    Last Month: $(echo $recent_stats | jq .data.last_month)"
    echo "    Last Week: $(echo $recent_stats | jq .data.last_week)"
    echo "    Last Day: $(echo $recent_stats | jq .data.last_day)"
}

clean(){
    echo -n "Cleaning the *.pyc, site/, build/, dist/ and all __pycache__ directories..."
    find gitlint-core qa -type d -name "__pycache__" -exec rm -rf {} \; 2> /dev/null
    find gitlint-core qa -iname "*.pyc" -exec rm -rf {} \; 2> /dev/null
    rm -rf "site" "dist" "build" "gitlint-core/dist" "gitlint-core/build"
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
    run_formatting_check
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
        pypy_download_mirror="https://downloads.python.org/pypy"
        if [[ $version == *"pypy36"* ]]; then
            pypy_full_version="pypy3.6-v7.3.2-linux64"
        elif [[ $version == *"pypy37"* ]]; then
            pypy_full_version="pypy3.7-v7.3.2-linux64"
        fi

        python_binary="/opt/$pypy_full_version/bin/pypy"
        pypy_archive="$pypy_full_version.tar.bz2"
        if [ ! -f $python_binary ]; then
            assert_root "Must be root to install $version, use sudo"
            title "### DOWNLOADING $version ($pypy_archive) ###"
            pushd "/opt"
            wget "$pypy_download_mirror/$pypy_archive"
            title "### EXTRACTING PYPY TARBALL ($pypy_archive) ###"
            tar xvf $pypy_archive
            popd
        fi
    fi

    title "### INSTALLING $venv_name ($python_binary) ###"
    deactivate 2> /dev/null # deactivate any active environment
    virtualenv -p "$python_binary" "$venv_name"
    source "${venv_name}/bin/activate"
    pip install --ignore-requires-python -r requirements.txt
    pip install --ignore-requires-python -r test-requirements.txt
    deactivate  2> /dev/null
}

container_name(){
    echo "jorisroovers/gitlint:dev-python-$1"
}

start_container(){
    container_name="$1"
    echo -n "Starting container $1..."
    container_details=$(docker container inspect $container_name 2>&1 > /dev/null)
    local exit_code=$?
    if [ $exit_code -gt 0 ]; then
        docker run -t -d -v $(pwd):/gitlint --name $container_name $container_name
        exit_code=$?
        echo -e "${GREEN}DONE${NO_COLOR}"
    else
        echo -e "${YELLOW}SKIP (ALREADY RUNNING)${NO_COLOR}"
        exit_code=0
    fi
    return $exit_code
}

stop_container(){
    container_name="$1"
    echo -n "Stopping container $container_name..."
    result=$(docker kill $container_name 2> /dev/null)
    local exit_code=$?
    if [ $exit_code -gt 0 ]; then
        echo -e "${YELLOW}SKIP (DOES NOT EXIST)${NO_COLOR}"
        exit_code=0
    else
        echo -e "${GREEN}DONE${NO_COLOR}"
    fi
    return $exit_code
}

install_container(){
    local exit_code=0
    python_version="$1"
    python_version_dotted="${python_version:0:1}.${python_version:1:1}"
    container_name="$(container_name $python_version)"

    title "Installing container $container_name"
    image_details=$(docker image inspect $container_name 2> /dev/null)
    tmp_exit_code=$?
    if [ $tmp_exit_code -gt 0 ]; then
        subtitle "Building container image from python:${python_version_dotted}-stretch..."
        docker build -f Dockerfile.dev --build-arg python_version_dotted="$python_version_dotted" -t $container_name .
        exit_code=$?
    else
        subtitle "Building container image from python:${python_version_dotted}-stretch...SKIP (ALREADY-EXISTS)"
        echo "  Use '$0 --uninstall-container; $0 --install-container'  to rebuild"
        exit_code=0
    fi
    return $exit_code
}

uninstall_container(){
    python_version="$1"
    container_name="$(container_name $python_version)"

    echo -n "Removing container image $container_name..."
    image_details=$(docker image inspect $container_name 2> /dev/null)
    tmp_exit_code=$?
    if [ $tmp_exit_code -gt 0 ]; then
        echo -e "${YELLOW}SKIP (DOES NOT EXIST)${NO_COLOR}"
        exit_code=0
    else
        result=$(docker image rm -f $container_name 2> /dev/null)
        exit_code=$?
    fi
    return $exit_code
}

assert_specific_env(){
    if [ -z "$1" ] || [ "$1" == "default" ]; then
        fatal "ERROR: Please specify one or more valid python environments using --envs: 36,37,38,39,pypy37"
        exit 1
    fi
}

switch_env(){
    if [ "$1" != "default" ]; then
        # If we activated a virtualenv within this script, deactivate it
        deactivate 2> /dev/null # deactivate any active environment

        # If this script was run from within an existing virtualenv, manually remove the current VIRTUAL_ENV from the
        # current path. This ensures that our PATH is clean of that virtualenv.
        # Note that the 'deactivate' function from the virtualenv is not available here unless the script was invoked
        # as 'source ./run_tests.sh').
        # Thanks internet stranger! https://unix.stackexchange.com/a/496050/38465
        if [ ! -z "$VIRTUAL_ENV" ]; then
            export PATH=$(echo $PATH | tr ":" "\n" | grep -v "$VIRTUAL_ENV" | tr "\n" ":");
        fi
        set -e # Let's error out if you try executing against a non-existing env
        source "/vagrant/.venv${1}/bin/activate"
        set +e
    fi
    title "### PYTHON ($(python --version 2>&1), $(which python)) ###"
}

run_in_container(){
    python_version="$1"
    envs="$2"
    args="$3"
    container_name="$(container_name $python_version)"
    container_command=$(echo "$0 $args" | sed -E "s/( -e | --envs )$envs//" | sed -E "s/( --container| -C)//")

    title "### CONTAINER $container_name"
    start_container "$container_name"
    docker exec "$container_name" $container_command
}
##############################################################################
# The magic starts here: argument parsing and determining what to do


# default behavior
just_formatting=0
just_lint=0
just_git=0
just_integration_tests=0
just_build_tests=0
just_stats=0
just_all=0
just_clean=0
just_install=0
just_uninstall=0
just_install_container=0
just_uninstall_container=0
just_exec=0
container_enabled=0
include_coverage=1
envs="default"
cmd=""
testargs=""
original_args="$@"
while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) shift; help;;
        -c|--clean) shift; just_clean=1;;
        -f|--format) shift; just_formatting=1;;
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
        --install-container) shift; just_install_container=1;;
        --uninstall-container) shift; just_uninstall_container=1;;
        --all-env) shift; envs="all";;
        -C|--container) shift; container_enabled=1;;
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
    envs="36,37,38,39,pypy37"
fi
original_envs="$envs"
envs=$(echo "$envs" | tr ',' '\n') # Split the env list on comma so we can loop through it

for environment in $envs; do

    if [ $container_enabled -eq 1 ]; then
        run_in_container "$environment" "$original_envs" "$original_args"
    elif [ $just_formatting -eq 1 ]; then
        switch_env "$environment"
        run_formatting_check
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
    elif [ $just_install_container -eq 1 ]; then
        assert_specific_env "$environment"
        install_container "$environment"
    elif [ $just_uninstall_container -eq 1 ]; then
        assert_specific_env "$environment"
        uninstall_container "$environment"
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
