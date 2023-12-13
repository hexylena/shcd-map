#!/usr/bin/env python
import json
import yaml
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



for region in ('sw', 'se'):
    print(region)
    with open(f'{region}.yaml', 'r') as handle:
        y = yaml.safe_load(handle)


    geojson = {}
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = []

    for k, v in y.items():
        feature = {}
        feature['type'] = 'Feature'

        ref = f'{k}{region.upper()}'
        feature['properties'] = {}
        feature['properties']['name'] = ref
        feature['properties']['district'] = region.upper()
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
        feature['properties']['search'] = f"{k}{region.upper()} {region.upper()}{k} "
        for k2, v2 in grouped.items():
            feature['properties']['search'] += f'{k2} {", ".join(v2)} '

        feature['properties']['key'] = k

        feature['geometry'] = {}
        feature['geometry']['type'] = 'Point'
        feature['geometry']['coordinates'] = [*v['p'][::-1]]

        geojson['features'].append(feature)

    with open(f'{region}.geojson', 'w') as handle:
        json.dump(geojson, handle)

    with open(f'{region}.geojson.js', 'w') as handle:
        handle.write(f'const {region.upper()} = ')
        json.dump(geojson, handle)
