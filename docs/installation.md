## Fully supported

### Pip (recommended)
```{.sh .copy}
pip install gitlint
```

By default, gitlint is installed with pinned dependencies.
To install gitlint with looser dependency requirements, only install gitlint-core:
```{.sh .copy}
pip install gitlint-core
```

??? info "Installing from GitHub source Git archive URLs"
    ```{.sh .copy}
    # Set version to install
    export GITLINT_VERSION="v0.20.0"

    # Install using pinned dependencies
    pip install "gitlint-core [trusted-deps] @ https://github.com/jorisroovers/gitlint/archive/$GITLINT_VERSION.tar.gz#subdirectory=gitlint-core"
    
    # Install using looser dependencies
    pip install "https://github.com/jorisroovers/gitlint/archive/$GITLINT_VERSION.tar.gz#subdirectory=gitlint-core"
    ```

??? info "Uninstalling gitlint"
    To fully uninstall gitlint, you need to remove both `gitlint` and `gitlint-core`:
    ```{.sh .copy}
    pip uninstall gitlint gitlint-core 
    ```

### Docker
There is a fully maintained and supported [docker image for gitlint](https://hub.docker.com/r/jorisroovers/gitlint).
```{.sh .copy}
docker run --ulimit nofile=1024 -v $(pwd):/repo jorisroovers/gitlint # (1)
```

1. `--ulimit` is required to work around a limitation in Docker.
   Details: see issue [#129](https://github.com/jorisroovers/gitlint/issues/129)

## Community Maintained Packages
These packages are not officially maintained by gitlint. For the latest and fully supported version, always use `pip`.

#### Brew
```{.sh .copy}
brew install gitlint
```
#### MacPorts

```{.sh .copy}
port install gitlint
```

#### Ubuntu
```{.sh .copy}
apt-get install gitlint
```

#### All available packages 
[![Packaging status](https://repology.org/badge/vertical-allrepos/gitlint.svg)](https://repology.org/project/gitlint/versions)

## Shell completion

```sh
# Bash: add to ~/.bashrc
eval "$(_GITLINT_COMPLETE=bash_source gitlint)"

# Zsh: add to ~/.zshrc
eval "$(_GITLINT_COMPLETE=zsh_source gitlint)"

# Fish: add to ~/.config/fish/completions/foo-bar.fish
eval (env _GITLINT_COMPLETE=fish_source gitlint)
```