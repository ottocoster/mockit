#!/usr/bin/env python3
"""
Build the browser version of Mock'it into web/dist/.

    cd web && npm install && python3 build.py
    python3 -m http.server -d dist 8080   # then open http://localhost:8080

Produces a static site: Pyodide + xterm.js (vendored from node_modules) and
mockit.zip, which holds src/ and the SSH parts of configs/ (handler modules,
scripts and command templates). SNMP walks, MIBs and NETCONF files are left
out because those servers can't run in a browser.
"""
import shutil
import zipfile
from pathlib import Path

WEB = Path(__file__).resolve().parent
ROOT = WEB.parent
DIST = WEB / "dist"
NODE = WEB / "node_modules"

PYODIDE_FILES = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm",
                 "python_stdlib.zip", "pyodide-lock.json"]
XTERM_FILES = {
    "@xterm/xterm/lib/xterm.js": "xterm.js",
    "@xterm/xterm/css/xterm.css": "xterm.css",
    "@xterm/addon-fit/lib/addon-fit.js": "addon-fit.js",
}
SKIP_DIRS = {"__pycache__", "netconf", "api"}


def include_config(path: Path) -> bool:
    rel = path.relative_to(ROOT / "configs")
    if SKIP_DIRS & set(rel.parts):
        return False
    if path.suffix == ".py":
        return True
    # command templates (static command outputs)
    return path.suffix == ".txt" and "templates" in rel.parts


def build_zip(target: Path) -> int:
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted((ROOT / "src").rglob("*.py")):
            if "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(ROOT).as_posix())
                count += 1
        # configs/ has no __init__.py files; add them so the device modules
        # import as regular packages.
        zf.writestr("configs/__init__.py", "")
        for path in sorted((ROOT / "configs").rglob("*")):
            if path.is_file() and include_config(path):
                zf.write(path, path.relative_to(ROOT).as_posix())
                count += 1
    return count


def main():
    if not (NODE / "pyodide").is_dir():
        raise SystemExit("node_modules missing: run `npm install` in web/ first")
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "pyodide").mkdir(parents=True)
    (DIST / "vendor").mkdir()

    for name in PYODIDE_FILES:
        shutil.copy2(NODE / "pyodide" / name, DIST / "pyodide" / name)
    for src, dst in XTERM_FILES.items():
        shutil.copy2(NODE / src, DIST / "vendor" / dst)
    for name in ["index.html", "app.js", "mockit_browser.py"]:
        shutil.copy2(WEB / name, DIST / name)

    files = build_zip(DIST / "mockit.zip")
    size = (DIST / "mockit.zip").stat().st_size / 1024 / 1024
    print(f"Built {DIST} ({files} files in mockit.zip, {size:.1f} MiB)")


if __name__ == "__main__":
    main()
