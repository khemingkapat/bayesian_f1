{
  description = "F1 Bayesian Network Project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux"; # Change to aarch64-darwin if you are on a Mac
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          uv
          python311
        ];

        shellHook = ''
          echo "🏁 F1 Bayesian Network Environment"
          echo "Run 'uv sync' to install dependencies"
          echo "Run 'uv run jupyter lab' to start"
        '';
      };
    };
}
