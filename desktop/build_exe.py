"""
Build MusaMotoRacer.exe - a single-file Windows app that runs the game offline.

    python -m venv buildenv
    buildenv\\Scripts\\pip install pyinstaller pywebview
    buildenv\\Scripts\\python desktop\\build_exe.py

The exe lands in dist/MusaMotoRacer.exe and needs nothing installed to run,
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
        "--name", "MusaMotoRacer",
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

    exe = os.path.join(DIST, "MusaMotoRacer.exe")
    sign(exe)
    print("\nbuilt: %s  (%.1f MB)" % (exe, os.path.getsize(exe) / 1048576.0))


def sign(exe):
    """Authenticode-sign the exe if a certificate is configured.

    Unsigned, Windows SmartScreen warns on first run. Set these to sign:

        set MOTORACER_CERT=C:\\path\\to\\cert.pfx
        set MOTORACER_CERT_PW=...

    Needs signtool.exe from the Windows SDK on PATH. Skipped silently when no
    certificate is configured, so an unsigned build still succeeds.
    """
    cert = os.environ.get("MOTORACER_CERT")
    if not cert:
        print("\n(unsigned - set MOTORACER_CERT to sign; SmartScreen will warn on "
              "first run without it)")
        return
    if not os.path.exists(cert):
        print("\nWARNING: MOTORACER_CERT points at a missing file: " + cert)
        return
    signtool = shutil.which("signtool") or shutil.which("signtool.exe")
    if not signtool:
        print("\nWARNING: signtool.exe not on PATH (install the Windows SDK); "
              "leaving the exe unsigned")
        return
    cmd = [signtool, "sign", "/fd", "SHA256",
           "/tr", "http://timestamp.digicert.com", "/td", "SHA256", "/f", cert]
    pw = os.environ.get("MOTORACER_CERT_PW")
    if pw:
        cmd += ["/p", pw]
    cmd.append(exe)
    print("\n$ signtool sign ... " + os.path.basename(exe))
    if subprocess.run(cmd).returncode == 0:
        print("signed OK")
    else:
        print("WARNING: signing failed; the exe is still usable but unsigned")


if __name__ == "__main__":
    main()
