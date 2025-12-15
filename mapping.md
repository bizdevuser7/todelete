# Mapping

This repository uses **GeoJSON** as the canonical, portable map format (iOS / watchOS / Android). The `mapping-tools/map-generator-v6.py` script generates:

- `detailed.svg` (human-friendly visual inspection)
- `detailed.geojson` (canonical data for clients)

## map-generator-v6.py

### Quickstart

From `mapping-tools/`:

```bash
python3 map-generator-v6.py
```

This writes:

- `detailed.svg`
- `detailed.geojson`

To bootstrap suggested beacon placements:

```bash
python3 map-generator-v6.py --auto-anchors
```

The script prints:

- `Generated SVG: ...`
- `Generated GeoJSON: ...`

### CLI

- `--svg`
  - Generate SVG only.
- `--geojson`
  - Generate GeoJSON only.
- `--out-svg <filename>`
  - Default: `detailed.svg`
- `--out-geojson <filename>`
  - Default: `detailed.geojson`

SVG layer toggles:

- `--no-structure`
- `--no-measurements`
- `--no-labels`
- `--no-markers`

GeoJSON feature toggles:

- `--no-rooms`
- `--no-zones`
- `--no-polygons`
- `--no-pins`
- `--no-anchors`
- `--no-metadata`

Anchor generation:

- `--auto-anchors`
  - Adds suggested anchors (in addition to any explicitly defined in `anchors`).

### Data model (in-script)

The script currently defines these top-level collections:

- `rooms`: axis-aligned rectangles (meters)
- `zones`: axis-aligned rectangles (meters) with `parent` room id
- `doors`: rectangles (meters) used for SVG structure only (not exported to GeoJSON)
- `polygons`: arbitrary polygons (meters)
- `pins`: point markers (meters)
- `anchors`: point markers (meters)

All coordinates in these collections are in **meters** in a local indoor coordinate system:

- Origin `(0, 0)` is the **top-left** of the map.
- +x goes **right**.
- +y goes **down**.

### GPS origin + conversion

GeoJSON is emitted in WGS84 lat/lon using a fixed origin:

- `GEO_ORIGIN = {"lat": ..., "lon": ...}`

Conversions:

- `meters_to_gps(x_m, y_m, origin)`
- `gps_to_meters(lat, lon, origin)`

Important: because y increases downward in the indoor coordinate system, conversion uses `dy = -y_meters` when computing latitude offset.

## GeoJSON output schema

The script writes a single `FeatureCollection` with a mixture of polygons and points.

### Feature: Metadata

A single point feature that anchors the map’s coordinate system and bounds:

- `properties.type = "Metadata"`
- `properties.geo_origin_lat`
- `properties.geo_origin_lon`
- `properties.width_m`
- `properties.height_m`

`geometry` is a `Point` at `[origin.lon, origin.lat]`.

### Feature: Room

Axis-aligned polygon derived from a rectangle:

- `properties.type = "Room"`
- `properties.id`
- `properties.name`
- `properties.height` (copied from room `h`)

`geometry.type = "Polygon"` with coordinates closed (first point repeated).

### Feature: Zone

Axis-aligned polygon derived from a rectangle:

- `properties.type = "Zone"`
- `properties.id`
- `properties.name`
- `properties.parent` (room id)

### Feature: Polygon

Arbitrary polygon from the `polygons` list:

- `properties.type = "Polygon"`
- `properties.id`
- `properties.name`

### Feature: Pin

Point feature representing a human/venue reference point (entrances, corners, calibration spots):

- `properties.type = "Pin"`
- `properties.id`
- `properties.name`
- `properties.kind` (default `"pin"`)
- `properties.color`
- `properties.x_m`
- `properties.y_m`

`geometry.type = "Point"` with `[lon, lat]`.

### Feature: Anchor

Point feature representing a beacon placement (planned or deployed):

- `properties.type = "Anchor"`
- `properties.id`
- `properties.name`
- `properties.kind` (default `"beacon"`)
- `properties.room` (room id)
- `properties.suggested` (boolean)
- `properties.color`
- `properties.roleId` (optional)
- `properties.tgId` (optional)
- `properties.x_m`
- `properties.y_m`

### Notes

- Doors are currently only used to visually represent gaps/entries in SVG.
- Clients should treat GeoJSON as authoritative and ignore SVG.
- Clients should prefer `x_m/y_m` for deterministic indoor placement and use lat/lon primarily for GPS alignment and debugging.

## How to add / edit points

### Pins

Add a dict to `pins`:

- required: `id`, `x`, `y`
- recommended: `name`, `kind`, `color`

### Anchors

Add a dict to `anchors`:

- required: `id`, `x`, `y`, `room`
- recommended: `name`, `kind`, `color`, `roleId`, `tgId`

If using `--auto-anchors`, suggested anchors are appended and marked with:

- `suggested: True`

## Suggested anchor placement logic

`--auto-anchors` uses `recommend_anchors(rooms)`:

- Small rooms: 1 anchor
- Medium rooms: 2 anchors
- Large rooms: 3 anchors

Suggested points are centered with offsets derived from room dimensions.

This is intended as a bootstrap; real placements should be curated and then written into `anchors` (or a future external config).
