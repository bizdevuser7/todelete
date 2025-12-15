import argparse
import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Coordinates (x,y) are relative to the top-left of the area mapped
GEO_ORIGIN = {"lat": 47.661378, "lon": -122.365703}

rooms = [
    {"id": "patio", "name": "Patio", "x": 0, "y": 0, "w": 8, "h": 9, "color": "#FFD700"},
    {"id": "hallway", "name": "Hallway", "x": 2, "y": 9, "w": 26, "h": 3, "color": "#D3D3D3"},
    {"id": "entrance_hall", "name": "", "x": 23, "y": 0, "w": 5, "h": 9, "color": "#D3D3D3"},
    {"id": "exit", "name": "", "x": 8, "y": 1, "w": 1, "h": 8, "color": "#D3D3D3"},
    {"id": "annex", "name": "Annex", "x": 0, "y": 12, "w": 28, "h": 13, "color": "#ADD8E6"},
    {"id": "front_room", "name": "Front Room", "x": 9, "y": 0, "w": 14, "h": 9, "color": "#90EE90"},
]

zones = [
    {"id": "stage", "name": "VIP Area / Main Stage", "parent": "annex", "x": 23, "y": 17, "w": 5, "h": 8, "color": "#B7B5B5"},
    {"id": "booth", "name": "Sound Booth", "parent": "annex", "x": 1.5, "y": 18.5, "w": 2, "h": 4, "color": "#4682B4"},
    {"id": "annex_pole", "name": "pole", "parent": "annex", "x": 9, "y": 16.5, "w": .5, "h": .5, "color": "#9D5656"},
    {"id": "bathroom_annex", "name": "Bathrooms", "parent": "annex", "x": 0, "y": 17, "w": 1.5, "h": 6, "color": "#E6ADE6"},
    {"id": "bathroom_hallway", "name": "Bathrooms", "parent": "hallway", "x": 18, "y": 12, "w": 10, "h": 5, "color": "#E6ADE6"},
    {"id": "photobooth", "name": "Photobooth", "parent": "hallway", "x": 19, "y": 9, "w": 4, "h": 1.25, "color":  "#4682B4"},
    {"id": "lobby", "name": "Lobby", "parent": "hallway", "x": 23, "y": 0, "w": 5, "h": 3, "color": "#FFA07A"},
    {"id": "bar", "name": "Main Bar__", "parent": "front_room", "x": 9, "y": 7.5, "w": 9, "h": 1.5, "color": "#9D5656"},
]

doors = [
    {"name": "Lobby->Front", "x": 24, "y": 2.75, "w": 3, "h": 0.5, "type": "gap"},
    {"name": "Hallway Turn", "x": 23.5, "y": 8.75, "w": 4, "h": 0.5, "type": "gap"},
    {"name": "Patio Access", "x": 4, "y": 8.75, "w": 2, "h": 0.5, "type": "gap"},
    {"name": "Hall->Annex", "x": 6, "y": 11.75, "w": 3, "h": 0.5, "type": "gap"},
    {"name": "Hall->Front_Room", "x": 22.75, "y": 5.5, "w": .5, "h": 1.25, "type": "gap"},
    {"name": "Street Entry", "x": 25.5, "y": 0, "w": 1, "h": 0.5, "type": "gap"},
    {"name": "bathroom0", "x": 0, "y": 18, "w": 0.3, "h": 3.5, "type": "gap"},
    {"name": "bathroom1", "x": 25.5, "y": 11.75, "w": 1.5, "h": 0.5, "type": "gap"},
    {"name": "bathroom2", "x": 19, "y": 11.75, "w": 1.5, "h": 0.5, "type": "gap"},
]

polygons = [
    {"id": "only_cans_bar", "name": "", "points": [[12, 12], [18, 12], [18, 17]], "color": "#5D3030"}
]

pins: List[Dict[str, Any]] = [
    {"id": "pin_entrance", "name": "Entrance", "x": 25.8, "y": 0.8, "kind": "entrance", "color": "#1E90FF"},
    {"id": "pin_hall_turn", "name": "Hall Turn", "x": 25.0, "y": 9, "kind": "corner", "color": "#1E90FF"},
]

