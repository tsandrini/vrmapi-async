# --- flake-parts/shells/dev.nix
{
  lib,
  mkShell,
  nil,
  statix,
  deadnix,
  nix-output-monitor,
  nixfmt-rfc-style,
  writeShellScriptBin,
  nix-fast-build,
  treefmt-wrapper ? null,
  dev-process ? null,
  pre-commit ? null,
  uv,
  gh,
  commitizen,
  cz-cli,
}:
let
  scripts = {
    rename-project = writeShellScriptBin "rename-project" ''
      find $1 \( -type d -name .git -prune \) -o -type f -print0 | xargs -0 sed -i "s/vrmapi-async/$2/g"
    '';
  };

  env = {
    # MY_ENV_VAR = "Hello, World!";
    # MY_OTHER_ENV_VAR = "Goodbye, World!";
  };
in
mkShell {

  packages =
    (lib.attrValues scripts)
    ++ (lib.optional (treefmt-wrapper != null) treefmt-wrapper)
    ++ (lib.optional (dev-process != null) dev-process)
    ++ [
      # -- NIX UTILS --
      nil # Yet another language server for Nix
      statix # Lints and suggestions for the nix programming language
      deadnix # Find and remove unused code in .nix source files
      nix-output-monitor # Processes output of Nix commands to show helpful and pretty information
      nixfmt-rfc-style # An opinionated formatter for Nix
      nix-fast-build # A tool to speed up Nix builds by caching build results

      # -- GIT RELATED UTILS --
      commitizen # Tool to create committing rules for projects, auto bump versions, and generate changelogs
      cz-cli # The commitizen command line utility
      # fh # The official FlakeHub CLI
      gh # GitHub CLI tool
      # gh-dash # Github Cli extension to display a dashboard with pull requests and issues

      # -- BASE LANG UTILS --
      # markdownlint-cli # Command line interface for MarkdownLint
      # nodePackages.prettier # Prettier is an opinionated code formatter
      # typos # Source code spell checker

      # -- (YOUR) EXTRA PKGS --
      uv # Extremely fast Python package installer and resolver, written in Rust
    ];

  shellHook = ''
    ${lib.concatLines (lib.mapAttrsToList (name: value: "export ${name}=${value}") env)}
    ${lib.optionalString (pre-commit != null) pre-commit.installationScript}

    echo "Entering Python + uv environment..."
    export VIRTUAL_ENV=$(pwd)/.venv
    export PATH="$VIRTUAL_ENV/bin:$PATH"

    if [ ! -d "$VIRTUAL_ENV" ]; then
      echo "Creating virtual environment with uv..."
      uv venv
    fi

    echo "Syncing dependencies with uv..."
    uv sync --all-extras

    echo "Virtual environment ready and synced at $VIRTUAL_ENV"

    # Welcome splash text
    echo ""; echo -e "\e[1;37;42mWelcome to the vrmapi-async devshell!\e[0m"; echo ""
  '';
}
