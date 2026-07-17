"""Compact, scroll-safe preprocessing controls."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QToolButton,
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
        root.setSpacing(8)

        profile_row = QHBoxLayout()
        profile_label = QLabel("Processing profile")
        profile_label.setObjectName("sectionTitle")
        self.profile = QComboBox()
        self.profile.setAccessibleName("Processing profile")
        self.profile.setMinimumWidth(132)
        for profile in PreprocessingProfile:
            self.profile.addItem(profile.value.replace("_", " ").title(), profile.value)
        profile_row.addWidget(profile_label)
        profile_row.addWidget(self.profile, 1)
        root.addLayout(profile_row)

        self.advanced_toggle = QToolButton()
        self.advanced_toggle.setText("Advanced processing settings")
        self.advanced_toggle.setAccessibleName("Show advanced processing settings")
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_toggle.setCheckable(True)
        root.addWidget(self.advanced_toggle)

        self.advanced_scroll = QScrollArea()
        self.advanced_scroll.setObjectName("processingScroll")
        self.advanced_scroll.setWidgetResizable(True)
        self.advanced_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.advanced_scroll.setMinimumHeight(160)
        self.advanced_scroll.setMaximumHeight(230)
        advanced = QWidget()
        advanced_layout = QVBoxLayout(advanced)
        advanced_layout.setContentsMargins(4, 4, 8, 4)
        advanced_layout.setSpacing(8)

        self.rotation = QComboBox()
        self.rotation.setAccessibleName("Rotation")
        for value in (0, 90, 180, 270):
            self.rotation.addItem(f"{value}°", value)
        self.upscale = QComboBox()
        self.upscale.setAccessibleName("Upscale factor")
        for factor in (1.0, 1.5, 2.0, 3.0, 4.0):
            self.upscale.addItem(f"{factor:g}\N{MULTIPLICATION SIGN}", factor)
        transform = self._labeled_grid("Transform")
        transform.addWidget(QLabel("Rotation"), 1, 0)
        transform.addWidget(self.rotation, 1, 1)
        transform.addWidget(QLabel("Upscale"), 2, 0)
        transform.addWidget(self.upscale, 2, 1)
        transform.setColumnStretch(1, 1)
        advanced_layout.addLayout(transform)

        self.contrast = QDoubleSpinBox()
        self.contrast.setAccessibleName("Contrast")
        self.contrast.setRange(0.25, 3.0)
        self.contrast.setSingleStep(0.1)
        self.brightness = QSpinBox()
        self.brightness.setAccessibleName("Brightness")
        self.brightness.setRange(-100, 100)
        self.grayscale = QCheckBox("Grayscale")
        self.invert = QCheckBox("Invert colors")
        tone = self._labeled_grid("Tone")
        tone.addWidget(QLabel("Contrast"), 1, 0)
        tone.addWidget(self.contrast, 1, 1)
        tone.addWidget(QLabel("Brightness"), 2, 0)
        tone.addWidget(self.brightness, 2, 1)
        tone.addWidget(self.grayscale, 3, 0)
        tone.addWidget(self.invert, 3, 1)
        tone.setColumnStretch(1, 1)
        advanced_layout.addLayout(tone)

        self.denoise = QCheckBox("Denoise")
        self.sharpen = QCheckBox("Sharpen")
        self.deskew = QCheckBox("Deskew")
        self.threshold = QComboBox()
        self.threshold.setAccessibleName("Threshold mode")
        for mode in ThresholdMode:
            self.threshold.addItem(mode.value.title(), mode.value)
        cleanup = self._labeled_grid("Cleanup")
        cleanup.addWidget(QLabel("Threshold"), 1, 0)
        cleanup.addWidget(self.threshold, 1, 1)
        cleanup.addWidget(self.denoise, 2, 0)
        cleanup.addWidget(self.sharpen, 2, 1)
        cleanup.addWidget(self.deskew, 3, 0)
        cleanup.setColumnStretch(1, 1)
        advanced_layout.addLayout(cleanup)
        advanced_layout.addStretch(1)
        self.advanced_scroll.setWidget(advanced)
        self.advanced_scroll.setVisible(False)
        root.addWidget(self.advanced_scroll)

        actions = QHBoxLayout()
        self.apply_button = QPushButton("Preview processing")
        self.apply_button.setObjectName("primaryButton")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("tertiaryButton")
        actions.addWidget(self.apply_button, 1)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.reset_button)
        root.addLayout(actions)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setAccessibleName("Processing preview progress")
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        self.advanced_toggle.toggled.connect(self._toggle_advanced)
        self.profile.currentIndexChanged.connect(self._profile_changed)
        for control in (self.rotation, self.threshold, self.upscale):
            control.currentIndexChanged.connect(self._customized)
        self.contrast.valueChanged.connect(self._customized)
        self.brightness.valueChanged.connect(self._customized)
        for check in (self.grayscale, self.denoise, self.sharpen, self.invert, self.deskew):
            check.toggled.connect(self._customized)
        self.apply_button.clicked.connect(self._emit_options)
        self.reset_button.clicked.connect(self.reset)
        self.profile.setCurrentIndex(self.profile.findData(PreprocessingProfile.AUTOMATIC.value))
        self.set_options(options_for_profile(PreprocessingProfile.AUTOMATIC))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.set_busy(False)

    @staticmethod
    def _labeled_grid(title: str) -> QGridLayout:
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        grid.addWidget(label, 0, 0, 1, 2)
        return grid

    def _toggle_advanced(self, expanded: bool) -> None:
        self.advanced_scroll.setVisible(expanded)
        self.advanced_toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self.advanced_toggle.setAccessibleName(
            f"{'Hide' if expanded else 'Show'} advanced processing settings"
        )

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
        self.cancel_button.setVisible(busy)
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
