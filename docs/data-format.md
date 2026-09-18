# Data formats

## Image directory

Images are read in lexicographic order. Use zero-padded filenames when numeric order matters, for example `000001.png`.

## TUM-style trajectory

One row per image/keyframe:

```text
timestamp tx ty tz qx qy qz qw
```

v0.1.0 assumes row alignment between sorted images and trajectory rows. Timestamp association/interpolation is intentionally left to dataset/backend adapters.

## Semantic JSONL

One JSON object per line. Required field: `frame_id`. Other fields are optional.

```json
{
  "frame_id": 12,
  "image": "000012.png",
  "region": "living room",
  "objects": [
    {
      "label": "bag",
      "attrs": ["black"],
      "bbox": [120, 160, 80, 60],
      "xyz": [1.2, 0.1, 3.4],
      "score": 0.91
    }
  ],
  "relations": [
    {"subj": "bag", "rel": "near", "obj": "red chair"}
  ]
}
```

### Objects

- `label`: object/category text.
- `attrs`: optional attributes.
- `bbox`: optional `[x, y, width, height]` in pixels.
- `xyz`: optional 3D position in a consistent coordinate frame.
- `score`: optional detector confidence; defaults to 1.0.

### Relations

Relations are symbolic triples `subj-rel-obj`. If no relations are supplied but multiple objects have `xyz`, v0.1.0 can infer symmetric `near` relations for close pairs.
