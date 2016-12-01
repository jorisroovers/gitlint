#!/bin/bash -e

help(){
    echo "Usage: $0 [OPTION]..."
    echo "Run gitlint's test suite(s) or some convience commands"
    echo "  -h, --help              Show this help output"
    echo "  -c, --clean             Clean the project of temporary files"
    echo "  -p, --pep8              Run pep8 checks"
    echo "  -l, --lint              Run pylint checks"
    echo "  -g, --git               Run gitlint checks"
    echo "  -i, --integration       Run integration tests"
    echo "  -a, --all               Run all tests and checks (unit, integration, pep8, git)"
    echo "  --all-env               Run all tests against all python environments"
    echo "  --install-virtualenvs   Install virtualenvs for python 2.6, 2.7, 3.3, 3.4, 3.5"
    echo "  --remove-virtualenvs    Remove virtualenvs for python 2.6, 2.7, 3.3, 3.4, 3.5"
    echo "  -s, --stats             Show some project stats"
    echo "  --no-coverage           Don't make a unit test coverage report"
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
    echo "Running flake8..."
    flake8 --ignore=$FLAKE8_IGNORE --max-line-length=120 --exclude=$FLAKE8_EXCLUDE gitlint qa examples
}

run_unit_tests(){
    clean
    # py.test -s  => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    if [ -n "$testargs" ]; then
        coverage run -m pytest -rw -s "$testargs"
    else
        coverage run -m pytest -rw -s gitlint
    fi
    TEST_RESULT=$?
    if [ $include_coverage -eq 1 ]; then
        COVERAGE_REPORT=$(coverage report -m)
        echo "$COVERAGE_REPORT"
    fi

    if [ $TEST_RESULT  -gt 0 ]; then
        exit $TEST_RESULT;
    fi
}

run_integration_tests(){
    clean
    # py.test -s => print standard output (i.e. show print statement output)
    #         -rw => print warnings
    if [ -n "$testargs" ]; then
        py.test -s "$testargs"
    else
        py.test -s qa/
    fi
}

run_git_check(){
    echo "Running gitlint..."
    gitlint
}

run_lint_check(){
    echo "Running pylint..."
    pylint gitlint qa --rcfile=".pylintrc" -r n
}

run_stats(){
    echo "*** Code ***"
    radon raw -s gitlint | tail -n 6
    echo "*** Tests ***"
    nr_unit_tests=$(py.test gitlint/ --collect-only | grep TestCaseFunction | wc -l)
    nr_integration_tests=$(py.test qa/ --collect-only | grep TestCaseFunction | wc -l)
    echo "    Unit Tests: ${nr_unit_tests//[[:space:]]/}"
    echo "    Integration Tests: ${nr_integration_tests//[[:space:]]/}"
    echo "*** Git ***"
    echo "    Number of commits: $(git rev-list --all --count)"
    echo "    Number of authors: $(git log --format='%aN' | sort -u  | wc -l)"
}

clean(){
    echo -n "Cleaning the site, build, dist and all __pycache__directories..."
    set +e
    find gitlint -type d  -name "__pycache__" -exec rm -rf {} \; 2> /dev/null
    find qa -type d  -name "__pycache__" -exec rm -rf {} \; 2> /dev/null
    rm -rf "site" "dist" "build"
    set -e
    echo -e "${GREEN}DONE${NO_COLOR}"
}

run_all(){
    subtitle "# UNIT TESTS #"
    run_unit_tests
    subtitle "# INTEGRATION TESTS #"
    run_integration_tests
    subtitle "# STYLE CHECKS #"
    run_pep8_check
    run_git_check
}

remove_virtualenvs(){
    echo -n "Removing .venv26 .venv27 .venv33 .venv34 .venv35..."
    set +e
    deactivate 2> /dev/null # deactivate any active environment
    set -e
    rm -rf ".venv26" ".venv27" ".venv33" ".venv34" ".venv35"
    echo -e "${GREEN}DONE${NO_COLOR}"
}

