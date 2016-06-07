with (import <nixpkgs>) {};
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
        xetex-def
        enumitem
        wrapfig;
  };
in
stdenv.mkDerivation {
  name = "vitatex";
  propagatedBuildInputs = [ tex libertine ];
}
