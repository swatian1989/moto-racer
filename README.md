# Moto Racer — Coastline

A 3D sunset-highway racing game that runs in the browser and **installs like a
native app** on Android, iPhone, Windows, Mac and Linux. Once installed it works
with no internet connection at all.

**Play it:** https://swatian1989.github.io/moto-racer/

## Install it

| Device | How |
| --- | --- |
| **Android** (Chrome / Edge / Samsung) | Open the link, tap **⬇ INSTALL APP** on the title screen. |
| **iPhone / iPad** (Safari) | Open the link, tap **Share**, then **Add to Home Screen**. |
| **Windows / Mac / Linux** (Chrome / Edge) | Open the link, click **⬇ INSTALL APP**, or use the install icon in the address bar. |

After installing, launch it from your home screen, Start menu, Dock or app
drawer. It opens fullscreen with no browser chrome, and **works offline** — the
whole game, including the 3D engine, is stored on the device.

## The ride

Dodge traffic, thread the gaps, and get as far as you can before you wipe out.

- **Near misses build a combo.** Slip past a car in the next lane and the combo
  climbs, multiplying everything you score — up to 2× on its own. Stop
  threading traffic and it decays.
- **Power-ups** drop on the road: 🛡 **Shield** eats one crash,
  🧲 **Magnet** pulls coins to your line, **2× Score** doubles
  everything for ten seconds, and **Slow-Mo** drags the world down to a crawl
  while you keep steering at full speed.
- **Day turns to night** as the run goes on. Stars come out, your headlight
  starts doing real work, and oncoming traffic becomes a pair of lights in the
  dark before it becomes a car. The clock rides over whichever landscape you
  picked, so every world has its own dawn and dusk — except Neon City, which
  is pinned to night because that is the whole point of it.
- **Traffic changes lanes** ahead of you — but only while it is still far
  off, so it never swerves into you unfairly.
- **Weather** rolls between clear, rain and storm, with lightning and a wet,
  reflective road.

## Progression

Coins are earned from pickups, distance covered and near misses, then spent in
the menus on the title screen.

**Garage — six machines**, each a different model rather than a recolour:
different wheels, stance, bodywork, exhausts and rider posture.

| Bike | Type | Cost | Character |
| --- | --- | --- | --- |
| Street 500 | Naked standard | free | Upright, exposed engine, forgiving |
| Neon GT | Sport | 1,200 | Full fairing, clip-ons, twitchy and quick |
| Dune ADV | Adventure | 3,000 | Tall knobbly wheels, wide bars, panniers |
| Roadster 1200 | Cruiser | 4,500 | Long and low, twin pipes, slow to turn |
| Phantom S | Superbike | 6,500 | Winglets, twin cans, extreme tuck |
| Volt Zero | Electric hyper | 10,000 | Sculpted shell, light strips, no gearbox |

**Worlds — four landscapes**, each with its own sky, terrain, props and mood:

| World | Cost | What it is |
| --- | --- | --- |
| Sunset Coastline | free | Golden hour, palms and surf on your right |
| Canyon Run | 1,500 | Red mesas and saguaro on an empty desert highway |
| Alpine Pass | 3,500 | Snowbound pines and granite peaks either side |
| Neon City | 7,000 | Wet asphalt between lit towers — always after dark |

**Upgrades** — three tracks, four levels each: **Engine** (top speed),
**Nitro** (tank size and refill rate) and **Grip** (how fast you change lanes).

**Missions** — three objectives are always active on the title screen. Clear
one for a coin payout and a fresh objective takes its place.

**Achievements** unlock as you hit distance, coin, near-miss and garage
milestones.

## Controls

| | Touch | Keyboard | Gamepad |
| --- | --- | --- | --- |
| Steer | ◀ ▶ buttons, or tilt the phone | `←` `→` / `A` `D` | Left stick or D-pad |
| Throttle | 🔥 GAS | `↑` / `W` | Right trigger or B |
| Nitro | ⚡ NOS | `N` / `Shift` | X, left trigger, bumpers |
| Jump | JUMP | `Space` | A |
| Pause | ⏸ | `P` / `Esc` | Start |
| Fullscreen | ⛶ | `F` | — |
| Mute | 🔊 | `M` | — |
| Quit | EXIT button | `Q` | — |

