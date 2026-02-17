{
  description = "Tasman dbt-datadict, Tool for managing consistent column descriptions across a dbt project.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  };

  outputs =
    {
      nixpkgs,
      ...
    }:
    let
      # Systems supported
      allSystems = [
        "x86_64-linux" # 64-bit Intel/AMD Linux
        "aarch64-darwin" # MacOS M chips
      ];

      # Helper to provide system-specific attributes
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs allSystems (
          system:
          f {
            pkgs = import nixpkgs {
              inherit system;
              # NOTE: Uncomment this if using non-foss programs (like terraform)
              # config.allowUnfree = true;
            };
          }
        );

    in
    {
      devShells = forAllSystems (
        { pkgs }:
        {

          default = pkgs.mkShell {
            # There is no variable set by default for a Nix shell, this gives us
            #   something to use to detect if we're in.
            NIX_DEVELOP_SHELL = "true";

            # Tell uv to use the Nix-provided Python, not download its own
            UV_PYTHON_DOWNLOADS = "never";

            # The Nix packages provided in the environment
            packages = (
              with pkgs;
              [
                # Command runners
                just

                # Used by command runners
                curl
                # for `sed`
                gnused
                # For `fgrep`
                gnugrep

                # Standard python stuff
                python313
                uv

                # NOTE: Even though this should be installed by default, some darwin
                #   shells don't seem to detect it.
                #   This also means that re-running `nix develop` while in a shell
                #   causes issues as the system git and shell git conflict, so exit
                #   your dev shell, `exit`, before re-entering.
                # TODO: Figure out why this happens on some Macs but not others, so
                #   that this isn't needed anymore.
                git

                # For formatting nix files, with `nixfmt`
                nixfmt-rfc-style
              ]
            );
            shellHook = ''
              # Github Actions sets the "CI" environment variable to true.
              if [ -z "''${CI:-}" ]; then
                just ensure-uv-and-pre-commit

                # Activate the venv uv created
                if [ -d .venv ]; then
                  source .venv/bin/activate
                fi
              fi
            '';

          };
        }
      );
    };

}
