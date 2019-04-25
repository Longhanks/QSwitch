#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import sys

from PyQt5.QtCore import QSize, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QPointF, QParallelAnimationGroup, QPoint
from PyQt5.QtGui import QColor, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, \
    QGraphicsDropShadowEffect, QSizePolicy

kAnimationDuration = 400
kBorderLineWidth = 1
kGoldenRatio = 1.61803398875
kDecreasedGoldenRatio = 1.38
kKnobBackgroundColor = QColor(255, 255, 255, 255)
kDefaultTintColor = QColor(79, 220, 116, 255)
kDisabledBorderColor = QColor(0, 0, 0, 51)
kMargin = 5
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
        self.animations = QParallelAnimationGroup(self)
        self.setUpLayers()

    @pyqtProperty(bool)
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, newValue):
        self._checked = newValue
        self.reloadLayerSize(animated=True)

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

    def reloadLayerSize(self, animated=False) -> None:
        self.backgroundLayer.resize(self.width() - 2 * kMargin, self.height() - 2 * kMargin)
        self.backgroundLayer.borderRadius = int((self.height() - 2 * kMargin) / 2) - 1

        self.animations.clear()

        if (self.dragged and self.draggingTowardsOn) or (not self.dragged and self.checked):
            anim1 = QPropertyAnimation(self.backgroundLayer, b'backgroundColor')
            anim1.setDuration(kAnimationDuration)
            anim1.setStartValue(self.backgroundLayer.backgroundColor)
            anim1.setEndValue(kDefaultTintColor)
            if not self.dragged:
                curve1 = QEasingCurve(QEasingCurve.BezierSpline)
                curve1.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0))
                anim1.setEasingCurve(curve1)
            self.animations.addAnimation(anim1)

            anim2 = QPropertyAnimation(self.backgroundLayer, b'borderColor')
            anim2.setDuration(kAnimationDuration)
            anim2.setStartValue(self.backgroundLayer.borderColor)
            anim2.setEndValue(kDefaultTintColor)
            if not self.dragged:
                curve2 = QEasingCurve(QEasingCurve.BezierSpline)
                curve2.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0))
                anim2.setEasingCurve(curve2)
            self.animations.addAnimation(anim2)
        else:
            anim1 = QPropertyAnimation(self.backgroundLayer, b'backgroundColor')
            anim1.setDuration(kAnimationDuration)
            anim1.setStartValue(self.backgroundLayer.backgroundColor)
            anim1.setEndValue(self.backgroundLayer.disabledBackgroundColor)
            if not self.dragged:
                curve1 = QEasingCurve(QEasingCurve.BezierSpline)
                curve1.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0))
                anim1.setEasingCurve(curve1)
            self.animations.addAnimation(anim1)

            anim2 = QPropertyAnimation(self.backgroundLayer, b'borderColor')
            anim2.setDuration(kAnimationDuration)
            anim2.setStartValue(self.backgroundLayer.borderColor)
            anim2.setEndValue(kDisabledBorderColor)
            if not self.dragged:
                curve2 = QEasingCurve(QEasingCurve.BezierSpline)
                curve2.addCubicBezierSegment(QPointF(0.25, 1.5),
                                            QPointF(0.5, 1.0),
                                            QPointF(1.0, 1.0))
                anim2.setEasingCurve(curve2)
            self.animations.addAnimation(anim2)

        knobWidth = int((self.width() - 2 * kMargin - 2 * kBorderLineWidth) * (1 / kGoldenRatio))
        roundKnobWidth = knobWidth
        if self.active:
            knobWidth = int((self.width() - 2 * kMargin - 2 * kBorderLineWidth) * (1 / kDecreasedGoldenRatio))

        if animated:
            anim3 = QPropertyAnimation(self.knobLayer, b'size')
            anim3.setDuration(kAnimationDuration)
            anim3.setStartValue(self.knobLayer.size())
            anim3.setEndValue(QSize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth))
            if not self.dragged:
                curve3 = QEasingCurve(QEasingCurve.BezierSpline)
                curve3.addCubicBezierSegment(QPointF(0.25, 1.5), QPointF(0.5, 1.0),
                                            QPointF(1.0, 1.0))
                anim3.setEasingCurve(curve3)
            self.animations.addAnimation(anim3)
        else:
            self.knobLayer.resize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth)

        if (not self.dragged and not self.checked) or (self.dragged and not self.draggingTowardsOn):
            knobX = kMargin + kBorderLineWidth
        else:
            knobX = self.width() - knobWidth - kBorderLineWidth - kMargin

        if animated:
            anim4 = QPropertyAnimation(self.knobLayer, b'pos')
            anim4.setDuration(kAnimationDuration)
            anim4.setStartValue(self.knobLayer.pos())
            anim4.setEndValue(QPoint(knobX, kMargin + kBorderLineWidth))
            if not self.dragged:
                curve4 = QEasingCurve(QEasingCurve.BezierSpline)
                curve4.addCubicBezierSegment(QPointF(0.25, 1.5),
                                             QPointF(0.5, 1.0),
                                             QPointF(1.0, 1.0))
                anim4.setEasingCurve(curve4)
            self.animations.addAnimation(anim4)
        else:
            self.knobLayer.move(knobX, kMargin + kBorderLineWidth)
            self.knobLayer.setStyleSheet('QFrame#knobLayer {{ background-color: white; border-radius: {0}px; }}'.format(
                int(self.knobLayer.height() / 2) - 1))

        if animated:
            anim5 = QPropertyAnimation(self.knobInsideLayer, b'size')
            anim5.setDuration(kAnimationDuration)
            anim5.setStartValue(self.knobInsideLayer.size())
            anim5.setEndValue(QSize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth))
            if not self.dragged:
                curve5 = QEasingCurve(QEasingCurve.BezierSpline)
                curve5.addCubicBezierSegment(QPointF(0.25, 1.5),
                                             QPointF(0.5, 1.0),
                                             QPointF(1.0, 1.0))
                anim5.setEasingCurve(curve5)
            self.animations.addAnimation(anim5)
        else:
            self.knobInsideLayer.resize(knobWidth, self.height() - 2 * kMargin - 2 * kBorderLineWidth)

        if animated:
            anim6 = QPropertyAnimation(self.knobInsideLayer, b'pos')
            anim6.setDuration(kAnimationDuration)
            anim6.setStartValue(self.knobInsideLayer.pos())
            anim6.setEndValue(QPoint(knobX, kMargin + kBorderLineWidth))
            if not self.dragged:
                curve6 = QEasingCurve(QEasingCurve.BezierSpline)
                curve6.addCubicBezierSegment(QPointF(0.25, 1.5),
                                             QPointF(0.5, 1.0),
                                             QPointF(1.0, 1.0))
                anim6.setEasingCurve(curve6)
            self.animations.addAnimation(anim6)
        else:
            self.knobInsideLayer.move(knobX, kMargin + kBorderLineWidth)
            self.knobInsideLayer.setStyleSheet(
                'QFrame#knobInsideLayer {{ background-color: white; border-radius: {}px; }}'.format(
                    int(self.knobInsideLayer.height() / 2) - 1))

        self.animations.start()

        self.setMaximumHeight(roundKnobWidth + 2 * kMargin + 2 * kBorderLineWidth)

    def sizeHint(self) -> QSize:
        hint = self.backgroundLayer.sizeHint()
        return QSize(hint.width() + 2 * kMargin, hint.height() + 2 * kMargin)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        self.active = True
        self.reloadLayerSize(animated=True)

    # def mouseMoveEvent(self, event: QMouseEvent) -> None:
    #     if not self.active:
    #         return
    #
    #     self.dragged = True
    #     self.draggingTowardsOn = event.pos().x() >= (self.width() - 2 * kMargin) / 2.0
        self.reloadLayerSize(animated=True)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        self.active = False

        if not self.dragged:
            self.checked = not self.checked
        else:
            self.checked = self.draggingTowardsOn

        self.dragged = False
        self.draggingTowardsOn = False

        self.reloadLayerSize(animated=True)

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
