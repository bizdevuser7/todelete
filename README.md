

# mapping-tools

This folder contains the venue mapping artifacts and generators.

## Map generator

- Canonical generator: `map-generator-v6.py`
- Outputs (by default):
  - `detailed.svg`
  - `detailed.geojson`

Quickstart:

```bash
python3 map-generator-v6.py
```

Bootstrap suggested anchors:

```bash
python3 map-generator-v6.py --auto-anchors
```

## Documentation

- `mapping.md`
  - Script behavior (CLI), layers, and GeoJSON schema (rooms / zones / polygons / pins / anchors / metadata).
- `plan.md`
  - Venue mapping strategy + operational plan (3 TotemNodes per virtual room, replication strategy, handoff zone discovery, dense crowd tuning loop).