anchors: List[Dict[str, Any]] = [
    {"id": "anchor_annex_01", "name": "Anchor-A1", "x": 7, "y": 24.5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_annex_02", "name": "Anchor-A2", "x": 15, "y": 15, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_annex_03", "name": "Anchor-A3", "x": 21, "y": 24.5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_patio_01", "name": "Anchor-P1", "x": 6, "y": 2, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_patio_02", "name": "Anchor-P2", "x": 2, "y": 5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_patio_03", "name": "Anchor-P3", "x": 7, "y": 8.5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_frontroom_01", "name": "Anchor-F1", "x": 13, "y": 0.5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_frontroom_02", "name": "Anchor-F2", "x": 19, "y": 0.5, "kind": "corner", "color": "#FF1E44"},
    {"id": "anchor_frontroom_03", "name": "Anchor-F3", "x": 22.5, "y": 7.5, "kind": "corner", "color": "#FF1E44"},
]

@dataclass(frozen=True)
class Bounds:
    width_m: float
    height_m: float


def meters_to_gps(x_meters: float, y_meters: float, origin: Dict[str, float]) -> Dict[str, float]:
    earth_radius = 6378137
    dy = -y_meters
    dx = x_meters
    d_lat = (dy / earth_radius) * (180 / math.pi)
    d_lon = (dx / (earth_radius * math.cos(math.pi * origin["lat"] / 180))) * (180 / math.pi)
    return {"lat": origin["lat"] + d_lat, "lon": origin["lon"] + d_lon}


def gps_to_meters(lat: float, lon: float, origin: Dict[str, float]) -> Dict[str, float]:
    earth_radius = 6378137
    d_lat = (lat - origin["lat"]) * (math.pi / 180)
    d_lon = (lon - origin["lon"]) * (math.pi / 180)
    dy = d_lat * earth_radius
    dx = d_lon * (earth_radius * math.cos(math.pi * origin["lat"] / 180))
    return {"x": dx, "y": -dy}


def compute_bounds_m(rooms_: List[Dict[str, Any]], zones_: List[Dict[str, Any]], doors_: List[Dict[str, Any]], polygons_: List[Dict[str, Any]], pins_: List[Dict[str, Any]], anchors_: List[Dict[str, Any]]) -> Bounds:
    rect_items = rooms_ + zones_ + doors_
    max_x_rect = max([r["x"] + r["w"] for r in rect_items]) if rect_items else 0
    max_y_rect = max([r["y"] + r["h"] for r in rect_items]) if rect_items else 0

    def poly_max(items: List[Dict[str, Any]], axis: int) -> float:
        if not items:
            return 0
        return max(max(pt[axis] for pt in p["points"]) for p in items)

    max_x_poly = poly_max(polygons_, 0)
    max_y_poly = poly_max(polygons_, 1)

    max_x_pts = max([p["x"] for p in pins_ + anchors_], default=0)
    max_y_pts = max([p["y"] for p in pins_ + anchors_], default=0)

    return Bounds(width_m=max(max_x_rect, max_x_poly, max_x_pts), height_m=max(max_y_rect, max_y_poly, max_y_pts))


def recommend_anchors(rooms_: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rooms_:
        room_id = r.get("id", "")
        if not room_id:
            continue
        area = float(r.get("w", 0)) * float(r.get("h", 0))
        if area <= 0:
            continue

        w = float(r["w"])
        h = float(r["h"])
        x0 = float(r["x"])
        y0 = float(r["y"])
        cx = x0 + w / 2
        cy = y0 + h / 2

        if area < 60:
            count = 1
        elif area < 150:
            count = 2
        else:
            count = 3

        points: List[Tuple[float, float]] = [(cx, cy)]
        if count >= 2:
            ox = max(1.0, min(w * 0.25, 4.0))
            oy = max(1.0, min(h * 0.25, 4.0))
            points.append((cx + ox, cy + oy))
        if count >= 3:
            ox = max(1.0, min(w * 0.25, 4.0))
            oy = max(1.0, min(h * 0.25, 4.0))
            points.append((cx - ox, cy + oy))

        for idx, (ax, ay) in enumerate(points):
            out.append(
                {
                    "id": f"anchor_suggested_{room_id}_{idx}",
                    "name": f"Suggested Anchor {idx + 1}",
                    "x": ax,
                    "y": ay,
                    "kind": "beacon",
                    "room": room_id,
                    "suggested": True,
                    "color": "#FF1493",
                }
            )
    return out


def generate_svg(
    rooms_: List[Dict[str, Any]],
    zones_: List[Dict[str, Any]],
    doors_: List[Dict[str, Any]],
    polygons_: List[Dict[str, Any]],
    pins_: List[Dict[str, Any]],
    anchors_: List[Dict[str, Any]],
    filename: str,
    include_structure: bool,
    include_measurements: bool,
    include_labels: bool,
    include_markers: bool,
) -> None:
    scale = 20
    padding = 50

    bounds = compute_bounds_m(rooms_, zones_, doors_, polygons_, pins_, anchors_)
    max_x = bounds.width_m * scale
    max_y = bounds.height_m * scale

    svg: List[str] = [
        f'<svg width="{max_x + padding * 2}" height="{max_y + padding * 2}" '
        f'viewBox="-{padding} -{padding} {max_x + padding * 2} {max_y + padding * 2}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        "<defs><style>",
        ".wall { fill: none; stroke: black; stroke-width: 3; }",
        ".zone-fill { stroke: none; fill-opacity: 0.5; }",
        ".zone-line { fill: none; stroke: #333; stroke-width: 1; stroke-dasharray: 5,5; }",
        ".room-fill { fill-opacity: 0.2; stroke: none; }",
        ".door-gap { fill: white; stroke: none; }",
        ".dim-line { stroke: #555; stroke-width: 1; stroke-dasharray: 2; }",
        ".dim-text { font-family: sans-serif; font-size: 10px; fill: #666; text-anchor: middle; }",
        ".label-room { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: black; text-anchor: middle; }",
        ".label-zone { font-family: sans-serif; font-size: 10px; font-weight: normal; fill: #333; text-anchor: middle; font-style: italic;}",
        ".marker-pin { stroke: white; stroke-width: 2; }",
        ".marker-anchor { stroke: white; stroke-width: 2; }",
        ".marker-label { font-family: sans-serif; font-size: 10px; fill: #111; }",
        "</style></defs>",
    ]

    if include_structure:
        svg.append('<g id="layer1-structure">')
        for r in rooms_:
            svg.append(
                f'<rect x="{r["x"] * scale}" y="{r["y"] * scale}" width="{r["w"] * scale}" height="{r["h"] * scale}" class="room-fill" fill="{r["color"]}" />'
            )
        for z in zones_:
            svg.append(
                f'<rect x="{z["x"] * scale}" y="{z["y"] * scale}" width="{z["w"] * scale}" height="{z["h"] * scale}" class="zone-fill" fill="{z["color"]}" />'
            )
            svg.append(
                f'<rect x="{z["x"] * scale}" y="{z["y"] * scale}" width="{z["w"] * scale}" height="{z["h"] * scale}" class="zone-line" />'
            )
        for p in polygons_:
            points_str = " ".join([f"{pt[0] * scale},{pt[1] * scale}" for pt in p["points"]])
            svg.append(f'<polygon points="{points_str}" class="room-fill" fill="{p["color"]}" />')
        for r in rooms_:
            svg.append(
                f'<rect x="{r["x"] * scale}" y="{r["y"] * scale}" width="{r["w"] * scale}" height="{r["h"] * scale}" class="wall" />'
            )
        for d in doors_:
            svg.append(
                f'<rect x="{(d["x"] * scale) - 2}" y="{(d["y"] * scale) - 2}" width="{(d["w"] * scale) + 4}" height="{(d["h"] * scale) + 4}" class="door-gap" />'
            )
        svg.append("</g>")

    if include_measurements:
        svg.append('<g id="layer2-measurements">')

        def draw_dim(x: float, y: float, w: float, h: float, val: float, axis: str) -> None:
            if axis == "x":
                sx, sy, ex, ey = x * scale, (y * scale) - 10, (x + w) * scale, (y * scale) - 10
                svg.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" class="dim-line" />')
                svg.append(f'<text x="{sx + (ex - sx) / 2}" y="{sy - 5}" class="dim-text">{val}m</text>')
            else:
                sx, sy, ex, ey = (x * scale) - 10, y * scale, (x * scale) - 10, (y + h) * scale
                svg.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" class="dim-line" />')
                svg.append(f'<text x="{sx - 15}" y="{sy + (ey - sy) / 2}" class="dim-text">{val}m</text>')

        for r in rooms_:
            draw_dim(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r["w"]), "x")
            draw_dim(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r["h"]), "y")

        svg.append("</g>")

    if include_labels:
        svg.append('<g id="layer3-labels">')
        for r in rooms_:
            cx, cy = (r["x"] + r["w"] / 2) * scale, (r["y"] + r["h"] / 2) * scale
            if r.get("id") == "front_room":
                cy += 20
            svg.append(f'<text x="{cx}" y="{cy}" class="label-room">{r["name"]}</text>')
        for z in zones_:
            cx, cy = (z["x"] + z["w"] / 2) * scale, (z["y"] + z["h"] / 2) * scale
            svg.append(f'<text x="{cx}" y="{cy}" class="label-zone">{z["name"]}</text>')
        for p in polygons_:
            if p.get("name"):
                xs = [pt[0] for pt in p["points"]]
                ys = [pt[1] for pt in p["points"]]
                cx = sum(xs) / len(xs) * scale
                cy = sum(ys) / len(ys) * scale
                svg.append(f'<text x="{cx}" y="{cy}" class="label-room">{p["name"]}</text>')
        svg.append("</g>")

    if include_markers:
        svg.append('<g id="layer4-markers">')

        def marker(item: Dict[str, Any], radius: float, klass: str) -> None:
            x = float(item["x"]) * scale
            y = float(item["y"]) * scale
            color = item.get("color", "#FF1493")
            svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" class="{klass}" />')
            label = item.get("name") or item.get("id")
            if label:
                svg.append(f'<text x="{x + radius + 4}" y="{y + 4}" class="marker-label">{label}</text>')

        for p in pins_:
            marker(p, radius=5, klass="marker-pin")
        for a in anchors_:
            marker(a, radius=7, klass="marker-anchor")

        svg.append("</g>")

    svg.append("</svg>")

    with open(filename, "w") as f:
        f.write("\n".join(svg))
    print(f"Generated SVG: {filename}")



