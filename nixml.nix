
with (import (builtins.fetchTarball {
  name = "nixml-stable-22.05";
  url = https://github.com/nixos/nixpkgs/archive/5c0c0f0ee8d7b536925580e723a5f03bf6e0b7a4.tar.gz;
  sha256 = "0v1fbc261by0dfdwysr906garc081swwlyy5x3d7daf98gr5k7yx";
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
