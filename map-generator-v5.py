import json
import math

# --- 1. CONFIGURATION: The "Source of Truth" ---

GEO_ORIGIN = { "lat": 47.661378, "lon": -122.365703 } # Substation Seattle

# DATA MODEL
# Dimensions are in meters. 
# Coordinates (x,y) are relative to the top-left of the entire compound.

# A. ROOMS (The main structures)
rooms = [
    {"id": "patio", "name": "Patio", "x": 0, "y": 0, "w": 8, "h": 9, "color": "#FFD700"},
    {"id": "hallway", "name": "Hallway", "x": 2, "y": 9, "w": 26, "h": 3, "color": "#D3D3D3"},
    {"id": "entrance_hall", "name": "", "x": 23, "y": 0, "w": 5, "h": 9, "color": "#D3D3D3"},
    {"id": "exit", "name": "", "x": 8, "y": 1, "w": 1, "h": 8, "color": "#D3D3D3"},
    {"id": "annex", "name": "Annex", "x": 0, "y": 12, "w": 28, "h": 13, "color": "#ADD8E6"},
    {"id": "front_room", "name": "Front Room", "x": 9, "y": 0, "w": 14, "h": 9, "color": "#90EE90"}
]

# B. ZONES (Functional areas INSIDE rooms)
zones = [
    {"id": "stage", "name": "VIP Area / Main Stage", "parent": "annex", "x": 23, "y": 17, "w": 5, "h": 8, "color": "#B7B5B5"}, 
    {"id": "booth", "name": "Sound Booth", "parent": "annex", "x": 1.5, "y": 18.5, "w": 2, "h": 4, "color": "#4682B4"},  
    {"id": "bathroom_annex", "name": "Bathrooms", "parent": "annex", "x": 0, "y": 17, "w": 1.5, "h": 6, "color": "#E6ADE6"},

    {"id": "bathroom_hallway", "name": "Bathrooms", "parent": "hallway", "x": 18, "y": 12, "w": 10, "h": 5, "color": "#E6ADE6"},
    {"id": "lobby", "name": "Lobby", "parent": "hallway", "x": 23, "y": 0, "w": 5, "h": 3, "color":  "#FFA07A"},

    {"id": "bar", "name": "Main Bar__", "parent": "front_room", "x": 9, "y": 7.5, "w": 9, "h": 1.5, "color": "#9D5656"}
 #   {"id": "bar_wall", "name": "", "parent": "front_room", "x": 9, "y": 7, "w": 7, "h": 2, "color": "#8B4513"} 

]

# C. DOORS / OPENINGS
# These act as "erasers" or connectors. 
# Logic: We place a small rectangle over the wall line to represent a gap.
doors = [
    {"name": "Lobby->Front", "x": 24, "y": 2.75, "w": 3, "h": 0.5, "type": "gap"},  
    {"name": "Hallway Turn", "x": 23.5, "y": 8.75, "w": 4, "h": 0.5, "type": "gap"},  
    {"name": "Patio Access", "x": 4, "y": 8.75, "w": 2, "h": 0.5, "type": "gap"},      
    {"name": "Hall->Annex", "x": 6, "y": 11.75, "w": 3, "h": 0.5, "type": "gap"},   
    {"name": "Street Entry", "x": 25.5, "y": 0, "w": 1, "h": 0.5, "type": "gap"},
    {"name": "bathroom0", "x": 0, "y": 18, "w": 0.3, "h": 3.5, "type": "gap"},
    {"name": "bathroom1", "x": 25.5, "y": 11.75, "w": 1.5, "h": 0.5, "type": "gap"},
    {"name": "bathroom2", "x": 19, "y": 11.75, "w": 1.5, "h": 0.5, "type": "gap"}    

]
# D. POLYGONS (Custom shapes)
polygons = [
    # Example: Add custom polygonal areas here
    # {"id": "custom", "name": "Custom Area", "points": [[0,0], [10,0], [10,10], [0,10]], "color": "#FF0000"}
    {"id": "only_cans_bar", "name": "", "points": [[12,12], [18,12], [18,17]], "color": "#5D3030"}
]

# --- 2. LOGIC: Coordinate Conversion ---

