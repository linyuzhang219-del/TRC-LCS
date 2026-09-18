import numpy as np

from tools.convert_kitti_poses_to_tum import rotation_matrix_to_quaternion


def test_identity_rotation_converts_to_identity_quaternion():
    q = rotation_matrix_to_quaternion(np.eye(3))
    assert np.allclose(q, [0.0, 0.0, 0.0, 1.0])
