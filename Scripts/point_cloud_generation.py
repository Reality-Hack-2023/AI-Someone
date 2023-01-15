import os

import numpy as np
import open3d as o3d
import cv2


def get_translation_t(t):
    """Get the translation matrix for movement in t."""
    matrix = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, t],
        [0, 0, 0, 1],
    ]
    return np.array(matrix, dtype=np.float32)


def get_rotation_phi(phi):
    """Get the rotation matrix for movement in phi."""
    matrix = [
        [1, 0, 0, 0],
        [0, np.cos(phi), -np.sin(phi), 0],
        [0, np.sin(phi), np.cos(phi), 0],
        [0, 0, 0, 1],
    ]
    return np.array(matrix, dtype=np.float32)


def get_rotation_theta(theta):
    """Get the rotation matrix for movement in theta."""
    matrix = [
        [np.cos(theta), 0, -np.sin(theta), 0],
        [0, 1, 0, 0],
        [np.sin(theta), 0, np.cos(theta), 0],
        [0, 0, 0, 1],
    ]
    return np.array(matrix, dtype=np.float32)


def pose_spherical(theta, phi, t):
    """
    Get the camera-to-world matrix for the corresponding theta, phi,
    and t.
    """
    c2w = get_translation_t(t)
    c2w = get_rotation_phi(phi / 180.0 * np.pi) @ c2w
    c2w = get_rotation_theta(theta / 180.0 * np.pi) @ c2w
    c2w = np.array([[-1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]) @ c2w
    return c2w


def get_mesh(rgbd_image, im, transform=None):
    if transform is None:
        transform = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    print(rgbd_image)

    size = im.shape
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image,
        o3d.camera.PinholeCameraIntrinsic(
            width=im.shape[1], height=im.shape[0], fx=focal_length, fy=focal_length, cx=center[0], cy=center[1])
    )
    # Flip it, otherwise the pointcloud will be upside down.
    R = pcd.get_rotation_matrix_from_xyz((0, 0, -np.pi / 2), )
    pcd.rotate(R)
    pcd.transform(transform)
    downpcd = pcd.voxel_down_sample(voxel_size=0.01)
    radii = [0.005, 0.01, 0.02, 0.04]
    downpcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector(radii))

    return rec_mesh


def create_depth_image(color_folder, depth_folder, image_name):
    color_raw = o3d.io.read_image(f"{color_folder}/{image_name}")
    depth_raw = o3d.io.read_image(f"{depth_folder}/{image_name}")
    im = cv2.imread(f"{color_folder}/{image_name}")

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color_raw, depth_raw, depth_scale=50000,
                                                                    convert_rgb_to_intensity=False, depth_trunc=5)
    return rgbd_image, im


def create_scene_mesh(color_folder, depth_folder, output_folder):
    images = os.listdir(color_folder)
    images.remove('background_0.png')
    cnt = 1
    meshes = []
    step = 180 / len(images)
    phi = 0
    print(step)
    mesh_combined = o3d.geometry.TriangleMesh()
    for i in images:
        transform_matrix = pose_spherical(0, -90 + phi, -3)
        rgbd_image, im = create_depth_image(color_folder, depth_folder, i)
        mesh = get_mesh(rgbd_image, im, transform_matrix)
        meshes.append(mesh)
        mesh_combined += mesh
        phi += step
        cnt += 1

    R = mesh_combined.get_rotation_matrix_from_xyz((0, 0, np.pi / 2))
    mesh_combined.rotate(R, center=(0, 0, 0))
    o3d.io.write_triangle_mesh(os.path.join(output_folder, "fragment.gltf"), mesh_combined)

# print(create_scene_mesh('images', 'output', ""))
