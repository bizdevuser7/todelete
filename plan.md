# Venue Mapping Strategy + Operational Plan

This document describes how we use **pins**, **anchors**, and repeated **TotemNode** placements to iteratively improve indoor positioning in dense crowds and to define high-confidence **handoff zones** (e.g., UWB experiences).

## Goals

- **Room-level reliability first**: stable “which virtual room am I in?” despite crowd attenuation and multipath.
- **Zone / handoff refinement next**: identify high-quality areas within rooms where we can trigger experiences or hand off to higher-precision systems (e.g., UWB).
- **Repeatable deployments**: consistent placements that can be replicated across events.
- **Upgrade loop**: collect data, tune placements and logic, regenerate maps, redeploy.

## Core assumptions

- We deploy **3 TotemNodes per virtual room/placement**.
- Placements should be **replicable** (same relative geometry each time) to maintain signal characteristics and reduce per-event tuning.
- GeoJSON is the canonical map configuration for clients.

## Definitions

- **Virtual room**: a logical region used by inference and UX (may map 1:1 to a physical room, or subdivide a large room).
- **Anchor**: a point representing a planned/deployed beacon location (TotemNode placement). Anchors can be suggested (`suggested: true`) or curated.
- **Pin**: a human reference point used for calibration, validation, and operations (“stand here and verify”).
- **Handoff zone**: an area where beacon signal patterns produce sufficiently high confidence to trigger an experience or transition to another system.

## Phase 0: Base map + coordinate system

- Maintain an indoor coordinate system in meters.
- Choose a GPS origin (`GEO_ORIGIN`) so map features can be exported to lat/lon.
- Generate initial outputs:

```bash
python3 mapping-tools/map-generator-v6.py
```

Outputs:

- `detailed.svg` for inspection
- `detailed.geojson` for clients

## Phase 1: Bootstrap anchors (auto)

Use auto anchors to get started quickly:

```bash
python3 mapping-tools/map-generator-v6.py --auto-anchors
```

- This provides a baseline distribution of anchors per room (1–3 depending on size).
- Treat these as candidate placements.

### Immediate next step

- Curate anchors into “real” placements:
  - remove impractical suggestions
  - adjust to physically mountable positions
  - ensure each virtual room has exactly **3** anchors for the initial plan

## Phase 2: Pin-based calibration + validation

Add a small set of **Pins** that represent places operators can stand during setup and where expected results are unambiguous:

- Entrance / street-facing start point
- Major transitions (doorways, hallway turns)
- High-value experience points (candidate handoff zones)
- Room centers or known open areas

Use pins for:

- verifying GPS↔map alignment
- verifying room classification stability
- recording reference measurements across deployments

## Phase 3: Deployment geometry (3-node per virtual room)

### Placement pattern

Use a consistent geometry per virtual room:

- **One “coverage” anchor** near the center or main occupancy area.
- **Two “disambiguation” anchors** offset to create distinctive gradients.

Guidelines:

- Spread anchors so that the expected RSSI ordering changes meaningfully across the room.
- Avoid co-linear placements when possible.
- Prefer mount points that are stable across events (fixed structures).
- Consider height consistency (e.g., all head-height or all above-head) unless experimenting deliberately.

### Replication

For recurring events:

- replicate the same relative placements and heights
- keep anchor IDs stable (or map physical units to stable role IDs)

## Phase 4: Handoff zone discovery

We find “handoff zones” by experimenting with:

- anchor placement
- thresholding + smoothing parameters in inference
- collecting field observations

Recommended process:

- Pick a handful of candidate areas (near stage edge, bar queue edge, lobby entrance, etc.).
- Add pins for each candidate.
- Run multiple walks and standing tests during low-crowd and high-crowd conditions.

A good handoff zone has:

- high confidence
- low flip rate between adjacent rooms/zones
- resilience to human bodies and orientation

## Phase 5: Dense crowd tuning loop

Crowds change RF conditions. Expect:

- attenuation (body blocking)
- multipath reflections
- transient occlusion

Operational loop:

1. **Generate map** (anchors + pins updated)
2. **Deploy anchors** (3 per virtual room)
3. **Collect observations** (walk tests + live crowd)
4. **Analyze**
   - where misclassifications happen
   - where confidence collapses
   - where “sticky” incorrect rooms happen
5. **Adjust**
   - move anchors
   - add/relocate pins
   - split/merge virtual rooms if needed
6. **Regenerate + redeploy**

## Phase 6: UWB / higher precision handoff

Beacon-based inference provides:

- coarse-to-medium accuracy
- reliable room/zone context

Use that context to:

- guide users into a handoff zone
- trigger UWB session start only when confidence is high

## Data management + versioning

Recommended conventions (operationally, even if not yet encoded in the script):

- Maintain a versioned GeoJSON per venue:
  - `venue/<venue_id>/maps/<date_or_version>/detailed.geojson`
- Record a changelog for each iteration:
  - anchor moves
  - new pins
  - inference parameter changes

## Checklist (per deployment)

- Validate `GEO_ORIGIN` (GPS alignment sanity check)
- Confirm anchor count: **3 per virtual room**
- Verify physical feasibility (power, mounting, safety)
- Walk test each room boundary
- Stand test each candidate handoff zone pin
- Capture notes on crowd density + anomalies

## Next work items

- Move from in-script lists to an external venue config file (optional future step).
- Add explicit map version metadata to GeoJSON.
- Add a lightweight field log template for setup + walk tests.
