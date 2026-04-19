{
  description = "Reproducible environment for citations.py";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      pkgsFor = system: nixpkgs.legacyPackages.${system};
      pythonFor = system:
        let pkgs = pkgsFor system;
        in pkgs.python3.withPackages (ps: [
          ps.numpy
          ps.matplotlib
          ps.pandas
          ps.seaborn
        ]);
    in {
      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = let
            pkgs = pkgsFor system;
            script = pkgs.writeShellScript "run-citations" ''
              export MPLBACKEND=Agg
              exec ${pythonFor system}/bin/python citations.py "$@"
            '';
          in "${script}";
        };
      });

      devShells = forAllSystems (system: {
        default = let pkgs = pkgsFor system; in
          pkgs.mkShell {
            packages = [ (pythonFor system) ];
          };
      });
    };
}