## Settings

Graphics preset (low / medium / high), tilt steering with an adjustable
sensitivity, volume, vibration, an optional FPS readout, and a progress reset.
The game also drops its own resolution automatically if a device cannot hold
frame rate.

**Moving a save between the app and the website.** They are separate origins,
so they cannot see each other's storage. Settings has a **Save Data** box:
press EXPORT in one, paste the code into the other, press IMPORT.

Your coins, bikes, upgrades, missions, achievements, best distance and the
top-10 leaderboard are all stored on your device.

## Desktop app (Windows .exe)

`MotoRacer.exe` is a single self-contained file. Double-click it and the game
opens in its own window - no browser, no install, no internet.

It works by serving the game from a local web server on a fixed port and
displaying it in a native WebView2 window. That sounds roundabout, but a
service worker (and so offline play) will not run from a `file://` origin, and
the fixed port keeps `localStorage` on a stable origin so your coins, bikes and
unlocked worlds survive between launches. Progress lives in
`%LOCALAPPDATA%\MotoRacer`.

To build it yourself:

```sh
python -m venv buildenv
buildenv\Scripts\pip install pyinstaller pywebview pillow
buildenv\Scripts\python desktop\build_exe.py
# -> dist/MotoRacer.exe
```

Requires the Microsoft Edge WebView2 runtime, which ships with Windows 11 and
current Windows 10. Without it the launcher falls back to opening a Chromium
app window instead.

**EXIT** on the title or pause screen closes the app (two taps, so a stray press cannot end a run). `Q` does the same when you are not mid-corner. In a plain browser tab a page is not allowed to close itself, so it drops out of fullscreen and tells you to close the tab instead.

Useful flags: `--serve-only` runs the server with no window, `--browser` forces
the browser fallback, `--port N` moves the port (which starts a fresh save).

## Android app (APK)

`MotoRacer.apk` is a signed release build that bundles the whole game -
including the 3D engine - inside the package. Nothing is fetched at runtime, so
it works offline from the moment it installs.

To install it, copy the APK to your phone and open it. Android will ask you to
allow installs from that source the first time.

Built with [Capacitor](https://capacitorjs.com). To rebuild:

```sh
cd mobile
npm install
npx cap add android          # regenerates the native project
python make_android_assets.py   # launcher icons + splash from the game art
cd .. && python mobile/build_apk.py
# -> mobile/dist/MotoRacer.apk
```

Needs **Node**, **JDK 21** (Capacitor 8 will not build on 17) and the Android
SDK with `platforms;android-36` and `build-tools;36.0.0`.

`mobile/keystore/` holds the signing key and is git-ignored. **Back it up.**
Android refuses to install an update over an app signed with a different key,
so losing it means every future version has to be installed fresh.

`mobile/android/`, `mobile/www/` and `node_modules/` are all generated and
git-ignored; the four small files in `mobile/` reproduce them.

## Tuning

`ECONOMY_RATE` near the top of the progression code scales how fast coins come
in. Raise it if unlocking drags, lower it if the garage fills too quickly.

## How it's built

Single-page WebGL game on [three.js](https://threejs.org/) r128 — no build
step, no dependencies to install.

```
index.html                 the whole game: scene, physics, progression, HUD, audio
vendor/three.min.js        three.js, vendored so the app runs offline
manifest.json              PWA metadata that makes it installable
sw.js                      service worker: precaches everything for offline play
icons/                     app icons, including maskable icons for Android
```

To run it locally, serve the folder over HTTP (a service worker will not
register from a `file://` URL):

```sh
python -m http.server 8000
# then open http://localhost:8000
```

## Licence

Game code: MIT. three.js is MIT, © three.js authors.
