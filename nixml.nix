
with (import (builtins.fetchTarball {
  name = "nixml-stable-20.09";
  url = https://github.com/nixos/nixpkgs/archive/0d60b0b10eae7a29abb1cbcd47a764c752b39bd9.tar.gz;
  sha256 = "067aj1j2zp919gqj8cq749x9byxclb732dxkh1z65bddkca76nnm";
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
