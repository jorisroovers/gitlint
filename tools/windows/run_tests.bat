@echo off

set arg1=%1

IF "%arg1%"=="-p" (
    echo Running flake8...
    flake8 --extend-ignore=H307,H405,H803,H904,H802,H701 --max-line-length=120 --exclude="*settings.py,*.venv/*.py" gitlint qa examples
) ELSE (
    :: Run passed arg, or all unit tests if passed arg is empty
    IF "%arg1%" == "" (
        pytest -rw -s gitlint
    ) ELSE (
        pytest -rw -s %arg1%
    )
)