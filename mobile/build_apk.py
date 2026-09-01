"""
Build a signed release APK of Moto Racer.

    python mobile/build_apk.py

Needs Node, JDK 21 and the Android SDK. Signing uses mobile/keystore, which is
git-ignored: losing that keystore means Android will refuse to install an
update over an existing copy, so keep a backup of it somewhere safe.

Set JAVA_HOME / ANDROID_HOME to override the defaults below.
"""

import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANDROID = os.path.join(HERE, "android")
KEYDIR = os.path.join(HERE, "keystore")
OUT = os.path.join(HERE, "dist")


def find_jdk():
    if os.environ.get("JAVA_HOME"):
        return os.environ["JAVA_HOME"]
    hits = sorted(glob.glob(r"C:\Program Files\Microsoft\jdk-21*"))
    if not hits:
        raise SystemExit("JDK 21 not found - set JAVA_HOME (Capacitor 8 needs 21, not 17)")
    return hits[-1]


def find_sdk():
    for c in (os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT"),
              r"C:\Android", os.path.expanduser(r"~\AppData\Local\Android\Sdk")):
        if c and os.path.isdir(c):
            return c
    raise SystemExit("Android SDK not found - set ANDROID_HOME")


def find_node():
    for c in (r"C:\Program Files\nodejs", ):
        if os.path.isdir(c):
            return c
    return None


def build_tools(sdk):
    versions = sorted(glob.glob(os.path.join(sdk, "build-tools", "*")))
    if not versions:
        raise SystemExit("no build-tools installed in " + sdk)
    return versions[-1]


def read_props(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def run(cmd, cwd=None, env=None):
    print("\n$ " + " ".join(str(c) for c in cmd))
    r = subprocess.run(cmd, cwd=cwd, env=env, shell=False)
    if r.returncode != 0:
        raise SystemExit("failed (%d): %s" % (r.returncode, cmd[0]))


def main():
    jdk, sdk = find_jdk(), find_sdk()
    bt = build_tools(sdk)
    node = find_node()
    print("JDK        :", jdk)
    print("Android SDK:", sdk)
    print("build-tools:", os.path.basename(bt))

    env = dict(os.environ)
    env["JAVA_HOME"] = jdk
    env["ANDROID_HOME"] = sdk
    env["ANDROID_SDK_ROOT"] = sdk
    env["PATH"] = os.path.join(jdk, "bin") + os.pathsep + \
        ((node + os.pathsep) if node else "") + env.get("PATH", "")

    if not os.path.isdir(ANDROID):
        raise SystemExit("android/ missing - run: npx cap add android")

    # Gradle reads the SDK path from here; forward slashes avoid the
    # backslash-escaping rules of .properties files.
    with open(os.path.join(ANDROID, "local.properties"), "w", encoding="utf-8") as f:
        f.write("sdk.dir=" + sdk.replace("\\", "/") + "\n")

    npx = os.path.join(node, "npx.cmd") if node else "npx"
    node_exe = os.path.join(node, "node.exe") if node else "node"
    run([node_exe, os.path.join(HERE, "sync-www.js")], cwd=HERE, env=env)
    run([npx, "cap", "sync", "android"], cwd=HERE, env=env)
    run([os.path.join(ANDROID, "gradlew.bat"), "assembleRelease"], cwd=ANDROID, env=env)

    unsigned = os.path.join(ANDROID, "app", "build", "outputs", "apk", "release",
                            "app-release-unsigned.apk")
    if not os.path.exists(unsigned):
        hits = glob.glob(os.path.join(ANDROID, "app", "build", "outputs", "apk",
                                      "release", "*.apk"))
        if not hits:
            raise SystemExit("gradle produced no release apk")
        unsigned = hits[0]

    os.makedirs(OUT, exist_ok=True)
    aligned = os.path.join(OUT, "MotoRacer-aligned.apk")
    final = os.path.join(OUT, "MotoRacer.apk")

    run([os.path.join(bt, "zipalign.exe"), "-f", "-p", "4", unsigned, aligned], env=env)

    props = read_props(os.path.join(KEYDIR, "keystore.properties"))
    run([os.path.join(bt, "apksigner.bat"), "sign",
         "--ks", os.path.join(KEYDIR, props["storeFile"]),
         "--ks-key-alias", props["keyAlias"],
         "--ks-pass", "pass:" + props["storePassword"],
         "--key-pass", "pass:" + props["keyPassword"],
         "--out", final, aligned], env=env)
    os.remove(aligned)
    if os.path.exists(final + ".idsig"):
        os.remove(final + ".idsig")

    run([os.path.join(bt, "apksigner.bat"), "verify", "--print-certs", final], env=env)
    print("\nbuilt: %s  (%.1f MB)" % (final, os.path.getsize(final) / 1048576.0))


if __name__ == "__main__":
    main()
