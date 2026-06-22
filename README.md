# BiteRisk

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Schnabel80/biterisk-ha.svg)](https://github.com/Schnabel80/biterisk-ha/releases)

A Home Assistant custom integration that estimates **mosquito bite risk** (low / medium / high) from your local weather sensors.

Based on *Culex pipiens* (Common House Mosquito) biology for Germany/Central Europe:
- **Temperature** — active between 10–35 °C, optimal 20–25 °C
- **Humidity** — prefers > 80 % relative humidity
- **Time of day** — crepuscular peak 30 min before to 3 h after sunset
- **Wind** — suppressed above 0.5 m/s, zero above 3 m/s
- **Brood population** — 21-day lag-weighted rain model (larval development ~10 days)

## Sensors

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.biterisk_mosquito_risk` | text | **low / medium / high** |
| `sensor.biterisk_mosquito_score` | 0–100 | Numeric score for history charts |
| `sensor.biterisk_brood_factor` | 0–1 | 21-day rain brood estimate |
| `sensor.biterisk_temperature_factor` | 0–1 | Temperature curve |
| `sensor.biterisk_humidity_factor` | 0–1 | Humidity curve |
| `sensor.biterisk_wind_factor` | 0–1 | Wind suppression |
| `sensor.biterisk_time_factor` | 0–1 | Crepuscular time bell |

## Installation (HACS)

1. In HACS → **Custom Repositories** → add `Schnabel80/biterisk-ha` (type: Integration)
2. Install **BiteRisk** and restart Home Assistant
3. **Settings → Devices & Services → Add Integration → BiteRisk**
4. Select your temperature, humidity, wind, and rain sensors
5. Choose your floor level (EG / 1.OG / 2.OG+)

## Floor modifier

Each integration instance represents one location. Multiple instances cover different floors:
- Ground floor (EG): ×1.0
- 1st floor (1.OG): ×0.8
- 2nd floor+ (2.OG+): ×0.6

## Dashboard example

```yaml
type: history-graph
title: Mosquito Score (last 12h)
entities:
  - entity: sensor.biterisk_mosquito_score
hours_to_show: 12
```

## Scientific basis

- Culex temperature review: Springer 2023
- Wind & mosquito flight: J. Med. Entomol. 2003
- Rainfall & Culex dynamics: PubMed 2017
- Vertical floor distribution: PMC 2023
- Crepuscular activity: Springer 2026
