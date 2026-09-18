# Public-dataset integration

TRC-LCS does not redistribute third-party datasets. Always follow each dataset's license and citation requirements.

## KITTI odometry

A practical workflow is:

1. Use a KITTI sequence image directory as ordered keyframes, or export keyframes from your SLAM frontend.
2. Convert KITTI pose matrices into the row-aligned TUM representation expected by TRC-LCS:

```bash
python tools/convert_kitti_poses_to_tum.py \
  --poses /path/to/poses/00.txt \
  --times /path/to/sequences/00/times.txt \
  --out data/kitti00_trajectory_tum.txt
```

3. Produce optional semantic JSONL from your detector/segmenter.
4. Run `trc-lcs` with camera intrinsics matching the image stream.

Do not treat ground-truth poses as an online SLAM estimate when measuring a scheduling method's practical localization gain. Record whether the supplied trajectory is ground truth, estimated, or post-processed.

## TUM RGB-D

TUM trajectories already use a closely related pose convention, but the RGB frames and trajectory are not necessarily row aligned. Create an associated, ordered keyframe subset first, then write one pose row per exported keyframe.

## Existing SLAM systems

The most faithful integration is often to export:

- keyframe image,
- keyframe timestamp,
- current pose estimate,
- optional covariance/uncertainty,
- optional semantic observations.

TRC-LCS then returns prioritized/verified loop pairs. The host SLAM backend remains responsible for pose-graph insertion and optimization.
