import logging

import numpy as np
import numpy.linalg
from scipy.sparse import linalg as splinalg

from ferret_scan.engine.calibration.calibration import CalibrationCancel
from ferret_scan.engine.calibration.moving_calibration import MovingCalibration
from ferret_scan.util.mesh_loaders import ply
from ferret_scan.util.model import Mesh

logger = logging.getLogger(__name__)


class LaserTriangulationError(Exception):
    def __init__(self):
        Exception.__init__(self, 'LaserTriangulationError')


class LaserTriangulation(MovingCalibration):
    """Laser triangulation algorithm:

    - Laser coordinates matrix
    - Pattern's origin
    - Pattern's normal
    """

    def __init__(self, calibration_data=None):
        from ferret_scan.engine.calibration.calibration_data import calibration_data as _calibration_data

        self.calibration_data = calibration_data if calibration_data is not None else _calibration_data

        self.image = None
        self.points_image = None
        self.has_image = False

        self._point_cloud = {}
        self.calibration_num = 0

        self.continue_calibration = False
        MovingCalibration.__init__(self)

    def _initialize(self):
        self.image = None
        self.has_image = True
        self.image_capture.stream = False
        self.calibration_num += 1
        if not self.continue_calibration:
            self.points_image = None
            self._point_cloud = {}
            self.calibration_num = 0
        self.continue_calibration = False

    def read_profile(self):
        MovingCalibration.read_profile(self)

    def _capture(self, angle):
        self.image_capture.stream = False
        image = self.image_capture.capture_pattern()
        pose = self.image_detection.detect_pose(image, False)
        plane = self.image_detection.detect_pattern_plane(pose)
        if plane is not None:
            distance, normal, corners = plane

            if self.points_image is None:
                self.points_image = np.zeros(image.shape, dtype='uint8')
            self.image = np.copy(self.points_image)
            colors = [(255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255)]

            images = self.image_capture.capture_lasers()[:-1]
            for i, image in enumerate(images):
                if image is not None:
                    image = self.image_detection.pattern_mask(image, corners)
                    np.maximum(self.image, image, out=self.image)

                    points_2d, image = self.laser_segmentation.compute_2d_points(image)
                    if len(points_2d[0]) > 0:
                        points_3d = self.point_cloud_generation.compute_camera_point_cloud(points_2d, distance, normal)
                        self._point_cloud.setdefault(i, Mesh(None)._prepare_vertex_count(100)).add_pointcloud(
                            points_3d.T,
                            [colors[i]] * len(points_3d[0]),
                            (self.calibration_num, int(angle / self.motor_step), np.deg2rad(angle)),
                        )
                        self.points_image[points_2d[1], np.rint(points_2d[0]).astype(int)] = colors[i]

                    # test line detection: draw 3D points back on image
                    """
                    if points_3d.shape[1]>0:
                        p, jac = cv2.projectPoints(np.float32(points_3d.T),
                            np.identity(3),
                            np.zeros(3),
                            self.calibration_data.camera_matrix,
                            self.calibration_data.distortion_vector)
                        p.reshape(-1,2)
                        for pp in p.astype(np.int):
                            self.image[pp[0][1], pp[0][0]] = [255,0,0]
                    """
        else:
            self.image = image

    def _calibrate(self):
        self.has_image = False
        self.image_capture.stream = True

        # Save point clouds
        for i, mesh in self._point_cloud.items():
            ply.save_scene('laser_triangulation' + str(i) + '.ply', self._point_cloud[i])

        self.planes = {}

        # Compute planes
        for i, mesh in self._point_cloud.items():
            if self._is_calibrating:
                # distance, normal, std
                self.planes[i] = compute_plane(i, mesh.get_vertexes())

        if self._is_calibrating:
            if all(np.array(list(self.planes.values()))[:, 2] < 1.0) and all(
                np.array(list(self.planes.values()))[:, 0]
            ):
                response = (True, (self.planes, self._point_cloud))
            else:
                response = (False, LaserTriangulationError())
        else:
            response = (False, CalibrationCancel())

        self._is_calibrating = False
        self.image = None

        return response

    def accept(self):
        for i, p in self.planes.items():
            self.calibration_data.laser_planes[i].distance = p[0]
            self.calibration_data.laser_planes[i].normal = p[1]


# ========================================================


def compute_plane(index, X):
    if X is not None and X.shape[0] > 3:
        model, inliers = ransac(X, PlaneDetection(), 3, 0.1)

        distance, normal, M = model
        std = np.dot(M.T, normal).std()

        logger.info('Laser calibration ' + str(index))
        logger.info(' Distance: ' + str(distance))
        logger.info(' Normal: ' + str(normal))
        logger.info(' Standard deviation: ' + str(std))
        logger.info(' Point cloud size: ' + str(len(inliers)))

        return distance, normal, std
    else:
        return None, None, None


# ========================================================


class PlaneDetection:
    def fit(self, X):
        M, Xm = self._compute_m(X)
        # U = linalg.svds(M, k=2)[0]
        # normal = np.cross(U.T[0], U.T[1])

        # slower but fit in memory
        U = splinalg.svds(M, k=2)[0]
        normal = np.cross(U.T[0], U.T[1])

        # faster but need a lot of memory
        # normal = numpy.linalg.svd(M)[0][:, 2]

        # save memory enough to fit but.... is this ok?
        # normal = numpy.linalg.svd(M, full_matrices= False)[0][:, 2]

        if normal[2] < 0:
            normal *= -1
        dist = np.dot(normal, Xm)
        return dist, normal, M

    def residuals(self, model, X):
        _, normal, _ = model
        M, Xm = self._compute_m(X)
        return np.abs(np.dot(M.T, normal))

    def is_degenerate(self, sample):
        return False

    def _compute_m(self, X):
        n = X.shape[0]
        Xm = X.sum(axis=0) / n
        M = np.array(X - Xm).T
        return M, Xm


# ========================================================


def ransac(data, model_class, min_samples, threshold, max_trials=500):
    best_model = None
    best_inlier_num = 0
    best_inliers = None
    data_idx = np.arange(data.shape[0])
    for _ in range(max_trials):
        sample = data[np.random.randint(0, data.shape[0], 3)]
        if model_class.is_degenerate(sample):
            continue
        sample_model = model_class.fit(sample)
        sample_model_residua = model_class.residuals(sample_model, data)
        sample_model_inliers = data_idx[sample_model_residua < threshold]
        inlier_num = sample_model_inliers.shape[0]
        if inlier_num > best_inlier_num:
            best_inlier_num = inlier_num
            best_inliers = sample_model_inliers
    if best_inliers is not None:
        best_model = model_class.fit(data[best_inliers])
    return best_model, best_inliers
