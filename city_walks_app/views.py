from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import mimetypes

from django.conf import settings
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import render

from .models import load_all_walks, load_walk, walks_by_city, _load_poi

CONTENT_DIR = Path(settings.BASE_DIR) / "content"

# Warm palette — one colour per city, cycling
_CITY_COLORS = [
    "#b8532b", "#c96840", "#9a3e1a", "#d4875a",
    "#7a3010", "#e0956a", "#6b2b0e", "#bf6035",
]


def content_image(request, path):
    file_path = CONTENT_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise Http404
    mime, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(open(file_path, "rb"), content_type=mime or "image/jpeg")


def home(request):
    walks = load_all_walks()
    cities = walks_by_city(walks)

    # Assign a colour to each city for the map
    color_map = {
        c["path"]: _CITY_COLORS[i % len(_CITY_COLORS)]
        for i, c in enumerate(cities)
    }

    all_routes = [
        {
            "title": w.title,
            "city": w.city_name,
            "path": w.path,
            "color": color_map.get(w.city_path, _CITY_COLORS[0]),
            "route": w.route,
        }
        for w in walks
        if w.route
    ]

    total_km = round(sum(w.distance_km for w in walks), 0)

    return render(request, "city_walks_app/home.html", {
        "walks": walks,
        "cities": cities,
        "all_routes_json": json.dumps(all_routes),
        "total_walks": len(walks),
        "total_cities": len(cities),
        "total_km": int(total_km),
    })


def walk_detail(request, path):
    walk = load_walk(path)
    if not walk:
        raise Http404

    # Load full waypoint POI data for the map
    city_path = walk.city_path
    waypoints_data = []
    for slug in walk.waypoints:
        poi = _load_poi(f"{city_path}/{slug}")
        if poi:
            waypoints_data.append({
                "slug": slug,
                "title": poi.title,
                "lat": poi.latitude or None,
                "lng": poi.longitude or None,
                "snippet": poi.meta.get("snippet", ""),
            })
        else:
            waypoints_data.append({
                "slug": slug,
                "title": slug.replace("_", " ").title(),
                "lat": None, "lng": None, "snippet": "",
            })

    return render(request, "city_walks_app/walk.html", {
        "walk": walk,
        "route_json": json.dumps(walk.route),
        "waypoints_json": json.dumps(waypoints_data),
        "waypoints": waypoints_data,
    })


def walk_gpx(request, path):
    walk = load_walk(path)
    if not walk:
        raise Http404

    # Load waypoint details for GPX waypoints
    wpts = []
    for slug in walk.waypoints:
        poi = _load_poi(f"{walk.city_path}/{slug}")
        if poi:
            lat = poi.latitude or None
            lng = poi.longitude or None
            desc = poi.meta.get("snippet") or (poi.body[:200].strip() if poi.body else "")
            wpts.append({"title": poi.title, "lat": lat, "lng": lng, "desc": desc})

    plain_body = re.sub(r"<[^>]+>", "", walk.body).strip()
    stops_text = "\n".join(
        f"{i+1}. {w['title']}" + (f" — {w['desc']}" if w.get("desc") else "")
        for i, w in enumerate(wpts)
    )
    full_desc = (plain_body[:400] + "\n\n" if plain_body else "") + stops_text

    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "World66 City Walks",
        "xmlns": "http://www.topografix.com/GPX/1/1",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": (
            "http://www.topografix.com/GPX/1/1 "
            "http://www.topografix.com/GPX/1/1/gpx.xsd"
        ),
    })
    meta_el = ET.SubElement(gpx, "metadata")
    ET.SubElement(meta_el, "name").text = walk.title
    if full_desc:
        ET.SubElement(meta_el, "desc").text = full_desc

    # Waypoints
    for w in wpts:
        if w["lat"] and w["lng"]:
            wpt = ET.SubElement(gpx, "wpt", {"lat": str(w["lat"]), "lon": str(w["lng"])})
            ET.SubElement(wpt, "name").text = w["title"]
            if w.get("desc"):
                ET.SubElement(wpt, "desc").text = w["desc"]

    # Track
    if walk.route:
        trk = ET.SubElement(gpx, "trk")
        ET.SubElement(trk, "name").text = walk.title
        seg = ET.SubElement(trk, "trkseg")
        for pt in walk.route:
            ET.SubElement(seg, "trkpt", {"lat": str(pt[0]), "lon": str(pt[1])})

    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        gpx, encoding="unicode"
    ).encode("utf-8")
    slug = path.split("/")[-1]
    response = HttpResponse(xml_bytes, content_type="application/gpx+xml")
    response["Content-Disposition"] = f'attachment; filename="{slug}.gpx"'
    return response
