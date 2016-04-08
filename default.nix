{ pkgs ? import <nixpkgs> {} }:
let
  stdenv = pkgs.stdenv;
  pythonpkgs = pkgs.python27Packages;
in {
  spotd = pythonpkgs.buildPythonPackage {
    name = "spotd";
    version = "0.0.1";
    src = ./.;

    buildInputs = with pythonpkgs; [
      httpretty
      flake8
    ];

    postCheck = ''
    flake8 --exclude nix_run_setup.py .
    '';
  };
}