def generate_geojson(
    rooms_: List[Dict[str, Any]],
    zones_: List[Dict[str, Any]],
    polygons_: List[Dict[str, Any]],
    pins_: List[Dict[str, Any]],
    anchors_: List[Dict[str, Any]],
    origin: Dict[str, float],
    filename: str,
    include_rooms: bool,
    include_zones: bool,
    include_polygons: bool,
    include_pins: bool,
    include_anchors: bool,
    include_metadata: bool,
) -> None:
    features: List[Dict[str, Any]] = []

    def make_rect_feature(item: Dict[str, Any], properties: Dict[str, Any], poly_type: str) -> Dict[str, Any]:
        tl = meters_to_gps(item["x"], item["y"], origin)
        tr = meters_to_gps(item["x"] + item["w"], item["y"], origin)
        br = meters_to_gps(item["x"] + item["w"], item["y"] + item["h"], origin)
        bl = meters_to_gps(item["x"], item["y"] + item["h"], origin)
        return {
            "type": "Feature",
            "properties": {**properties, "type": poly_type},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [tl["lon"], tl["lat"]],
                        [tr["lon"], tr["lat"]],
                        [br["lon"], br["lat"]],
                        [bl["lon"], bl["lat"]],
                        [tl["lon"], tl["lat"]],
                    ]
                ],
            },
        }

    def make_poly_feature(item: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
        coords = [[meters_to_gps(pt[0], pt[1], origin)["lon"], meters_to_gps(pt[0], pt[1], origin)["lat"]] for pt in item["points"]]
        coords.append(coords[0])
        return {
            "type": "Feature",
            "properties": {**properties, "type": "Polygon"},
            "geometry": {"type": "Polygon", "coordinates": [coords]},
        }

    def make_point_feature(item: Dict[str, Any], properties: Dict[str, Any], point_type: str) -> Dict[str, Any]:
        gps = meters_to_gps(float(item["x"]), float(item["y"]), origin)
        return {
            "type": "Feature",
            "properties": {**properties, "type": point_type, "x_m": float(item["x"]), "y_m": float(item["y"])},
            "geometry": {"type": "Point", "coordinates": [gps["lon"], gps["lat"]]},
        }

    bounds = compute_bounds_m(rooms_, zones_, [], polygons_, pins_, anchors_)

    if include_metadata:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "type": "Metadata",
                    "geo_origin_lat": origin["lat"],
                    "geo_origin_lon": origin["lon"],
                    "width_m": bounds.width_m,
                    "height_m": bounds.height_m,
                },
                "geometry": {"type": "Point", "coordinates": [origin["lon"], origin["lat"]]},
            }
        )

    if include_rooms:
        for r in rooms_:
            features.append(make_rect_feature(r, {"id": r.get("id", ""), "name": r.get("name", ""), "height": r.get("h", None)}, "Room"))

    if include_zones:
        for z in zones_:
            features.append(make_rect_feature(z, {"id": z.get("id", ""), "name": z.get("name", ""), "parent": z.get("parent", "")}, "Zone"))

    if include_polygons:
        for p in polygons_:
            features.append(make_poly_feature(p, {"id": p.get("id", ""), "name": p.get("name", "")}))

    if include_pins:
        for p in pins_:
            features.append(
                make_point_feature(
                    p,
                    {
                        "id": p.get("id", ""),
                        "name": p.get("name", ""),
                        "kind": p.get("kind", "pin"),
                        "color": p.get("color", ""),
                    },
                    "Pin",
                )
            )

    if include_anchors:
        for a in anchors_:
            features.append(
                make_point_feature(
                    a,
                    {
                        "id": a.get("id", ""),
                        "name": a.get("name", ""),
                        "kind": a.get("kind", "beacon"),
                        "room": a.get("room", ""),
                        "suggested": bool(a.get("suggested", False)),
                        "color": a.get("color", ""),
                        "roleId": a.get("roleId", None),
                        "tgId": a.get("tgId", None),
                    },
                    "Anchor",
                )
            )

    geojson = {"type": "FeatureCollection", "features": features}

    with open(filename, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"Generated GeoJSON: {filename}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--svg", dest="svg", action="store_true")
    parser.add_argument("--geojson", dest="geojson", action="store_true")
    parser.add_argument("--out-svg", dest="out_svg", default="detailed.svg")
    parser.add_argument("--out-geojson", dest="out_geojson", default="detailed.geojson")

    parser.add_argument("--no-structure", dest="include_structure", action="store_false", default=True)
    parser.add_argument("--no-measurements", dest="include_measurements", action="store_false", default=True)
    parser.add_argument("--no-labels", dest="include_labels", action="store_false", default=True)
    parser.add_argument("--no-markers", dest="include_markers", action="store_false", default=True)

    parser.add_argument("--no-rooms", dest="include_rooms", action="store_false", default=True)
    parser.add_argument("--no-zones", dest="include_zones", action="store_false", default=True)
    parser.add_argument("--no-polygons", dest="include_polygons", action="store_false", default=True)
    parser.add_argument("--no-pins", dest="include_pins", action="store_false", default=True)
    parser.add_argument("--no-anchors", dest="include_anchors", action="store_false", default=True)
    parser.add_argument("--no-metadata", dest="include_metadata", action="store_false", default=True)

    parser.add_argument("--auto-anchors", dest="auto_anchors", action="store_true")

    args = parser.parse_args()

    anchors_out = list(anchors)
    if args.auto_anchors:
        anchors_out = anchors_out + recommend_anchors(rooms)

    if not args.svg and not args.geojson:
        args.svg = True
        args.geojson = True

    if args.svg:
        generate_svg(
            rooms_=rooms,
            zones_=zones,
            doors_=doors,
            polygons_=polygons,
            pins_=pins,
            anchors_=anchors_out,
            filename=args.out_svg,
            include_structure=args.include_structure,
            include_measurements=args.include_measurements,
            include_labels=args.include_labels,
            include_markers=args.include_markers,
        )

    if args.geojson:
        generate_geojson(
            rooms_=rooms,
            zones_=zones,
            polygons_=polygons,
            pins_=pins,
            anchors_=anchors_out,
            origin=GEO_ORIGIN,
            filename=args.out_geojson,
            include_rooms=args.include_rooms,
            include_zones=args.include_zones,
            include_polygons=args.include_polygons,
            include_pins=args.include_pins,
            include_anchors=args.include_anchors,
            include_metadata=args.include_metadata,
        )


if __name__ == "__main__":
    main()
