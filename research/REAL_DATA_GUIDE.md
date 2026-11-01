# Replacing schematic comparison with physical railway geometry

**Status (v4 audit):** A **source-derived 0.2° railway occupancy raster** IS bundled and used in the reported spatial-proximity figures. The full-resolution track alignment GeoJSON is **not bundled** and its direct high-precision comparison was **not executed**. v3 network-length, detour, and damage metrics remain independent of the GIS. The original version’s “real corridors” were schematic; do not mistake them for mapped railway geometry.

## Provenance-checked source options

- **Indian rail lines, stations and related GIS**: India Geodata's railway section: https://yashveeeeeeer.github.io/india-geodata/ (Indian Railways → dataset release). The portal describes track lines from IR GeoPortal, Survey of India, GatiShakti and Bhuvan. Confirm each release asset's file format, geographic coverage, date, accuracy, and license. It may require conversion from Parquet or zipped GeoJSONL to plain GeoJSON/GeoJSONL.
- **OpenStreetMap railways**: https://download.geofabrik.de/asia/india.html — extract features tagged as railway tracks from OSM PBF; attribute **© OpenStreetMap contributors, ODbL** and note feature completeness and date. Full extract is large.
- **DataMeet/railways**: https://github.com/datameet/railways — useful for *station locations* and schedules, but train-route GeoJSON lines may connect **station stops**, not surveyed physical tracks. **Do not feed these into the track-comparison script.** The script rejects any single jump longer than 250 km, but shorter stop-to-stop jumps can still pass, so manual provenance QA is required.
- **Boundary polygons**: https://www.geoboundaries.org/api.html (gbOpen/IND/ADM0, CC BY 4.0) or simplified `geoBoundaries-IND-ADM0_simplified.geojson` in https://github.com/srisbalyan/India-Administrative-Maps. These geometries are not part of current simulation inputs. Source choice may affect disputed areas; document your decision.

## Run once you have *actual lines*

1. Save railway track LINESTRING GeoJSON as `data/rail_tracks.geojson` (or .geojsonl). Inspect several randomly chosen features to confirm that consecutive coordinates follow actual tracks rather than stopping stations or timetable routes.
2. Check CRS **EPSG:4326 longitude, latitude** and note data vintage, license and extraction method.
3. Run:

```bash
python research/compare_real_tracks.py --tracks data/rail_tracks.geojson --out out/real_rail_metrics.json --tolerance-km 50
```

This produces **geodesic length-weighted proximity** in both directions. The comparison deliberately does *not* claim comparable transport efficiency because a countrywide rail map is far larger than a 16-terminal design. It does not solve railway graph topology, match demand, deduplicate parallel tracks, or guarantee city connections are on actual tracks. If the source line features are duplicates, rail length and proximity weights may also be duplicated.

**The LinkedIn publication gate:** Do not claim the model reproduces, approximates, or improves Indian Railways until physical alignment data are inspected and an appropriate *route-level* comparison is designed. The current results are legitimate for a mathematical toy network with Indian city coordinates and stylized terrain penalties.
