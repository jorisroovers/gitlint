#!/bin/bash -e


help(){
    echo "Usage: $0 [OPTION]..."
    echo "Run pymarkdownlint's test suite(s) or some convience commands"
    echo "  -h, --help         Show this help output"
    echo "  -p, --pep8         Run pep8 checks"
    echo "  -l, --lint         Run pylint checks"
    echo "  -s, --stats        Show some project stats"
    echo "  --no-coverage      Don't make a unit test coverage report"
    echo ""
    exit 0;
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
    flake8 --ignore=$FLAKE8_IGNORE --max-line-length=120 --exclude=$FLAKE8_EXCLUDE pymarkdownlint
}

run_unit_tests(){
    OMIT=".venv/*"
    coverage run --omit=$OMIT -m unittest discover -v
    if [ $include_coverage -eq 1 ]; then
        COVERAGE_REPORT=$(coverage report -m)
        echo "$COVERAGE_REPORT"
    fi
}

run_stats(){
    echo "*** Code ***"
    radon raw -s pymarkdownlint | tail -n 6
}

# default behavior
just_pep8=0
just_lint=0
just_stats=0
include_coverage=1

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) shift; help;;
        -p|--pep8) shift; just_pep8=1;;
        -l|--lint) shift; just_lint=1;;
        -s|--stats) shift; just_stats=1;;
        --no-coverage)shift; include_coverage=0;;
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

run_unit_tests || exit
