{
  description = "Reproducible environment for vita (CV) and citations.py";

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

      texFor = system:
        let pkgs = pkgsFor system;
        in pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-tetex
            collection-fontsextra
            collection-fontsrecommended
            xetex
            polyglossia
            euenc
            xunicode
            enumitem
            wrapfig;
        };

      localFonts = system:
        let pkgs = pkgsFor system;
        in pkgs.runCommand "vita-fonts" {} ''
          mkdir -p $out/share/fonts/truetype
          cp ${./fonts}/*.ttf $out/share/fonts/truetype/
        '';
    in {
      packages = forAllSystems (system:
        let
          pkgs = pkgsFor system;
          tex = texFor system;
          allFonts = [ pkgs.libertine pkgs.gentium-book-basic (localFonts system) "${tex}/share/texmf/fonts" ];
          fontsConf = pkgs.makeFontsConf { fontDirectories = allFonts; };
        in {
          default = pkgs.stdenvNoCC.mkDerivation {
            name = "vita";
            src = self;
            nativeBuildInputs = [ (pythonFor system) tex ] ++ allFonts;
            buildPhase = ''
              export MPLBACKEND=Agg
              export HOME=$TMPDIR
              export FONTCONFIG_FILE=${fontsConf}
              python citations.py
              xelatex vita.tex
              xelatex vita.tex
            '';
            installPhase = ''
              mkdir -p $out
              cp vita.pdf citations-h-index.pdf $out/
            '';
          };
        });

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

      devShells = forAllSystems (system:
        let pkgs = pkgsFor system; in {
          default = pkgs.mkShell {
            packages = [ (pythonFor system) (texFor system) pkgs.libertine pkgs.gentium-book-basic (localFonts system) ];
          };
          python = pkgs.mkShell {
            packages = [ (pythonFor system) ];
          };
          tex = pkgs.mkShell {
            packages = [ (texFor system) pkgs.libertine pkgs.gentium-book-basic (localFonts system) ];
          };
        });
    };
}
