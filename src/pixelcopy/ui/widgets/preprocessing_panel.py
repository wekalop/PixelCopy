"""Preprocessing profile and custom-control panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.domain.preprocessing import (
    PreprocessingOptions,
    PreprocessingProfile,
    ThresholdMode,
)
from pixelcopy.preprocessing.profiles import options_for_profile


class PreprocessingPanel(QWidget):
    """Collect explicit options without running image operations in the UI."""

    process_requested = Signal(object)
    cancel_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._updating = False
        self._source_available = False
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        grid = QGridLayout()
        self.profile = QComboBox()
        self.profile.setMinimumWidth(100)
        for profile in PreprocessingProfile:
            self.profile.addItem(profile.value.replace("_", " ").title(), profile.value)
        self.rotation = QComboBox()
        self.rotation.setMinimumWidth(60)
        for value in (0, 90, 180, 270):
            self.rotation.addItem(f"{value}°", value)
        self.grayscale = QCheckBox("Grayscale")
        self.contrast = QDoubleSpinBox()
        self.contrast.setRange(0.25, 3.0)
        self.contrast.setSingleStep(0.1)
        self.brightness = QSpinBox()
        self.brightness.setRange(-100, 100)
        self.denoise = QCheckBox("Denoise")
        self.sharpen = QCheckBox("Sharpen")
        self.threshold = QComboBox()
        self.threshold.setMinimumWidth(90)
        for mode in ThresholdMode:
            self.threshold.addItem(mode.value.title(), mode.value)
        self.invert = QCheckBox("Invert")
        self.deskew = QCheckBox("Deskew")
        self.upscale = QComboBox()
        self.upscale.setMinimumWidth(70)
        for factor in (1.0, 1.5, 2.0, 3.0, 4.0):
            self.upscale.addItem(f"{factor:g}x", factor)

        grid.addWidget(QLabel("Profile"), 0, 0)
        grid.addWidget(self.profile, 0, 1)
        grid.addWidget(QLabel("Rotate"), 0, 2)
        grid.addWidget(self.rotation, 0, 3)
        grid.addWidget(self.grayscale, 1, 0, 1, 2)
        grid.addWidget(self.denoise, 1, 2, 1, 2)
        grid.addWidget(self.sharpen, 2, 0, 1, 2)
        grid.addWidget(self.invert, 2, 2, 1, 2)
        grid.addWidget(QLabel("Contrast"), 3, 0)
        grid.addWidget(self.contrast, 3, 1)
        grid.addWidget(QLabel("Brightness"), 3, 2)
        grid.addWidget(self.brightness, 3, 3)
        grid.addWidget(QLabel("Threshold"), 4, 0)
        grid.addWidget(self.threshold, 4, 1)
        grid.addWidget(QLabel("Upscale"), 4, 2)
        grid.addWidget(self.upscale, 4, 3)
        grid.addWidget(self.deskew, 5, 0, 1, 2)
        for column in (1, 3):
            grid.setColumnStretch(column, 1)
        root.addLayout(grid)

        actions = QGridLayout()
        self.apply_button = QPushButton("Preview processing")
        self.apply_button.setObjectName("primaryButton")
        self.cancel_button = QPushButton("Cancel")
        self.reset_button = QPushButton("Reset")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)
        actions.addWidget(self.apply_button, 0, 0)
        actions.addWidget(self.cancel_button, 0, 1)
        actions.addWidget(self.reset_button, 0, 2)
        actions.addWidget(self.progress, 1, 0, 1, 3)
        root.addLayout(actions)

        self.profile.currentIndexChanged.connect(self._profile_changed)
        for control in (self.rotation, self.threshold, self.upscale):
            control.currentIndexChanged.connect(self._customized)
        self.contrast.valueChanged.connect(self._customized)
        self.brightness.valueChanged.connect(self._customized)
        for check in (self.grayscale, self.denoise, self.sharpen, self.invert, self.deskew):
            check.toggled.connect(self._customized)
        self.apply_button.clicked.connect(self._emit_options)
        self.cancel_button.clicked.connect(self.cancel_requested)
        self.reset_button.clicked.connect(self.reset)
        self.profile.setCurrentIndex(self.profile.findData(PreprocessingProfile.AUTOMATIC.value))
        self.set_options(options_for_profile(PreprocessingProfile.AUTOMATIC))
        self.set_busy(False)

    def current_options(self) -> PreprocessingOptions:
        return PreprocessingOptions(
            rotation_degrees=int(self.rotation.currentData()),
            grayscale=self.grayscale.isChecked(),
            contrast=self.contrast.value(),
            brightness=self.brightness.value(),
            denoise=self.denoise.isChecked(),
            sharpen=self.sharpen.isChecked(),
            threshold=ThresholdMode(str(self.threshold.currentData())),
            invert=self.invert.isChecked(),
            deskew=self.deskew.isChecked(),
            upscale_factor=float(self.upscale.currentData()),
        )

    def set_options(self, options: PreprocessingOptions) -> None:
        self._updating = True
        self.rotation.setCurrentIndex(self.rotation.findData(options.rotation_degrees))
        self.grayscale.setChecked(options.grayscale)
        self.contrast.setValue(options.contrast)
        self.brightness.setValue(options.brightness)
        self.denoise.setChecked(options.denoise)
        self.sharpen.setChecked(options.sharpen)
        self.threshold.setCurrentIndex(self.threshold.findData(options.threshold.value))
        self.invert.setChecked(options.invert)
        self.deskew.setChecked(options.deskew)
        self.upscale.setCurrentIndex(self.upscale.findData(options.upscale_factor))
        self._updating = False

    def set_source_available(self, available: bool) -> None:
        self._source_available = available
        self.apply_button.setEnabled(available and not self.progress.isVisible())
        self.reset_button.setEnabled(available and not self.progress.isVisible())

    def set_busy(self, busy: bool) -> None:
        self.progress.setVisible(busy)
        self.cancel_button.setEnabled(busy)
        self.apply_button.setEnabled(self._source_available and not busy)
        self.reset_button.setEnabled(self._source_available and not busy)
        if busy:
            self.progress.setValue(0)

    def set_progress(self, value: int) -> None:
        self.progress.setValue(value)

    def reset(self) -> None:
        self.profile.setCurrentIndex(self.profile.findData(PreprocessingProfile.AUTOMATIC.value))
        self.set_options(options_for_profile(PreprocessingProfile.AUTOMATIC))
        self.reset_requested.emit()

    def _profile_changed(self) -> None:
        if not self._updating:
            profile = PreprocessingProfile(str(self.profile.currentData()))
            self.set_options(options_for_profile(profile))

    def _customized(self) -> None:
        if self._updating:
            return
        self._updating = True
        self.profile.setCurrentIndex(self.profile.findData(PreprocessingProfile.CUSTOM.value))
        self._updating = False

    def _emit_options(self) -> None:
        self.process_requested.emit(self.current_options())
