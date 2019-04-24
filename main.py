#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import sys

from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QPointF
from PyQt5.QtGui import QColor, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, \
    QGraphicsDropShadowEffect

kAnimationDuration = 0.4
kBorderLineWidth = 1
kGoldenRatio = 1.61803398875
kDecreasedGoldenRatio = 1.38
kKnobBackgroundColor = QColor(255, 255, 255, 255)
kDefaultTintColor = QColor(79, 220, 116, 255)
kDisabledBorderColor = QColor(0, 0, 0, 51)
kMargin = 2
kMinimumWidth = 32
kMinimumHeight = 20


class _QSwitchLayer(QFrame):
    _templateStyleSheet = '_QSwitchLayer {{ background: rgba({}, {}, {}, {}); border: {}px solid rgba({}, {}, {}, {}); border-radius: {}px; }}'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.disabledBackgroundColor = self.palette().color(self.backgroundRole())
        self._backgroundColor = self.disabledBackgroundColor
        self._borderColor = kDisabledBorderColor
        self._borderRadius = 0

    def _applyStyleSheet(self):
        self.setStyleSheet(
            _QSwitchLayer._templateStyleSheet.format(self.backgroundColor.red(), self.backgroundColor.green(),
                                                     self.backgroundColor.blue(), self.backgroundColor.alpha(),
                                                     kBorderLineWidth, self.borderColor.red(), self.borderColor.green(),
                                                     self.borderColor.blue(), self.borderColor.alpha(),
                                                     self.borderRadius))

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, newValue):
        self._backgroundColor = newValue
        self._applyStyleSheet()

    @pyqtProperty(QColor)
    def borderColor(self):
        return self._borderColor

    @borderColor.setter
    def borderColor(self, newValue):
        self._borderColor = newValue
        self._applyStyleSheet()

    @pyqtProperty(int)
    def borderRadius(self):
        return self._borderRadius

    @borderRadius.setter
    def borderRadius(self, newvalue):
        self._borderRadius = newvalue
        self._applyStyleSheet()


class QSwitch(QFrame):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active: bool = False
        self._checked: bool = False
        self.dragged: bool = False
        self.draggingTowardsOn: bool = False
        self.backgroundLayer: QWidget
        self.knobLayer: QWidget
        self.knobInsideLayer: QWidget
        self.setUpLayers()

    @pyqtProperty(bool)
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, newValue):
        self._checked = newValue
        self.reloadLayerSize()

    def setUpLayers(self) -> None:
        self.backgroundLayer = _QSwitchLayer(self)
        self.backgroundLayer.setObjectName('backgroundLayer')
        self.setMinimumSize(kMinimumWidth + 2 * kMargin, kMinimumHeight + 2 * kMargin)
        self.backgroundLayer.move(kMargin, kMargin)

        self.knobLayer = QFrame(self)
        self.knobLayer.setObjectName('knobLayer')
        knobLayerShadowEffect = QGraphicsDropShadowEffect()
        knobLayerShadowEffect.setColor(QColor(0, 0, 0, 77))
        knobLayerShadowEffect.setBlurRadius(4)
        knobLayerShadowEffect.setOffset(0, 2)
        self.knobLayer.setGraphicsEffect(knobLayerShadowEffect)

        self.knobInsideLayer = QFrame(self)
        self.knobInsideLayer.setObjectName('knobInsideLayer')
        knobLayerInsideShadowEffect = QGraphicsDropShadowEffect()
        knobLayerInsideShadowEffect.setColor(QColor(0, 0, 0, 89))
        knobLayerInsideShadowEffect.setBlurRadius(4)
        knobLayerInsideShadowEffect.setOffset(0, 0)
        self.knobInsideLayer.setGraphicsEffect(knobLayerInsideShadowEffect)

        self.reloadLayerSize()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.reloadLayerSize()

    def reloadLayerSize(self) -> None:
        self.backgroundLayer.resize(self.width() - 2 * kMargin, self.height() - 2 * kMargin)
        if self.checked:
            self.anim = QPropertyAnimation(self.backgroundLayer, b'backgroundColor')
            self.anim.setDuration(int(1000 * kAnimationDuration))
            self.anim.setStartValue(self.backgroundLayer.backgroundColor)
            self.anim.setEndValue(kDefaultTintColor)
            self.curve = QEasingCurve(QEasingCurve.BezierSpline)
            self.curve.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0))
            self.anim.setEasingCurve(self.curve)
            self.anim.start()
            self.backgroundLayer.borderColor = kDefaultTintColor
            self.backgroundLayer.borderRadius = int((self.height() - 2 * kMargin) / 2) - 1
        else:
            self.anim = QPropertyAnimation(self.backgroundLayer, b'backgroundColor')
            self.anim.setDuration(int(1000 * kAnimationDuration))
            self.anim.setStartValue(self.backgroundLayer.backgroundColor)
            self.anim.setEndValue(self.backgroundLayer.disabledBackgroundColor)
            self.curve = QEasingCurve(QEasingCurve.BezierSpline)
            self.curve.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0))
            self.anim.setEasingCurve(self.curve)
            self.anim.start()
            self.backgroundLayer.borderColor = kDisabledBorderColor
            self.backgroundLayer.borderRadius = int((self.height() - 2 * kMargin) / 2) - 1

        knobWidth = int((self.width() - 2 * kMargin - 2 * kBorderLineWidth) * (1 / kGoldenRatio))
        roundKnobWidth = knobWidth
        if self.active:
            knobWidth = int((self.width() - 2 * kMargin - 2 * kBorderLineWidth) * (1 / kDecreasedGoldenRatio))
        self.knobLayer.resize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth)

        knobX = kMargin + kBorderLineWidth
        if self.checked:
            knobX = self.width() - knobWidth - kBorderLineWidth - kMargin

        self.knobLayer.move(knobX, kMargin + kBorderLineWidth)
        self.knobLayer.setStyleSheet('QFrame#knobLayer {{ background-color: white; border-radius: {0}px; }}'.format(
            int(self.knobLayer.height() / 2) - 1))

        self.knobInsideLayer.resize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth)
        self.knobInsideLayer.move(knobX, kMargin + kBorderLineWidth)
        self.knobInsideLayer.setStyleSheet(
            'QFrame#knobInsideLayer {{ background-color: white; border-radius: {}px; }}'.format(
                int(self.knobInsideLayer.height() / 2) - 1))

        self.setMaximumHeight(roundKnobWidth + 2 * kMargin + 2 * kBorderLineWidth)

    def sizeHint(self) -> QSize:
        hint = self.backgroundLayer.sizeHint()
        return QSize(hint.width() + 2 * kMargin, hint.height() + 2 * kMargin)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        self.active = True
        self.reloadLayerSize()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.active = False
        self.checked = not self.checked
        self.toggled.emit(self.checked)


def main(argv: List[str]) -> int:
    app = QApplication(argv)

    switch1 = QSwitch()
    switch2 = QSwitch()

    def cb(isChecked: bool) -> None:
        switch2.checked = isChecked

    switch1.toggled.connect(cb)

    layoutSwitch1 = QHBoxLayout()
    layoutSwitch1.addStretch()
    layoutSwitch1.addWidget(switch1)
    layoutSwitch1.addStretch()

    layout = QVBoxLayout()
    layout.addLayout(layoutSwitch1)
    layout.addWidget(switch2)
    layout.setStretch(1, 1)

    central_widget = QWidget()
    central_widget.setLayout(layout)

    main_window = QMainWindow()
    main_window.setCentralWidget(central_widget)
    main_window.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
