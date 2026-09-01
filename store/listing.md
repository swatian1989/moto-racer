# Google Play listing — Musa Moto Racer

Copy-paste material for the Play Console. Character limits are Google's.

---

## App name (30 max)

```
Musa Moto Racer
```

## Short description (80 max)

```
Ride a sunset coast at 300km/h. Dodge traffic, chain near misses, build a garage.
```
<sub>78 characters</sub>

## Full description (4000 max)

```
Thread the traffic on a sunset coastal highway at 300 km/h.

Musa Moto Racer is a fast, no-nonsense arcade racer. No timers, no energy bars,
no waiting. Just you, an open road and the next corner.

NEAR MISSES BUILD COMBOS
Slip past a car in the neighbouring lane and your combo climbs, multiplying
everything you score. Stop threading the traffic and it decays. The closer you
ride, the more you earn.

SIX REAL MACHINES
A naked standard, a tucked-in sport bike, a tall adventure bike with panniers,
a long low cruiser on twin pipes, a winglet-clad superbike, and a silent
electric hyper. Each one is a different machine with its own top speed,
acceleration, grip and nitro tank - not a colour swap.

FOUR LANDSCAPES
Ride the Sunset Coastline with surf on your right. Cross the Canyon Run between
red mesas and saguaro. Climb the Alpine Pass through snowbound pines. Or take
Neon City, which is always after dark, wet asphalt between lit towers.

DAY TURNS TO NIGHT
The clock moves as your run goes on. Stars come out, your headlight starts doing
real work, and oncoming traffic becomes a pair of lights in the dark before it
becomes a car. Weather rolls between clear, rain and storm.

POWER-UPS
Shield eats one crash. Magnet drags coins into your line. 2x Score doubles
everything. Slow-Mo drops the world into a crawl while you keep steering at full
speed.

UPGRADE THE GARAGE
Coins come from pickups, distance and near misses. Spend them on new bikes, on
new landscapes, and on engine, nitro and grip upgrades. Three missions are always
running, and achievements unlock as you go.

PLAYS ANYWHERE
- Fully offline. The whole game is in the app, nothing is downloaded.
- Touch, tilt steering, or a game controller.
- No ads. No in-app purchases. No accounts. No data collected.

Open source under the MIT Licence.
```

---

## Store assets checklist

| Asset | Requirement | File |
| --- | --- | --- |
| App icon | 512x512 PNG, 32-bit | `icons/icon-512.png` |
| Feature graphic | 1024x500 PNG/JPG | `store/feature-graphic.png` |
| Phone screenshots | 2-8, min 320px, 16:9-ish | `store/screenshots/*.png` |
| Privacy policy URL | public https page | `https://swatian1989.github.io/moto-racer/privacy.html` |
| App bundle | .aab | `mobile/dist/MusaMotoRacer.aab` |

## Content rating questionnaire

Answer these honestly and it comes out **PEGI 3 / ESRB Everyone**:

- Violence: **No** — no combat, no injury depicted; crashes end the run
- Sexuality, language, controlled substances, gambling: **No** to all
- User-generated content or sharing: **No** — the leaderboard is local only
- Location sharing / personal info: **No**

## Data safety form

- Does your app collect or share any user data? — **No**
- Is all user data encrypted in transit? — N/A (no data leaves the device)
- Do you provide a way to request deletion? — **Yes**, Settings has Reset Progress

The leaderboard, coins and settings live in `localStorage` on the device. Nothing
is transmitted, so there is nothing to declare as collected.

## Category and tags

- Category: **Games → Racing**
- Tags: arcade racing, endless runner, offline game
- Contains ads: **No**
- In-app purchases: **No**
