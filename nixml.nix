
with (import (builtins.fetchTarball {
  name = "nixml-stable-19.03";
  url = https://github.com/nixos/nixpkgs/archive/c42f391c0c87429dafd059c2da2aff66edb00357.tar.gz;
  sha256 = "0yh8wmyws63lc757akgwclvjgl5hk763ci26ndz04dpw6frsrlkq";
}) {});

let
  tex = pkgs.texlive.combine {
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
in

stdenv.mkDerivation {
  name = "pynix-env";
  buildInputs = [
    tex libertine
  ];
}