install_virtualenvs(){
    echo "Installing .venv26 .venv27 .venv33 .venv34 .venv35..."

    set +e
    deactivate 2> /dev/null # deactivate any active environment
    set -e

    # Install the virtualenvs for different python versions
    virtualenv -p /usr/bin/python2.6 .venv26
    source .venv26/bin/activate
    easy_install -U pip
    pip install -r requirements.txt
    pip install -r test-requirements.txt
    deactivate

    virtualenv -p /usr/bin/python2.7 .venv27
    source .venv27/bin/activate
    easy_install -U pip
    pip install -r requirements.txt
    pip install -r test-requirements.txt
    deactivate

    virtualenv -p /usr/bin/python3.3 .venv33
    source .venv33/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r test-requirements.txt
    deactivate

    virtualenv -p /usr/bin/python3.4 .venv34
    source .venv34/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r test-requirements.txt
    deactivate

    virtualenv -p /usr/bin/python3.5 .venv35
    source .venv35/bin/activate
    pip3 install -r requirements.txt
    pip3 install -r test-requirements.txt
    deactivate
}

run_tests_in_all_env(){
    # Let's make sure we can recover the current virtualenv after we're done
    old_virtualenv="$VIRTUAL_ENV"
    set +e
    deactivate 2> /dev/null # deactivate any active environment
    set -e

    # Run the tests against all environments in vagrant
    source /vagrant/.venv26/bin/activate
    title "### PYTHON 2.6 ($(python --version 2>&1), /vagrant/.venv26) ###"
    run_all
    deactivate

    source /vagrant/.venv27/bin/activate
    title "### PYTHON 2.7 ($(python --version 2>&1), /vagrant/.venv27) ###"
    run_all
    deactivate

    source /vagrant/.venv33/bin/activate
    title "### PYTHON 3.3 ($(python --version 2>&1), /vagrant/.venv33) ###"
    run_all
    deactivate

    source /vagrant/.venv34/bin/activate
    title "### PYTHON 3.4 ($(python --version 2>&1), /vagrant/.venv34) ###"
    run_all
    deactivate

    source /vagrant/.venv35/bin/activate
    title "### PYTHON 3.5 ($(python --version 2>&1), /vagrant/.venv35) ###"
    run_all
    deactivate

    if [ ! -z "$old_virtualenv" ]; then
        source "$old_virtualenv/bin/activate"
    fi
}

# default behavior
just_pep8=0
just_lint=0
just_git=0
just_integration_tests=0
just_stats=0
just_all_env=0
just_all=0
just_clean=0
just_install_virtualenvs=0
just_remove_virtualenvs=0
include_coverage=1
testargs=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) shift; help;;
        -c|--clean) shift; just_clean=1;;
        -p|--pep8) shift; just_pep8=1;;
        -l|--lint) shift; just_lint=1;;
        -g|--git) shift; just_git=1;;
        -s|--stats) shift; just_stats=1;;
        -i|--integration) shift; just_integration_tests=1;;
        -a|--all) shift; just_all=1;;
        --install-virtualenvs) shift; just_install_virtualenvs=1;;
        --remove-virtualenvs) shift; just_remove_virtualenvs=1;;
        --all-env) shift; just_all_env=1;;
        --no-coverage)shift; include_coverage=0;;
        *) testargs="$1"; shift;
   esac
done

if [ $just_pep8 -eq 1 ]; then
    run_pep8_check
    exit $?
fi

if [ $just_stats -eq 1 ]; then
    run_stats
    exit $?
fi

if [ $just_integration_tests -eq 1 ]; then
    run_integration_tests
    exit $?
fi

if [ $just_git -eq 1 ]; then
    run_git_check
    exit $?
fi

if [ $just_lint -eq 1 ]; then
    run_lint_check
    exit $?
fi

if [ $just_all_env -eq 1 ]; then
    run_tests_in_all_env
    exit $?
fi

if [ $just_all -eq 1 ]; then
    run_all
    exit $?
fi

if [ $just_clean -eq 1 ]; then
    clean
    exit $?
fi

if [ $just_remove_virtualenvs -eq 1 ]; then
    remove_virtualenvs
    exit $?
fi

if [ $just_install_virtualenvs -eq 1 ]; then
    install_virtualenvs
    exit $?
fi


run_unit_tests || exit