def meters_to_gps(x_meters, y_meters, origin):
    earth_radius = 6378137
    dy = -y_meters 
    dx = x_meters
    d_lat = (dy / earth_radius) * (180 / math.pi)
    d_lon = (dx / (earth_radius * math.cos(math.pi * origin["lat"] / 180))) * (180 / math.pi)
    return { "lat": origin["lat"] + d_lat, "lon": origin["lon"] + d_lon }

# --- 3. GENERATOR: SVG ---

def generate_svg(rooms, zones, doors, polygons, filename="substation_detailed.svg"):
    scale = 20 
    padding = 50
    
    # Calculate bounds
    rect_items = rooms + zones + doors
    poly_items = polygons
    max_x_rect = max([r['x'] + r['w'] for r in rect_items]) if rect_items else 0
    max_y_rect = max([r['y'] + r['h'] for r in rect_items]) if rect_items else 0
    max_x_poly = max([max(pt[0] for pt in p['points']) for p in poly_items]) if poly_items else 0
    max_y_poly = max([max(pt[1] for pt in p['points']) for p in poly_items]) if poly_items else 0
    max_x = max(max_x_rect, max_x_poly) * scale
    max_y = max(max_y_rect, max_y_poly) * scale
    
    svg = [
        f'<svg width="{max_x + padding*2}" height="{max_y + padding*2}" '
        f'viewBox="-{padding} -{padding} {max_x + padding*2} {max_y + padding*2}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        '<defs><style>',
        # Styles
        '.wall { fill: none; stroke: black; stroke-width: 3; }', # Thicker outer walls
        '.zone-fill { stroke: none; fill-opacity: 0.5; }', # Zones
        '.zone-line { fill: none; stroke: #333; stroke-width: 1; stroke-dasharray: 5,5; }', # Dashed line for zones
        '.room-fill { fill-opacity: 0.2; stroke: none; }',
        '.door-gap { fill: white; stroke: none; }', # "Erases" the wall
        '.dim-line { stroke: #555; stroke-width: 1; stroke-dasharray: 2; }',
        '.dim-text { font-family: sans-serif; font-size: 10px; fill: #666; text-anchor: middle; }',
        '.label-room { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: black; text-anchor: middle; }',
        '.label-zone { font-family: sans-serif; font-size: 10px; font-weight: normal; fill: #333; text-anchor: middle; font-style: italic;}',
        '</style></defs>'
    ]

    # LAYER 1: Overall Floor Plan (Fills and Walls)
    svg.append('<g id="layer1-structure">')
    
    # Room Fills (Backgrounds)
    for r in rooms:
        svg.append(f'<rect x="{r["x"]*scale}" y="{r["y"]*scale}" width="{r["w"]*scale}" height="{r["h"]*scale}" class="room-fill" fill="{r["color"]}" />')
        
    # Zone Fills (On top of rooms)
    for z in zones:
        svg.append(f'<rect x="{z["x"]*scale}" y="{z["y"]*scale}" width="{z["w"]*scale}" height="{z["h"]*scale}" class="zone-fill" fill="{z["color"]}" />')
        # Add dashed border for zones
        svg.append(f'<rect x="{z["x"]*scale}" y="{z["y"]*scale}" width="{z["w"]*scale}" height="{z["h"]*scale}" class="zone-line" />')

    # Polygon Fills
    for p in polygons:
        points_str = ' '.join([f"{pt[0]*scale},{pt[1]*scale}" for pt in p["points"]])
        svg.append(f'<polygon points="{points_str}" class="room-fill" fill="{p["color"]}" />')

    # Walls (The heavy lines)
    for r in rooms:
        svg.append(f'<rect x="{r["x"]*scale}" y="{r["y"]*scale}" width="{r["w"]*scale}" height="{r["h"]*scale}" class="wall" />')

    # Doors (The "Erasers" / Gaps)
    # We draw white rectangles over the black walls to create openings
    for d in doors:
        # Slightly offset to ensure it covers the stroke
        svg.append(f'<rect x="{(d["x"]*scale)-2}" y="{(d["y"]*scale)-2}" width="{(d["w"]*scale)+4}" height="{(d["h"]*scale)+4}" class="door-gap" />')
        
    svg.append('</g>')

    # LAYER 2: Measurements
    svg.append('<g id="layer2-measurements">')
    
    def draw_dim(x, y, w, h, val, axis):
        if axis == 'x':
            sx, sy, ex, ey = x*scale, (y*scale)-10, (x+w)*scale, (y*scale)-10
            svg.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" class="dim-line" />')
            svg.append(f'<text x="{sx + (ex-sx)/2}" y="{sy - 5}" class="dim-text">{val}m</text>')
        else:
            sx, sy, ex, ey = (x*scale)-10, y*scale, (x*scale)-10, (y+h)*scale
            svg.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" class="dim-line" />')
            svg.append(f'<text x="{sx - 15}" y="{sy + (ey-sy)/2}" class="dim-text">{val}m</text>')

    # Room Dimensions
    for r in rooms:
        draw_dim(r['x'], r['y'], r['w'], r['h'], r['w'], 'x')
        draw_dim(r['x'], r['y'], r['w'], r['h'], r['h'], 'y')
        
    svg.append('</g>')

    # LAYER 3: Labels
    svg.append('<g id="layer3-labels">')
    for r in rooms:
        cx, cy = (r["x"] + r["w"]/2)*scale, (r["y"] + r["h"]/2)*scale
        # If the room has a zone taking up space (like the front room bar), shift label
        if r['id'] == 'front_room': cy += 20 
        svg.append(f'<text x="{cx}" y="{cy}" class="label-room">{r["name"]}</text>')
        
    for z in zones:
        cx, cy = (z["x"] + z["w"]/2)*scale, (z["y"] + z["h"]/2)*scale
        svg.append(f'<text x="{cx}" y="{cy}" class="label-zone">{z["name"]}</text>')
        
    for p in polygons:
        if p.get('name'):
            xs = [pt[0] for pt in p['points']]
            ys = [pt[1] for pt in p['points']]
            cx = sum(xs)/len(xs) * scale
            cy = sum(ys)/len(ys) * scale
            svg.append(f'<text x="{cx}" y="{cy}" class="label-room">{p["name"]}</text>')
    svg.append('</g>')

    svg.append('</svg>')
    
    with open(filename, 'w') as f:
        f.write("\n".join(svg))
    print(f"Generated SVG: {filename}")

