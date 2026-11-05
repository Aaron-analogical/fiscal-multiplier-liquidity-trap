# Setup

Tested on Windows 11. Other platforms need the same tools but different paths.

| Tool | Version | Notes |
|---|---|---|
| Dynare | 7.2 | `winget install Dynare.Dynare`, installs to `C:\dynare\7.2` |
| GNU Octave | 11.3.0 | Portable zip from <https://ftp.gnu.org/gnu/octave/windows/>, or `winget install GNU.Octave` |
| Python | 3.13 | Packages pinned in `requirements.txt` |
| Node.js | 20 or later | Runs the interactive page tests |

The thesis used Dynare 5.4 with MATLAB. This repo uses free tools instead.

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

If your tools are elsewhere, set `OCTAVE_CLI` to the path of `octave-cli.exe` and `DYNARE_MATLAB` to Dynare's `matlab` folder.

Run everything:

```sh
.venv/Scripts/python scripts/run_all.py
```

## Building the English thesis

The PDF is committed, so this step is optional. It needs a LaTeX engine. [Tectonic](https://tectonic-typesetting.github.io/) 0.17 is standalone and was used here:

```sh
cd paper
tectonic thesis_en.tex
tectonic thesis_fr_corrected.tex
```
