from ferret_scan.engine.calibration.calibration_data import calibration_data
from ferret_scan.engine.calibration.pattern import pattern
from ferret_scan.gui.util.video_view import VideoView
from ferret_scan.gui.workbench.calibration.ferret_board_pages import FerretBoardPages
from ferret_scan.gui.workbench.calibration.ferret_board_wizard import FerretBoardWizard
from ferret_scan.gui.workbench.calibration.pages.camera_intrinsics import CameraIntrinsicsPages
from ferret_scan.gui.workbench.calibration.pages.laser_triangulation import LaserTriangulationPages
from ferret_scan.gui.workbench.calibration.pages.pattern_settings import PatternSettingsPages
from ferret_scan.gui.workbench.calibration.pages.platform_extrinsics import PlatformExtrinsicsPages
from ferret_scan.gui.workbench.calibration.pages.scanner_autocheck import ScannerAutocheckPages
from ferret_scan.gui.workbench.calibration.panels import (
    CameraIntrinsics,
    FerretBoardCalibrationPanel,
    LaserTriangulationPanel,
    PatternSettings,
    PlatformExtrinsics,
    RotatingPlatform,
    ScannerAutocheck,
    VideoSettings,
)
from ferret_scan.gui.workbench.workbench import Workbench
from ferret_scan.hardware.types import DeviceCapabilities
from ferret_scan.runtime_engine import (
    combo_calibration,
    driver,
    image_capture,
    image_detection,
    laser_segmentation,
    laser_triangulation,
    platform_extrinsics,
)
from ferret_scan.util import profile