# --- 4. GENERATOR: GeoJSON ---

def generate_geojson(rooms, zones, polygons, origin, filename="substation_detailed.geojson"):
    features = []
    
    # Helper to make polygon
    def make_feature(item, properties, poly_type="Room"):
        tl = meters_to_gps(item['x'], item['y'], origin)
        tr = meters_to_gps(item['x'] + item['w'], item['y'], origin)
        br = meters_to_gps(item['x'] + item['w'], item['y'] + item['h'], origin)
        bl = meters_to_gps(item['x'], item['y'] + item['h'], origin)
        
        return {
            "type": "Feature",
            "properties": { **properties, "type": poly_type },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [tl['lon'], tl['lat']], [tr['lon'], tr['lat']],
                    [br['lon'], br['lat']], [bl['lon'], bl['lat']],
                    [tl['lon'], tl['lat']]
                ]]
            }
        }

    for r in rooms:
        features.append(make_feature(r, {"name": r["name"], "height": r["h"]}, "Room"))
        
    for z in zones:
        features.append(make_feature(z, {"name": z["name"], "parent": z.get("parent", "")}, "Zone"))

    for p in polygons:
        coords = [[meters_to_gps(pt[0], pt[1], origin)['lon'], meters_to_gps(pt[0], pt[1], origin)['lat']] for pt in p["points"]]
        coords.append(coords[0])
        features.append({
            "type": "Feature",
            "properties": {"name": p.get("name", ""), "type": "Polygon"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        })

    geojson = { "type": "FeatureCollection", "features": features }
    
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)
    print(f"Generated GeoJSON: {filename}")

# --- EXECUTE ---
if __name__ == "__main__":
    generate_svg(rooms, zones, doors, polygons)
    generate_geojson(rooms, zones, polygons, GEO_ORIGIN)
