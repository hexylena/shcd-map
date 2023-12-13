#!/usr/bin/env python
import json
import yaml
with open('sw.yaml', 'r') as handle:
    y = yaml.safe_load(handle)

directory = {}
with open('directory.tsv', 'r') as handle:
    d = []
    for row in [l.strip().split('\t') for l in handle.readlines()]:
        if row[0] == 'NAME': continue

        # print(row)
        k, v = row[0:2]
        category = 'Residential'
        if len(row) > 4 and len(row[4]) > 0:
            category = row[4].title()

        if v not in directory:
            directory[v] = []

        directory[v].append((category, k))

for k, v in directory.items():
    directory[k] = list(set(v))

geojson = {}
geojson['type'] = 'FeatureCollection'
geojson['features'] = []

for k, v in y.items():
    feature = {}
    feature['type'] = 'Feature'

    ref = f'{k}SW'
    feature['properties'] = {}
    feature['properties']['name'] = ref
    feature['properties']['district'] = 'SW'
    residents = directory.get(ref, [])
    feature['properties']['amenity'] = list(set([r[0] for r in residents]))
    feature['properties']['residents'] = list(set([r[1] for r in residents]))
    feature['properties']['pairs'] = residents
    grouped = {
        k: [r[1] for r in residents if r[0] == k]
        for k in set([r[0] for r in residents])
    }
    feature['properties']['html'] = ''.join([
        f'<b>{k2}</b>: <ul><li>{"</li><li>".join(v2)}</li></ul>'
        for k2, v2 in grouped.items()
    ])
    feature['properties']['search'] = f"{k}SW SW{k} "
    for k2, v2 in grouped.items():
        feature['properties']['search'] += f'{k2} {", ".join(v2)} '

    feature['properties']['key'] = k

    feature['geometry'] = {}
    feature['geometry']['type'] = 'Point'
    feature['geometry']['coordinates'] = [*v['p'][::-1]]

    geojson['features'].append(feature)

with open('sw.geojson', 'w') as handle:
    json.dump(geojson, handle)

with open('sw.geojson.js', 'w') as handle:
    handle.write('const SW = ')
    json.dump(geojson, handle)
