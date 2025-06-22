# --- flake-parts/pkgs/default.nix
_: {
  perSystem = _: {
    packages = {
      # NOTE For more info on the nix `callPackage` pattern see
      # https://nixos.org/guides/nix-pills/13-callpackage-design-pattern.html

      # my-custom-package = pkgs.callPackage ./my-custom-package.nix { };
    };
  };
}
