{
  description = "F1 Bayesian Network Project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          uv
          python311

          # Added system libraries needed by pre-compiled Python wheels (Jupyter, Pandas, etc.)
          stdenv.cc.cc.lib
          zlib
        ];

        # Tell the environment exactly where to find those libraries
        env = {
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
        };

        shellHook = ''
          echo "🏁 F1 Bayesian Network Environment"
          echo "Run 'uv sync' to install dependencies"
          echo "Run 'uv run jupyter lab' to start"
        '';
      };
    };
}
