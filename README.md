# Moto Racer — Coastline

A 3D sunset-highway racing game that runs in the browser and **installs like a
native app** on Android, iPhone, Windows, Mac and Linux. Once installed it works
with no internet connection at all.

**Play it:** https://swatian1989.github.io/moto-racer/

![Moto Racer](icons/icon-192.png)

## Install it

| Device | How |
| --- | --- |
| **Android** (Chrome / Edge / Samsung) | Open the link, tap **⬇ INSTALL APP** on the title screen. |
| **iPhone / iPad** (Safari) | Open the link, tap **Share**, then **Add to Home Screen**. |
| **Windows / Mac / Linux** (Chrome / Edge) | Open the link, click **⬇ INSTALL APP**, or use the install icon in the address bar. |

After installing, launch it from your home screen, Start menu, Dock or app
drawer. It opens fullscreen with no browser chrome, and **works offline** — the
whole game, including the 3D engine, is stored on the device.

## Controls

| | Touch | Keyboard |
| --- | --- | --- |
| Steer | ◀ ▶ buttons, or tilt the phone | `←` `→` or `A` `D` |
| Throttle | 🔥 GAS | `↑` or `W` |
| Nitro | ⚡ NOS | `N` or `Shift` |
| Jump | JUMP | `Space` |
| Pause | ⏸ | `P` or `Esc` |
| Fullscreen | ⛶ | `F` |
| Mute | 🔊 | `M` |

Dodge traffic, grab coins, and ride as far as you can. Weather shifts between
clear, rain and storm as the run goes on. Your best distance and the top-10
leaderboard are stored on your device.

## How it's built

Single-page WebGL game on [three.js](https://threejs.org/) r128 — no build step,
no dependencies to install.

```
index.html                 the whole game: scene, physics, HUD, audio
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
