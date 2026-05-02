# City Walks

A standalone Django app for browsing and downloading curated walking routes in cities around the world. Each walk has a map, a list of stops, a narrative description, and a GPX download.

## What it is

City Walks reads walk content from the `content/` directory. Each walk is a markdown file with YAML frontmatter containing `type: walk`, a `route` (list of `[lat, lng]` points), and a `waypoints` list of POI slugs in the same city directory.

## Running locally

```bash
pip install -r requirements.txt
python manage.py runserver
```

Then open http://localhost:8000/.

To compile a fresh `requirements.txt` from `requirements.in`:

```bash
pip install uv
uv pip compile requirements.in -o requirements.txt
```

## Adding walk content

Walk content lives in `content/` following the same hierarchy as the World66 travel guide:

```
content/
  europe/
    netherlands/
      amsterdam/
        jordaan_walk.md       # type: walk
        anne_frank_house.md   # type: poi  (a waypoint)
```

A minimal walk file looks like:

```yaml
---
title: Jordaan Walk
type: walk
latitude: 52.374
longitude: 4.884
waypoints:
  - anne_frank_house
  - westerkerk
route:
  - [52.375, 4.882]
  - [52.374, 4.886]
  - [52.372, 4.890]
---

A stroll through Amsterdam's most charming neighbourhood.
```

POI files referenced in `waypoints` should have `latitude`, `longitude`, and optionally a `snippet` field for the stop description.