class CalibrationWorkbench(Workbench):
    def __init__(self, parent):
        self.engine_mode = 'calibration'
        self._capabilities = None
        Workbench.__init__(self, parent, name=_('Calibration workbench'))

    def configure(self, capabilities: DeviceCapabilities) -> None:
        self._capabilities = capabilities
        if not hasattr(self, 'panels_collection'):
            return
        for key, panel in self.panels_collection.expandable_panels.items():
            if key in capabilities.calibration_panels:
                panel.Show()
            else:
                panel.Hide()
        if capabilities.has_ferret_board_calibration and not capabilities.has_pattern_calibration:
            current = profile.settings.get('current_panel_calibration', '')
            if current not in capabilities.calibration_panels:
                profile.settings['current_panel_calibration'] = 'ferret_board_calibration'
            panel = self.panels_collection.expandable_panels.get('ferret_board_calibration')
            if panel is not None:
                panel.select_panel(invoke_callback=False)
        self.Layout()

    def _activate_panel(self, panel_key: str, *, invoke_callback: bool = False) -> None:
        panel = self.panels_collection.expandable_panels.get(panel_key)
        if panel is not None:
            panel.select_panel(invoke_callback=invoke_callback)

    def add_panels(self):
        self.add_panel(
            'ferret_board_calibration', FerretBoardCalibrationPanel, self.on_ferret_board_calibration_selected
        )
        self.add_panel('pattern_settings', PatternSettings, self.on_pattern_settings_selected)
        self.add_panel('scanner_autocheck', ScannerAutocheck, self.on_scanner_autocheck_selected)
        self.add_panel('rotating_platform_settings', RotatingPlatform, self.on_rotating_platform_settings_selected)
        self.add_panel('video_settings', VideoSettings, self.on_video_settings_selected)
        self.add_panel('camera_intrinsics', CameraIntrinsics, self.on_camera_intrinsics_selected)
        self.add_panel('laser_triangulation', LaserTriangulationPanel, self.on_laser_triangulation_selected)
        self.add_panel('platform_extrinsics', PlatformExtrinsics, self.on_platform_extrinsics_selected)

    def add_pages(self):
        self.add_page('video_view', VideoView(self, self.get_image))
        self.add_page('ferret_board_pages', FerretBoardPages(self, self.open_ferret_board_wizard))
        self.add_page(
            'camera_intrinsics_pages',
            CameraIntrinsicsPages(self, start_callback=self.disable_panels, exit_callback=self.update_panels),
        )
        self.add_page(
            'scanner_autocheck_pages',
            ScannerAutocheckPages(self, start_callback=self.disable_panels, exit_callback=self.update_panels),
        )
        self.add_page(
            'laser_triangulation_pages',
            LaserTriangulationPages(self, start_callback=self.disable_panels, exit_callback=self.update_panels),
        )
        self.add_page(
            'platform_extrinsics_pages',
            PlatformExtrinsicsPages(self, start_callback=self.disable_panels, exit_callback=self.update_panels),
        )
        self.add_page('pattern_settings_pages', PatternSettingsPages(self))

        self.pages_collection['ferret_board_pages'].Hide()
        self.pages_collection['camera_intrinsics_pages'].Hide()
        self.pages_collection['scanner_autocheck_pages'].Hide()
        self.pages_collection['laser_triangulation_pages'].Hide()
        self.pages_collection['platform_extrinsics_pages'].Hide()
        self.pages_collection['pattern_settings_pages'].Hide()

        self.pages_collection['camera_intrinsics_pages'].Disable()
        self.pages_collection['scanner_autocheck_pages'].Disable()
        self.pages_collection['laser_triangulation_pages'].Disable()
        self.pages_collection['platform_extrinsics_pages'].Disable()
        self.pages_collection['pattern_settings_pages'].Disable()

        if not profile.settings['view_mode_advanced']:
            if 'video_settings' in self.panels_collection.expandable_panels:
                self.panels_collection.expandable_panels['video_settings'].Hide()
            if 'camera_intrinsics' in self.panels_collection.expandable_panels:
                self.panels_collection.expandable_panels['camera_intrinsics'].Hide()
            if profile.settings['current_panel_calibration'] in ('video_settings', 'camera_intrinsics'):
                profile.settings['current_panel_calibration'] = 'pattern_settings'

        if profile.settings['view_hide_help']:
            self.pages_collection['scanner_autocheck_pages'].video_page.info_panel.Hide()
            self.pages_collection['laser_triangulation_pages'].video_page.info_panel.Hide()
            self.pages_collection['platform_extrinsics_pages'].video_page.info_panel.Hide()
            self.pages_collection['pattern_settings_pages'].info_panel.Hide()

        self._activate_panel(profile.settings['current_panel_calibration'], invoke_callback=False)

    def get_image(self):
        if (
            self._capabilities
            and self._capabilities.has_ferret_board_calibration
            and not self._capabilities.has_pattern_calibration
        ):
            return None
        image = image_capture.capture_pattern()
        return image_detection.detect_pattern(image)

    def on_open(self):
        if driver.is_connected:
            self.pages_collection['camera_intrinsics_pages'].Enable()
            self.pages_collection['scanner_autocheck_pages'].Enable()
            self.pages_collection['laser_triangulation_pages'].Enable()
            self.pages_collection['platform_extrinsics_pages'].Enable()
            self.pages_collection['pattern_settings_pages'].Enable()
        else:
            for page in self.pages_collection:
                self.pages_collection[page].stop()
            self.pages_collection['camera_intrinsics_pages'].Disable()
            self.pages_collection['scanner_autocheck_pages'].Disable()
            self.pages_collection['laser_triangulation_pages'].Disable()
            self.pages_collection['platform_extrinsics_pages'].Disable()
            self.pages_collection['pattern_settings_pages'].Disable()

        self._activate_panel(profile.settings['current_panel_calibration'], invoke_callback=False)

    def on_close(self):
        try:
            for page in self.pages_collection:
                self.pages_collection[page].stop()
        except Exception:
            pass

    def reset(self):
        for page in self.pages_collection:
            self.pages_collection[page].reset()

    def setup_engine(self):
        self.engine_mode = 'calibration'

        driver.camera.read_profile()
        if self._capabilities and self._capabilities.has_pattern_calibration:
            image_capture.pattern_mode.read_profile('pattern_calibration')
            image_capture.texture_mode.read_profile('texture_scanning')
            image_capture.laser_mode.read_profile('laser_calibration')
            image_capture.set_remove_background(profile.settings['remove_background_calibration'])
            laser_segmentation.read_profile('calibration')
            pattern.read_profile()
            calibration_data.read_profile_camera()
            calibration_data.read_profile_calibration()
            laser_triangulation.read_profile()
            platform_extrinsics.read_profile()
            combo_calibration.read_profile()
            image_capture.set_mode_pattern()

    def switch_engine_mode(self, mode='calibration'):
        if self.engine_mode == mode:
            return
        if self._capabilities and self._capabilities.has_pattern_calibration:
            image_capture.laser_mode.read_profile('laser_' + mode)
            image_capture.set_remove_background(profile.settings['remove_background_' + mode])
            laser_segmentation.read_profile(mode)

    def on_ferret_board_calibration_selected(self):
        profile.settings['current_panel_calibration'] = 'ferret_board_calibration'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['ferret_board_pages'])

    def open_ferret_board_wizard(self):
        dlg = FerretBoardWizard(self.GetParent())
        dlg.ShowModal()
        dlg.Destroy()

    def on_pattern_settings_selected(self):
        profile.settings['current_panel_calibration'] = 'pattern_settings'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['pattern_settings_pages'])

    def on_rotating_platform_settings_selected(self):
        profile.settings['current_panel_calibration'] = 'rotating_platform_settings'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['video_view'])

    def on_video_settings_selected(self):
        profile.settings['current_panel_calibration'] = 'video_settings'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['video_view'])

    def on_camera_intrinsics_selected(self):
        profile.settings['current_panel_calibration'] = 'camera_intrinsics'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['camera_intrinsics_pages'])

    def on_scanner_autocheck_selected(self):
        profile.settings['current_panel_calibration'] = 'scanner_autocheck'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['scanner_autocheck_pages'])

    def on_laser_triangulation_selected(self):
        profile.settings['current_panel_calibration'] = 'laser_triangulation'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['laser_triangulation_pages'])

    def on_platform_extrinsics_selected(self):
        profile.settings['current_panel_calibration'] = 'platform_extrinsics'
        self.switch_engine_mode('calibration')
        self._on_panel_selected(self.pages_collection['platform_extrinsics_pages'])

    def disable_panels(self):
        self.GetParent().enable_gui(False)
        self.scroll_panel.Disable()

    def update_panels(self):
        self.update_controls()
        self.GetParent().enable_gui(True)
        self.scroll_panel.Enable()

    def _on_panel_selected(self, panel):
        for page in self.pages_collection:
            self.pages_collection[page].Hide()
            self.pages_collection[page].stop()
        panel.Show()
        if driver.is_connected and hasattr(panel, 'play'):
            panel.play()
        self.Layout()
