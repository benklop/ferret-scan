import logging
import os

import numpy as np

from ferret_scan.settings.persistence import default_libferret_root
from ferret_scan.settings.schema import Setting
from ferret_scan.util import resources

logger = logging.getLogger(__name__)


def _default_libferret_root():
    try:
        return default_libferret_root()
    except RuntimeError:
        return ''


def _default_platform_mesh_path():
    try:
        for name in ('ferret_platform.stl', 'Gryphon_platform.stl', 'ciclop_platform.stl'):
            path = resources.get_path_for_mesh(name)
            if os.path.isfile(path):
                return str(path)
        return str(resources.get_path_for_mesh('ferret_platform.stl'))
    except (AssertionError, OSError):
        return 'ferret_platform.stl'


def _(n):
    return n


def register_ferret_settings(settings):
    # ============== CONNECTION Preferences ========

    settings._add_setting(Setting('serial_name', _('Serial name'), 'preferences', str, ''))
    settings._add_setting(
        Setting(
            'baud_rate',
            _('Baud rate'),
            'preferences',
            int,
            115200,
            possible_values=(9600, 14400, 19200, 38400, 57600, 115200),
        )
    )
    settings._add_setting(Setting('camera_id', _('Camera ID'), 'preferences', str, ''))
    from ferret_scan.diy import diy_available

    _scanner_modes = ('Ferret structured light',)
    if diy_available():
        _scanner_modes = ('Ciclop laser', 'Ferret structured light')
    settings._add_setting(
        Setting(
            'scanner_mode',
            _('Scanner mode'),
            'preferences',
            str,
            'Ferret structured light',
            possible_values=_scanner_modes,
            tooltip=_('Ciclop: webcam + line lasers. Ferret: CR-Scan Ferret depth/RGB-D.'),
        )
    )
    settings._add_setting(
        Setting(
            'ferret_libferret_root',
            _('libferret path'),
            'preferences',
            str,
            _default_libferret_root(),
            tooltip=_('Path to libferret (submodule or clone with OrbbecSDK_v2).'),
        )
    )
    from ferret_scan.revolve import revolve_available

    _turntable_backends = ['None']
    _default_turntable = 'None'
    if revolve_available():
        _turntable_backends.append('Revopoint DAT')
        _default_turntable = 'Revopoint DAT'
    if diy_available():
        _turntable_backends.append('GRBL (Ciclop)')
        if _default_turntable == 'None':
            _default_turntable = 'GRBL (Ciclop)'
    settings._add_setting(
        Setting(
            'turntable_backend',
            _('Turntable'),
            'preferences',
            str,
            _default_turntable,
            possible_values=tuple(_turntable_backends),
            tooltip=_('Revopoint DAT: Bluetooth dual-axis table. GRBL: Ciclop serial board.'),
        )
    )
    settings._add_setting(
        Setting(
            'revolve_device_address',
            _('Revopoint BLE address'),
            'preferences',
            str,
            '',
            tooltip=_('MAC address from revolve scan, or empty for auto-select.'),
        )
    )
    settings._add_setting(
        Setting(
            'ferret_turntable_optional',
            _('Turntable optional (Ferret)'),
            'preferences',
            bool,
            True,
            tooltip=_('Allow Ferret connect when the turntable is absent (manual rotation).'),
        )
    )
    settings._add_setting(
        Setting(
            'board',
            _('Board'),
            'preferences',
            str,
            'BT ATmega328',
            possible_values=('Arduino Uno', 'BT ATmega328'),
        )
    )
    settings._add_setting(
        Setting('firmware_string', 'Firmware version string', 'preferences', str, "Ferret Scan ['$' for help]")
    )
    settings._add_setting(Setting('init_string', 'Board init string', 'preferences', str, ''))
    settings._add_setting(Setting('invert_motor', _('Invert motor'), 'preferences', bool, False))
    settings._add_setting(
        Setting(
            'language',
            _('Language'),
            'preferences',
            str,
            'English',
            possible_values=('English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português'),
            tooltip=_('Change the application language. Switching language requires a restart.'),
        )
    )

    # ========== Camera profiles ===========
    # Hack to translate combo boxes:
    _('Very high')
    _('High')
    _('Medium')
    _('Low')

    # ------- Control -----------
    settings._add_setting(
        Setting(
            'luminosity',
            _('Luminosity'),
            'profile_settings',
            str,
            'Medium',
            possible_values=('High', 'Medium', 'Low'),
        )
    )
    settings._add_setting(
        Setting('brightness_control', _('Brightness'), 'profile_settings', int, 128, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('contrast_control', _('Contrast'), 'profile_settings', int, 32, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('saturation_control', _('Saturation'), 'profile_settings', int, 32, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('exposure_control', _('Exposure'), 'profile_settings', int, 16, min_value=1, max_value=64)
    )
    settings._add_setting(
        Setting('light1_control', _('Lamp 1 brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('light2_control', _('Lamp 2 brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )

    # -------- Calibration --------
    settings._add_setting(
        Setting(
            'brightness_pattern_calibration',
            _('Brightness'),
            'profile_settings',
            int,
            128,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting('contrast_pattern_calibration', _('Contrast'), 'profile_settings', int, 32, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting(
            'saturation_pattern_calibration',
            _('Saturation'),
            'profile_settings',
            int,
            32,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting('exposure_pattern_calibration', _('Exposure'), 'profile_settings', int, 16, min_value=1, max_value=64)
    )
    settings._add_setting(
        Setting(
            'light1_pattern_calibration',
            _('Lamp 1 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting(
            'light2_pattern_calibration',
            _('Lamp 2 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )

    settings._add_setting(
        Setting('brightness_laser_calibration', _('Brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('contrast_laser_calibration', _('Contrast'), 'profile_settings', int, 100, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting(
            'saturation_laser_calibration',
            _('Saturation'),
            'profile_settings',
            int,
            100,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting('exposure_laser_calibration', _('Exposure'), 'profile_settings', int, 8, min_value=1, max_value=64)
    )
    settings._add_setting(
        Setting(
            'light1_laser_calibration',
            _('Lamp 1 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting(
            'light2_laser_calibration',
            _('Lamp 2 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )

    settings._add_setting(
        Setting('remove_background_calibration', _('Remove background'), 'profile_settings', bool, True)
    )

    # ------- Scanning ------
    settings._add_setting(
        Setting(
            'brightness_texture_scanning', _('Brightness'), 'profile_settings', int, 128, min_value=0, max_value=255
        )
    )
    settings._add_setting(
        Setting('contrast_texture_scanning', _('Contrast'), 'profile_settings', int, 32, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('saturation_texture_scanning', _('Saturation'), 'profile_settings', int, 50, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('exposure_texture_scanning', _('Exposure'), 'profile_settings', int, 16, min_value=1, max_value=64)
    )
    settings._add_setting(
        Setting(
            'light1_texture_scanning',
            _('Lamp 1 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )
    settings._add_setting(
        Setting(
            'light2_texture_scanning',
            _('Lamp 2 brightness'),
            'profile_settings',
            int,
            0,
            min_value=0,
            max_value=255,
        )
    )

    settings._add_setting(
        Setting('brightness_laser_scanning', _('Brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('contrast_laser_scanning', _('Contrast'), 'profile_settings', int, 100, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('saturation_laser_scanning', _('Saturation'), 'profile_settings', int, 100, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('exposure_laser_scanning', _('Exposure'), 'profile_settings', int, 8, min_value=1, max_value=64)
    )
    settings._add_setting(
        Setting('light1_laser_scanning', _('Lamp 1 brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )
    settings._add_setting(
        Setting('light2_laser_scanning', _('Lamp 2 brightness'), 'profile_settings', int, 0, min_value=0, max_value=255)
    )

    settings._add_setting(Setting('remove_background_scanning', _('Remove background'), 'profile_settings', bool, True))

    # ============ Video flush profiles ==============
    # [ texture, laser, pattern, change mode ]
    # - Linux
    settings._add_setting(
        Setting(
            'flush_linux',
            'Flush Linux',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([3, 2, 3, 0])),
        )
    )
    settings._add_setting(
        Setting(
            'flush_stream_linux',
            'Flush stream Linux',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([0, 3, 3, 0])),
        )
    )
    # - Darwin
    settings._add_setting(
        Setting(
            'flush_darwin',
            'Flush Darwin',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([4, 3, 4, 0])),
        )
    )
    settings._add_setting(
        Setting(
            'flush_stream_darwin',
            'Flush stream Darwin',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([0, 3, 3, 0])),
        )
    )
    # - Windows
    settings._add_setting(
        Setting(
            'flush_windows',
            'Flush Windows',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([4, 3, 4, 0])),
        )
    )
    settings._add_setting(
        Setting(
            'flush_stream_windows',
            'Flush stream Windows',
            'preferences',
            np.ndarray,
            np.ndarray(shape=(4,), dtype=int, buffer=np.array([0, 3, 3, 0])),
        )
    )

    # ========== Segmentation profiles ===========

    # -------- Calibration --------
    settings._add_setting(
        Setting(
            'laser_color_detector_calibration',
            _('Laser color detector'),
            'profile_settings',
            str,
            'R (HSV)',
            possible_values=('R (RGB)', 'G (RGB)', 'B (RGB)', 'R (HSV)', 'Cr (YCrCb)', 'U (YUV)'),
        )
    )
    settings._add_setting(
        Setting('threshold_enable_calibration', _('Enable threshold'), 'profile_settings', bool, True)
    )
    settings._add_setting(
        Setting('threshold_value_calibration', _('Threshold'), 'profile_settings', int, 50, min_value=0, max_value=255)
    )
    settings._add_setting(Setting('blur_enable_calibration', _('Enable blur'), 'profile_settings', bool, False))
    settings._add_setting(
        Setting('blur_value_calibration', _('Blur'), 'profile_settings', int, 2, min_value=0, max_value=10)
    )
    settings._add_setting(Setting('window_enable_calibration', _('Enable window'), 'profile_settings', bool, True))
    settings._add_setting(
        Setting('window_value_calibration', _('Window'), 'profile_settings', int, 5, min_value=0, max_value=30)
    )
    settings._add_setting(
        Setting(
            'refinement_calibration',
            _('Refinement'),
            'profile_settings',
            str,
            'RANSAC',
            possible_values=('None', 'SGF', 'RANSAC'),
        )
    )

    # -------- Scanning --------
    settings._add_setting(
        Setting(
            'laser_color_detector_scanning',
            _('Laser color detector'),
            'profile_settings',
            str,
            'R (HSV)',
            possible_values=('R (RGB)', 'G (RGB)', 'B (RGB)', 'R (HSV)', 'Cr (YCrCb)', 'U (YUV)'),
        )
    )
    settings._add_setting(Setting('threshold_enable_scanning', _('Enable threshold'), 'profile_settings', bool, True))
    settings._add_setting(
        Setting('threshold_value_scanning', _('Threshold'), 'profile_settings', int, 50, min_value=0, max_value=255)
    )
    settings._add_setting(Setting('blur_enable_scanning', _('Enable blur'), 'profile_settings', bool, True))
    settings._add_setting(
        Setting('blur_value_scanning', _('Blur'), 'profile_settings', int, 2, min_value=0, max_value=10)
    )
    settings._add_setting(Setting('window_enable_scanning', _('Enable window'), 'profile_settings', bool, True))
    settings._add_setting(
        Setting('window_value_scanning', _('Window'), 'profile_settings', int, 8, min_value=0, max_value=30)
    )
    settings._add_setting(
        Setting(
            'refinement_scanning',
            _('Refinement'),
            'profile_settings',
            str,
            'SGF',
            possible_values=('None', 'SGF'),
        )
    )

    # ==================== CONTROL workbench ================

    settings._add_setting(
        Setting(
            'current_panel_control',
            'camera_control',
            'profile_settings',
            str,
            'camera_control',
            possible_values=('camera_control', 'laser_control', 'ldr_value', 'motor_control', 'gcode_control'),
        )
    )

    settings._add_setting(
        Setting('frame_rate', _('Frame rate'), 'profile_settings', int, 30, possible_values=(30, 25, 20, 15, 10, 5))
    )

    settings._add_setting(Setting('motor_step_control', _('Step (º)'), 'profile_settings', float, 90.0))
    settings._add_setting(
        Setting(
            'motor_speed_control',
            _('Speed (º/s)'),
            'profile_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )
    settings._add_setting(
        Setting(
            'motor_acceleration_control',
            _('Acceleration (º/s²)'),
            'profile_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )

    settings._add_setting(Setting('save_image_button', _('Save image'), 'no_settings', str, ''))
    settings._add_setting(Setting('left_button', _('Left'), 'no_settings', str, ''))
    settings._add_setting(Setting('right_button', _('Right'), 'no_settings', str, ''))
    settings._add_setting(Setting('move_button', _('Move'), 'no_settings', str, ''))
    settings._add_setting(Setting('enable_button', _('Enable'), 'no_settings', str, ''))
    settings._add_setting(Setting('reset_origin_button', _('Reset origin'), 'no_settings', str, ''))
    settings._add_setting(Setting('gcode_gui', _('Send'), 'no_settings', str, ''))
    settings._add_setting(Setting('ldr_value', _('Send'), 'no_settings', str, ''))

    # ==================== ADJUSTMENT workbench ================

    settings._add_setting(
        Setting(
            'current_panel_adjustment',
            'scan_capture',
            'profile_settings',
            str,
            'scan_capture',
            possible_values=(
                'scan_capture',
                'scan_segmentation',
                'calibration_capture',
                'calibration_segmentation',
            ),
        )
    )

    settings._add_setting(
        Setting(
            'current_video_mode_adjustment',
            'Texture',
            'profile_settings',
            str,
            'Texture',
            possible_values=('Texture', 'Pattern', 'Laser', 'Gray'),
        )
    )

    settings._add_setting(
        Setting(
            'capture_mode_scanning',
            _('Capture mode'),
            'profile_settings',
            str,
            'Texture',
            possible_values=('Texture', 'Laser'),
        )
    )
    settings._add_setting(Setting('draw_line_scanning', _('Draw line'), 'profile_settings', bool, True))

    settings._add_setting(
        Setting(
            'capture_mode_calibration',
            _('Capture mode'),
            'profile_settings',
            str,
            'Pattern',
            possible_values=('Pattern', 'Laser'),
        )
    )
    settings._add_setting(Setting('draw_line_calibration', _('Draw line'), 'profile_settings', bool, True))

    # ==================== CALIBRATION workbench ================

    settings._add_setting(
        Setting(
            'current_panel_calibration',
            'pattern_settings',
            'profile_settings',
            str,
            'pattern_settings',
            possible_values=(
                'pattern_settings',
                'camera_intrinsics',
                'scanner_autocheck',
                'rotating_platform_settings',
                'laser_triangulation',
                'platform_extrinsics',
                'video_settings',
            ),
        )
    )  # , u'cloud_correction')))

    # ----- Pattern Settings ---------
    settings._add_setting(
        Setting('pattern_rows', _('Pattern rows'), 'calibration_settings', int, 6, min_value=2, max_value=50)
    )
    settings._add_setting(
        Setting('pattern_columns', _('Pattern columns'), 'calibration_settings', int, 11, min_value=2, max_value=50)
    )
    settings._add_setting(
        Setting('pattern_square_width', _('Square width (mm)'), 'calibration_settings', float, 13.0, min_value=1.0)
    )
    settings._add_setting(
        Setting('pattern_origin_distance', _('Origin distance (mm)'), 'calibration_settings', float, 0.0, min_value=0.0)
    )
    settings._add_setting(
        Setting('pattern_border_l', _('Border Left (mm)'), 'calibration_settings', float, 5.0, min_value=0.0)
    )
    settings._add_setting(
        Setting('pattern_border_r', _('Border Right (mm)'), 'calibration_settings', float, 5.0, min_value=0.0)
    )
    settings._add_setting(
        Setting('pattern_border_t', _('Border Top (mm)'), 'calibration_settings', float, 5.0, min_value=0.0)
    )
    settings._add_setting(
        Setting('pattern_border_b', _('Border Bottom (mm)'), 'calibration_settings', float, 5.0, min_value=0.0)
    )

    # ----- Scanner Autocheck ---------
    settings._add_setting(Setting('autocheck_button', _('Perform autocheck'), 'no_settings', str, ''))

    # ----- Rotating Platform ---------
    settings._add_setting(Setting('motor_step_calibration', _('Step (º)'), 'calibration_settings', float, 4.5))
    settings._add_setting(
        Setting(
            'motor_speed_calibration',
            _('Speed (º/s)'),
            'calibration_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )
    settings._add_setting(
        Setting(
            'motor_acceleration_calibration',
            _('Acceleration (º/s²)'),
            'calibration_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )

    settings._add_setting(
        Setting(
            'after_calibration_position',
            _('Platform position after calibration'),
            'calibration_settings',
            str,
            'Return',
            possible_values=('Keep', 'Return', 'Perpendicular'),
        )
    )

    # ----- Laser Triangulation ---------
    settings._add_setting(Setting('distance_left', _('Distance left (mm)'), 'calibration_settings', float, 0.0))
    settings._add_setting(
        Setting(
            'normal_left',
            _('Normal left'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0])),
        )
    )

    settings._add_setting(Setting('distance_right', _('Distance right (mm)'), 'calibration_settings', float, 0.0))
    settings._add_setting(
        Setting(
            'normal_right',
            _('Normal right'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0])),
        )
    )

    settings._add_setting(Setting('laser_triangulation_hash', '', 'calibration_settings', str, ''))

    settings._add_setting(
        Setting(
            'laser_calibration_angles',
            _('Laser on pattern visibility angle ranges'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(2, 2), buffer=np.array([[-90.0, 90.0], [-90.0, 90.0]])),
        )
    )

    # ----- Platform extrinsics ---------
    settings._add_setting(
        Setting(
            'rotation_matrix',
            _('Rotation matrix'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(3, 3), buffer=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])),
        )
    )
    settings._add_setting(
        Setting(
            'translation_vector',
            _('Translation vector (mm)'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0])),
        )
    )

    settings._add_setting(Setting('platform_extrinsics_hash', '', 'calibration_settings', str, ''))

    # ----- Video settings ---------

    # some cameras like "Lenovo EasyCamera" require to grab frame before update settings
    settings._add_setting(
        Setting(
            'camera_capture_before_set',
            _('Capture a frame right after connect before setting camera'),
            'profile_settings',
            bool,
            False,
        )
    )

    settings._add_setting(
        Setting('camera_width', _('Width'), 'calibration_settings', int, -1, min_value=-1, max_value=10000)
    )
    settings._add_setting(
        Setting('camera_height', _('Height'), 'calibration_settings', int, -1, min_value=-1, max_value=10000)
    )

    settings._add_setting(
        Setting('camera_focus', _('Manual focus'), 'calibration_settings', int, 0, min_value=0, max_value=255)
    )

    settings._add_setting(Setting('camera_rotate', _('Rotate'), 'calibration_settings', bool, True))
    settings._add_setting(Setting('camera_hflip', _('Horizontal flip'), 'calibration_settings', bool, True))
    settings._add_setting(Setting('camera_vflip', _('Vertical flip'), 'calibration_settings', bool, False))
    settings._add_setting(Setting('set_resolution_button', _('Set resolution'), 'no_settings', str, ''))
    settings._add_setting(Setting('auto_resolution', _('Use MAX resolution'), 'no_settings', bool, False))

    # ----- Camera intrinsics ---------
    settings._add_setting(
        Setting(
            'camera_matrix',
            _('Camera matrix'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(3, 3), buffer=np.array([[1430.0, 0.0, 480.0], [0.0, 1430.0, 640.0], [0.0, 0.0, 1.0]])),
        )
    )
    settings._add_setting(
        Setting(
            'distortion_vector',
            _('Distortion vector'),
            'calibration_settings',
            np.ndarray,
            np.ndarray(shape=(5,), buffer=np.array([0.0, 0.0, 0.0, 0.0, 0.0])),
        )
    )

    # new camera calculator
    settings._add_setting(
        Setting(
            'new_camera_matrix',
            _('Initial new camera matrix'),
            'no_settings',
            np.ndarray,
            np.ndarray(shape=(3, 3), buffer=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])),
        )
    )
    settings._add_setting(Setting('new_camera_ruler', _('Target length (mm)'), 'no_settings', float, 325.0))
    settings._add_setting(
        Setting('new_camera_distance_h', _('Target horizontal distance (mm)'), 'no_settings', float, 480.0)
    )
    settings._add_setting(
        Setting('new_camera_distance_v', _('Target vertical distance (mm)'), 'no_settings', float, 265.0)
    )
    settings._add_setting(Setting('apply_new_camera_button', _('Apply calculated camera data'), 'no_settings', str, ''))

    # ==================== SCANNING workbench ================

    settings._add_setting(
        Setting(
            'current_panel_scanning',
            'scan_parameters',
            'profile_settings',
            str,
            'scan_parameters',
            possible_values=(
                'scan_parameters',
                'rotating_platform',
                'point_cloud_roi',
                'point_cloud_color',
                'photogrammetry',
                'mesh_correction',
            ),
        )
    )

    settings._add_setting(Setting('view_scanning_panel', _('View scanning panel'), 'preferences', bool, False))
    settings._add_setting(Setting('view_scanning_video', _('View scanning video'), 'preferences', bool, False))
    settings._add_setting(Setting('view_scanning_scene', _('View scanning scene'), 'preferences', bool, True))

    # Hack to translate combo boxes:
    _('Open')
    _('Enable open')

    # Hack to translate combo boxes:
    _('Texture')
    _('Laser')
    _('Gray')
    _('Line')
    settings._add_setting(
        Setting(
            'video_scanning',
            _('Video'),
            'profile_settings',
            str,
            'Texture',
            possible_values=('Texture', 'Laser', 'Gray', 'Line'),
        )
    )

    # ----------- Scan parameters ----------
    # Hack to translate combo boxes:
    _('Left')
    _('Right')
    _('Both')
    settings._add_setting(
        Setting(
            'use_laser',
            _('Use laser'),
            'profile_settings',
            str,
            'Both',
            possible_values=('Left', 'Right', 'Both'),
        )
    )

    # ----------- Rotating platform ----------
    settings._add_setting(Setting('motor_step_scanning', _('Step (º)'), 'profile_settings', float, 0.45))
    settings._add_setting(
        Setting(
            'motor_speed_scanning',
            _('Speed (º/s)'),
            'profile_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )
    settings._add_setting(
        Setting(
            'motor_acceleration_scanning',
            _('Acceleration (º/s²)'),
            'profile_settings',
            float,
            200.0,
            min_value=1.0,
            max_value=1000.0,
        )
    )

    # ----------- Point cloud ROI ----------
    settings._add_setting(Setting('show_center', _('Show center'), 'profile_settings', bool, True))
    settings._add_setting(Setting('use_roi', _('Use ROI'), 'profile_settings', bool, False))
    settings._add_setting(
        Setting('roi_diameter', _('Diameter (mm)'), 'profile_settings', int, 300, min_value=0, max_value=350)
    )
    settings._add_setting(
        Setting('roi_height', _('Height (mm)'), 'profile_settings', int, 300, min_value=0, max_value=350)
    )

    # ----------- Point cloud color ----------
    settings._add_setting(
        Setting(
            'texture_mode',
            _('Texture'),
            'profile_settings',
            str,
            'Texture',
            possible_values=('Texture', 'Flat color', 'Multi color', 'Capture', 'Laser BG'),
        )
    )

    settings._add_setting(Setting('point_cloud_color', _('Cloud color'), 'profile_settings', list, [170, 170, 170]))
    settings._add_setting(Setting('point_cloud_color_l', _('Left color'), 'profile_settings', list, [255, 0, 0]))
    settings._add_setting(Setting('point_cloud_color_r', _('Right color'), 'profile_settings', list, [0, 255, 255]))

    # ------------- Photogrammetry ---------------
    settings._add_setting(Setting('ph_save_enable', _('Save photos'), 'preferences', bool, False))
    settings._add_setting(Setting('ph_save_folder', _('Images folder'), 'preferences', str, 'photo/'))
    settings._add_setting(
        Setting('ph_save_divider', "Save every N'th frame", 'preferences', int, 2, min_value=1, max_value=9999)
    )

    # ------------- Mesh Correction ---------------
    settings._add_setting(
        Setting(
            'mesh_correction_offset',
            _('Center Offset (model space)'),
            'no_settings',
            np.ndarray,
            np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0])),
        )
    )

    settings._add_setting(Setting('mesh_correction_apply', _('Apply'), 'no_settings', str, ''))
    settings._add_setting(Setting('mesh_correction_reset', _('Reset'), 'no_settings', str, ''))

    # ----------- Engine ----------
    settings._add_setting(
        Setting(
            'scan_sleep',
            _('Wait milliseconds after each scan capture step'),
            'profile_settings',
            float,
            0.0,
            min_value=0.0,
            max_value=1000.0,
        )
    )

    settings._add_setting(
        Setting('scan_sync_threads', _('Synchronize capture and process threads'), 'profile_settings', bool, False)
    )

    # ========== MACHINE Profile ==============

    settings._add_setting(Setting('machine_diameter', _('Machine diameter'), 'machine_settings', int, 304))
    settings._add_setting(Setting('machine_width', _('Machine width'), 'machine_settings', int, 200))
    settings._add_setting(Setting('machine_height', _('Machine height'), 'machine_settings', int, 200))
    settings._add_setting(Setting('machine_depth', _('Machine depth'), 'machine_settings', int, 200))

    # Hack to translate combo boxes:
    _('Circular')
    _('Rectangular')
    settings._add_setting(
        Setting(
            'machine_shape',
            _('Machine shape'),
            'machine_settings',
            str,
            'Circular',
            possible_values=('Circular', 'Rectangular'),
        )
    )
    settings._add_setting(
        Setting(
            'machine_model_path',
            _('Machine model'),
            'machine_settings',
            str,
            _default_platform_mesh_path(),
        )
    )
    settings._add_setting(
        Setting(
            'machine_model_diameter',
            _('Machine model diameter (-1 dont scale; 0 auto scale)'),
            'machine_settings',
            int,
            304,
        )
    )
    settings._add_setting(Setting('machine_model_offset_x', 'Machine model offset X', 'machine_settings', float, 0.00))
    settings._add_setting(Setting('machine_model_offset_y', 'Machine model offset Y', 'machine_settings', float, 0.00))
    settings._add_setting(
        Setting('machine_model_offset_z', 'Machine model offset Z', 'machine_settings', float, 0.00)
    )  # 8.05 for Ciclop
    settings._add_setting(Setting('platform_border_z', 'Platform border draw z offset', 'machine_settings', int, 0))
    settings._add_setting(
        Setting('platform_markers_diameter', 'Platform markers diameter', 'machine_settings', int, 276)
    )
    settings._add_setting(Setting('platform_markers_z', 'Platform markers draw z offset', 'machine_settings', int, 0))

    settings._add_setting(Setting('point_size', 'Point size', 'preferences', int, 2, min_value=1, max_value=4))

    # =============== GUI General ================
    from ferret_scan.diy import diy_available

    _workbench_values = ('adjustment', 'calibration', 'scanning')
    if diy_available():
        _workbench_values = ('control',) + _workbench_values
    settings._add_setting(
        Setting(
            'workbench',
            _('Workbench'),
            'preferences',
            str,
            'scanning',
            possible_values=_workbench_values,
        )
    )

    settings._add_setting(Setting('show_welcome', _('Show welcome'), 'preferences', bool, True))
    settings._add_setting(Setting('check_for_updates', _('Check for updates'), 'preferences', bool, True))

    # settings._add_setting(
    #    Setting('basic_mode', _('Basic mode'), 'preferences', bool, False))
    # settings._add_setting(
    #    Setting('view_control_panel', _('View control panel'), 'preferences', bool, True))
    # settings._add_setting(
    #    Setting('view_control_video', _('View control panel'), 'preferences', bool, True))
    # settings._add_setting(
    #    Setting('view_adjustment_panel', _('View adjustment panel'),
    #            'preferences', bool, True))
    # settings._add_setting(
    #    Setting('view_adjustment_video', _('View adjustment video'),
    #            'preferences', bool, True))
    # settings._add_setting(
    #    Setting('view_calibration_panel', _('View calibration panel'),
    #            'preferences', bool, True))
    # settings._add_setting(
    #    Setting('view_calibration_video', _('View calibration video'),
    #            'preferences', bool, True))

    settings._add_setting(Setting('view_mode_advanced', _('Advanced mode'), 'preferences', bool, True))
    settings._add_setting(Setting('view_hide_help', _('Hide directions'), 'preferences', bool, False))

    settings._add_setting(Setting('last_files', _('Last files'), 'preferences', list, []))
    # TODO: Set this default value
    settings._add_setting(Setting('last_file', _('Last file'), 'preferences', str, ''))
    # TODO: Set this default value
    settings._add_setting(Setting('last_profile', _('Last profile'), 'preferences', str, ''))
    settings._add_setting(Setting('model_color', _('Default model color'), 'preferences', str, '888888'))
    settings._add_setting(Setting('last_clear_log_date', _('Last clear log date'), 'preferences', str, ''))

    # wizard
    settings._add_setting(Setting('adjust_laser', _('Adjust laser'), 'calibration_settings', bool, True))
