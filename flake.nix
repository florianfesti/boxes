{
  description = "Dev shell for Boxes.py (florianfesti/boxes)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f:
        nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in {
      devShells = forAllSystems (pkgs:
        let
          python = pkgs.python3.withPackages (ps: with ps; [
            # runtime deps from requirements.txt
            affine
            lxml
            markdown
            numpy
            pillow
            pyyaml
            qrcode
            rectpack
            setuptools
            shapely
            svgpathtools
            typing-extensions

            # docs
            sphinx

            # dev / tests
            pytest
          ]);
        in {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.git
              # optional: needed for thumbnail generation
              pkgs.imagemagick
              # optional: needed for pre-commit hook
              pkgs.pre-commit
              # optional: needed only for non-SVG output (dxf, plt/hpgl, gcode, ps->pdf)
              pkgs.pstoedit
              pkgs.ghostscript
            ];

            shellHook = ''
              # Run from the repo root so ./boxes is importable and ./scripts is on PATH.
              repo_root=$(${pkgs.git}/bin/git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
              export PYTHONPATH="$repo_root''${PYTHONPATH:+:$PYTHONPATH}"
              export PATH="$repo_root/scripts:$PATH"

              echo "Boxes.py dev shell ($(python --version))"
              echo "  boxes --list                 # list generators"
              echo "  boxes TrayLayout --help      # options for one generator"
              echo "  boxesserver                  # local web UI on :8000"
              echo "  pre-commit run --all-files   # run checks before opening a PR"
            '';
          };
        });
    };
}
