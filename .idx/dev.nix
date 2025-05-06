# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python312                            # CPython 3.12 interpreter :contentReference[oaicite:0]{index=0}
    pkgs.python312Packages.pip                # pip for Python 3.12 :contentReference[oaicite:1]{index=1}
    pkgs.docker                                # Docker CLI & daemon support :contentReference[oaicite:0]{index=0}
    pkgs.docker-compose                        # Docker Compose plugin :contentReference[oaicite:1]{index=1}
  ];
  services.docker.enable = true;
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [ "ms-python.python" ];
    workspace = {
      # Runs when a workspace is first created with this `dev.nix` file
      onCreate = {
        install =
          "python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt";
        # Open editors for the following files by default, if they exist:
        # default.openFiles = [ "README.md" "src/index.html" "main.py" ];
      }; # To run something each time the workspace is (re)started, use the `onStart` hook
    };
    # Enable previews and customize configuration
    previews = {
      
    };
  };
}
