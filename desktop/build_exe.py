"""
Build MotoRacer.exe - a single-file Windows app that runs the game offline.

    python -m venv buildenv
    buildenv\\Scripts\\pip install pyinstaller pywebview
    buildenv\\Scripts\\python desktop\\build_exe.py

The exe lands in dist/MotoRacer.exe and needs nothing installed to run,
other than the Microsoft Edge WebView2 runtime, which ships with Windows 11
and current Windows 10.
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
DIST = os.path.join(ROOT, "dist")

# Everything the page needs at runtime, copied in as a "game" folder.
ASSETS = ["index.html", "manifest.json", "sw.js", "icon.svg", "icons", "vendor"]


def make_icon():
    """Windows wants a multi-resolution .ico for a crisp taskbar icon."""
    from PIL import Image
    src = os.path.join(ROOT, "icons", "icon-512.png")
    out = os.path.join(BUILD, "motoracer.ico")
    os.makedirs(BUILD, exist_ok=True)
    img = Image.open(src).convert("RGBA")
    img.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                         (128, 128), (256, 256)])
    print("icon:", out)
    return out


def stage_assets():
    """Collect the web assets under build/game so --add-data has one root."""
    stage = os.path.join(BUILD, "game")
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)
    for name in ASSETS:
        src = os.path.join(ROOT, name)
        if not os.path.exists(src):
            raise SystemExit("missing asset: " + src)
        dst = os.path.join(stage, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    total = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fs in os.walk(stage) for f in fs
    )
    print("staged %d assets, %.1f KB" % (len(ASSETS), total / 1024.0))
    return stage


def main():
    icon = make_icon()
    stage = stage_assets()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile",
        "--noconsole",
        "--name", "MotoRacer",
        "--icon", icon,
        "--distpath", DIST,
        "--workpath", os.path.join(BUILD, "pyi"),
        "--specpath", BUILD,
        "--add-data", stage + os.pathsep + "game",
        # keep the binary lean: none of these are used
        "--exclude-module", "numpy",
        "--exclude-module", "PIL",
        "--exclude-module", "pytest",
        "--exclude-module", "unittest",
        os.path.join(HERE, "moto_racer.py"),
    ]
    print("\n$ " + " ".join(cmd) + "\n")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(r.returncode)

    exe = os.path.join(DIST, "MotoRacer.exe")
    print("\nbuilt: %s  (%.1f MB)" % (exe, os.path.getsize(exe) / 1048576.0))


if __name__ == "__main__":
    main()
