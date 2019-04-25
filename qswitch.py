# -*- coding: utf-8 -*-
from PyQt5.QtCore import (
    QSize,
    pyqtSignal,
    pyqtProperty,
    QPropertyAnimation,
    QEasingCurve,
    QPointF,
    QParallelAnimationGroup,
    QPoint,
)
from PyQt5.QtGui import QColor, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QFrame, QGraphicsDropShadowEffect


class _QSwitchLayer(QFrame):
    def backgroundColor(self) -> QColor:
        return self._backgroundColor

    def setBackgroundColor(self, newValue: QColor) -> None:
        self._backgroundColor = newValue
        self._applyStyleSheet()

    def borderColor(self) -> QColor:
        return self._borderColor

    def setBorderColor(self, newValue: QColor) -> None:
        self._borderColor = newValue
        self._applyStyleSheet()

    def borderRadius(self) -> int:
        return self._borderRadius

    def setBorderRadius(self, newValue: int) -> None:
        self._borderRadius = newValue
        self._applyStyleSheet()

    backgroundColor = pyqtProperty(
        QColor, fget=backgroundColor, fset=setBackgroundColor
    )
    borderColor = pyqtProperty(QColor, fget=borderColor, fset=setBorderColor)
    borderRadius = pyqtProperty(int, fget=borderRadius, fset=setBorderRadius)
    _templateStyleSheet = '_QSwitchLayer {{ background: rgba({}, {}, {}, {}); border: {}px solid rgba({}, {}, {}, {}); border-radius: {}px; }}'

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.disabledBackgroundColor = self.palette().color(
            self.backgroundRole()
        )
        self.disabledBorderColor = QColor(0, 0, 0, 51)
        self._backgroundColor = self.disabledBackgroundColor
        self._borderColor = self.disabledBorderColor
        self._borderRadius = 0

    def _applyStyleSheet(self) -> None:
        self.setStyleSheet(
            _QSwitchLayer._templateStyleSheet.format(
                self.backgroundColor.red(),
                self.backgroundColor.green(),
                self.backgroundColor.blue(),
                self.backgroundColor.alpha(),
                QSwitch.BORDER_LINE_WIDTH,
                self.borderColor.red(),
                self.borderColor.green(),
                self.borderColor.blue(),
                self.borderColor.alpha(),
                self.borderRadius,
            )
        )


class QSwitch(QFrame):
    ANIMATION_DURATION_MS = 400
    BORDER_LINE_WIDTH = 1
    GOLDEN_RATIO = 1.61803398875
    DECREASED_GOLDEN_RATIO = 1.38
    KNOB_BACKGROUND_COLOR = QColor(255, 255, 255, 255)
    DEFAULT_TINT_COLOR = QColor(79, 220, 116, 255)
    DEFAULT_MARGIN = 5
    MINIMUM_WIDTH = 32
    MINIMUM_HEIGHT = 20

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, newValue: bool) -> None:
        self._checked = newValue
        self._redrawLayers(animated=True)

    def tintColor(self) -> QColor:
        return self._tintColor

    def setTintColor(self, newValue: QColor) -> None:
        self._tintColor = newValue
        self._redrawLayers()

    toggled = pyqtSignal(bool)
    checked = pyqtProperty(bool, fget=isChecked, fset=setChecked)
    tintColor = pyqtProperty(bool, fget=tintColor, fset=setTintColor)

    def __init__(
        self, tintColor: QColor = DEFAULT_TINT_COLOR, parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        self._checked = False
        self._tintColor = tintColor
        self._isMouseDown = False
        self._didDrag = False
        self._isDraggingTowardsOn = False
        self._isDraggingTowardsOnDidChangeSinceLastMoveEvent = False
        self._animations = QParallelAnimationGroup(self)

        self._backgroundLayer = _QSwitchLayer(self)
        self._backgroundLayer.setObjectName('_backgroundLayer')
        self.setMinimumSize(
            QSwitch.MINIMUM_WIDTH + 2 * QSwitch.DEFAULT_MARGIN,
            QSwitch.MINIMUM_HEIGHT + 2 * QSwitch.DEFAULT_MARGIN,
        )
        self._backgroundLayer.move(
            QSwitch.DEFAULT_MARGIN, QSwitch.DEFAULT_MARGIN
        )

        self._knobLayer = QFrame(self)
        self._knobLayer.setObjectName('_knobLayer')
        _knobLayerShadowEffect = QGraphicsDropShadowEffect()
        _knobLayerShadowEffect.setColor(QColor(0, 0, 0, 77))
        _knobLayerShadowEffect.setBlurRadius(4)
        _knobLayerShadowEffect.setOffset(0, 2)
        self._knobLayer.setGraphicsEffect(_knobLayerShadowEffect)

        self._knobInsideLayer = QFrame(self)
        self._knobInsideLayer.setObjectName('_knobInsideLayer')
        _knobLayerInsideShadowEffect = QGraphicsDropShadowEffect()
        _knobLayerInsideShadowEffect.setColor(QColor(0, 0, 0, 89))
        _knobLayerInsideShadowEffect.setBlurRadius(4)
        _knobLayerInsideShadowEffect.setOffset(0, 0)
        self._knobInsideLayer.setGraphicsEffect(_knobLayerInsideShadowEffect)

        self._redrawLayers()

    def _makeBezierCurveOvershoot(self) -> QEasingCurve:
        curve = QEasingCurve(QEasingCurve.BezierSpline)
        curve.addCubicBezierSegment(
            QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0)
        )
        return curve

    def _makeBezierCurveDefault(self) -> QEasingCurve:
        curve = QEasingCurve(QEasingCurve.BezierSpline)
        curve.addCubicBezierSegment(
            QPointF(0.25, 0.1), QPointF(0.25, 1.0), QPointF(1.0, 1.0)
        )
        return curve

    def _redrawLayers(self, animated: bool = False) -> None:
        self._backgroundLayer.resize(
            self.width() - 2 * QSwitch.DEFAULT_MARGIN,
            self.height() - 2 * QSwitch.DEFAULT_MARGIN,
        )
        self._backgroundLayer.borderRadius = (
            int((self.height() - 2 * QSwitch.DEFAULT_MARGIN) / 2) - 1
        )

        self._animations.clear()

        if (self._didDrag and self._isDraggingTowardsOn) or (
            not self._didDrag and self.checked
        ):
            _animationBackgroundColor = QPropertyAnimation(
                self._backgroundLayer, b'backgroundColor'
            )
            _animationBackgroundColor.setDuration(
                QSwitch.ANIMATION_DURATION_MS
            )
            _animationBackgroundColor.setStartValue(
                self._backgroundLayer.backgroundColor
            )
            _animationBackgroundColor.setEndValue(self.tintColor)
            if self._didDrag:
                _animationBackgroundColor.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            else:
                _animationBackgroundColor.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            self._animations.addAnimation(_animationBackgroundColor)

            _animationBorderColor = QPropertyAnimation(
                self._backgroundLayer, b'borderColor'
            )
            _animationBorderColor.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationBorderColor.setStartValue(
                self._backgroundLayer.borderColor
            )
            _animationBorderColor.setEndValue(self.tintColor)
            if self._didDrag:
                _animationBorderColor.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            else:
                _animationBorderColor.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            self._animations.addAnimation(_animationBorderColor)
        else:
            _animationBackgroundColor = QPropertyAnimation(
                self._backgroundLayer, b'backgroundColor'
            )
            _animationBackgroundColor.setDuration(
                QSwitch.ANIMATION_DURATION_MS
            )
            _animationBackgroundColor.setStartValue(
                self._backgroundLayer.backgroundColor
            )
            _animationBackgroundColor.setEndValue(
                self._backgroundLayer.disabledBackgroundColor
            )
            if self._didDrag:
                _animationBackgroundColor.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            else:
                _animationBackgroundColor.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            self._animations.addAnimation(_animationBackgroundColor)

            _animationBorderColor = QPropertyAnimation(
                self._backgroundLayer, b'borderColor'
            )
            _animationBorderColor.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationBorderColor.setStartValue(
                self._backgroundLayer.borderColor
            )
            _animationBorderColor.setEndValue(
                self._backgroundLayer.disabledBorderColor
            )
            if self._didDrag:
                _animationBorderColor.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            else:
                _animationBorderColor.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            self._animations.addAnimation(_animationBorderColor)

        knobWidth = int(
            (
                self.width()
                - 2 * QSwitch.DEFAULT_MARGIN
                - 2 * QSwitch.BORDER_LINE_WIDTH
            )
            * (1 / QSwitch.GOLDEN_RATIO)
        )
        roundKnobWidth = knobWidth
        if self._isMouseDown:
            knobWidth = int(
                (
                    self.width()
                    - 2 * QSwitch.DEFAULT_MARGIN
                    - 2 * QSwitch.BORDER_LINE_WIDTH
                )
                * (1 / QSwitch.DECREASED_GOLDEN_RATIO)
            )

        if animated:
            _animationSizeKnob = QPropertyAnimation(self._knobLayer, b'size')
            _animationSizeKnob.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationSizeKnob.setStartValue(self._knobLayer.size())
            _animationSizeKnob.setEndValue(
                QSize(
                    knobWidth,
                    self.height()
                    - 2 * QSwitch.DEFAULT_MARGIN
                    - 2 * QSwitch.BORDER_LINE_WIDTH,
                )
            )
            if not self._didDrag:
                _animationSizeKnob.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            else:
                _animationSizeKnob.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            self._animations.addAnimation(_animationSizeKnob)
        else:
            self._knobLayer.resize(
                knobWidth,
                self.height()
                - 2 * QSwitch.DEFAULT_MARGIN
                - 2 * QSwitch.BORDER_LINE_WIDTH,
            )

        if (not self._didDrag and not self.checked) or (
            self._didDrag and not self._isDraggingTowardsOn
        ):
            knobX = QSwitch.DEFAULT_MARGIN + QSwitch.BORDER_LINE_WIDTH
        else:
            knobX = (
                self.width()
                - knobWidth
                - QSwitch.BORDER_LINE_WIDTH
                - QSwitch.DEFAULT_MARGIN
            )

        if animated:
            _animationPosKnob = QPropertyAnimation(self._knobLayer, b'pos')
            _animationPosKnob.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationPosKnob.setStartValue(self._knobLayer.pos())
            _animationPosKnob.setEndValue(
                QPoint(
                    knobX, QSwitch.DEFAULT_MARGIN + QSwitch.BORDER_LINE_WIDTH
                )
            )
            if not self._didDrag:
                _animationPosKnob.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            else:
                _animationPosKnob.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            self._animations.addAnimation(_animationPosKnob)
        else:
            self._knobLayer.move(
                knobX, QSwitch.DEFAULT_MARGIN + QSwitch.BORDER_LINE_WIDTH
            )
            self._knobLayer.setStyleSheet(
                'QFrame#_knobLayer {{ background-color: white; border-radius: {0}px; }}'.format(
                    int(self._knobLayer.height() / 2) - 1
                )
            )

        if animated:
            _animationSizeKnobInside = QPropertyAnimation(
                self._knobInsideLayer, b'size'
            )
            _animationSizeKnobInside.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationSizeKnobInside.setStartValue(
                self._knobInsideLayer.size()
            )
            _animationSizeKnobInside.setEndValue(
                QSize(
                    knobWidth,
                    self.height()
                    - 2 * QSwitch.DEFAULT_MARGIN
                    - 2 * QSwitch.BORDER_LINE_WIDTH,
                )
            )
            if not self._didDrag:
                _animationSizeKnobInside.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            else:
                _animationSizeKnobInside.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            self._animations.addAnimation(_animationSizeKnobInside)
        else:
            self._knobInsideLayer.resize(
                knobWidth,
                self.height()
                - 2 * QSwitch.DEFAULT_MARGIN
                - 2 * QSwitch.BORDER_LINE_WIDTH,
            )

        if animated:
            _animationPosKnobInside = QPropertyAnimation(
                self._knobInsideLayer, b'pos'
            )
            _animationPosKnobInside.setDuration(QSwitch.ANIMATION_DURATION_MS)
            _animationPosKnobInside.setStartValue(self._knobInsideLayer.pos())
            _animationPosKnobInside.setEndValue(
                QPoint(
                    knobX, QSwitch.DEFAULT_MARGIN + QSwitch.BORDER_LINE_WIDTH
                )
            )
            if not self._didDrag:
                _animationPosKnobInside.setEasingCurve(
                    self._makeBezierCurveOvershoot()
                )
            else:
                _animationPosKnobInside.setEasingCurve(
                    self._makeBezierCurveDefault()
                )
            self._animations.addAnimation(_animationPosKnobInside)
        else:
            self._knobInsideLayer.move(
                knobX, QSwitch.DEFAULT_MARGIN + QSwitch.BORDER_LINE_WIDTH
            )
            self._knobInsideLayer.setStyleSheet(
                'QFrame#_knobInsideLayer {{ background-color: white; border-radius: {}px; }}'.format(
                    int(self._knobInsideLayer.height() / 2) - 1
                )
            )

        self._animations.start()

        self.setMaximumHeight(
            roundKnobWidth
            + 2 * QSwitch.DEFAULT_MARGIN
            + 2 * QSwitch.BORDER_LINE_WIDTH
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        self._isMouseDown = True
        self._redrawLayers(animated=True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._isMouseDown:
            return

        self._didDrag = True

        _oldIsDraggingTowardsOn = self._isDraggingTowardsOn
        self._isDraggingTowardsOn = (
            event.pos().x()
            >= (self.width() - 2 * QSwitch.DEFAULT_MARGIN) / 2.0
        )
        if _oldIsDraggingTowardsOn != self._isDraggingTowardsOn:
            self._isDraggingTowardsOnDidChangeSinceLastMoveEvent = True
            self._redrawLayers(animated=True)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        self._isMouseDown = False

        if not self._didDrag:
            self.checked = not self.checked
        else:
            self.checked = self._isDraggingTowardsOn

        self._didDrag = False
        self._isDraggingTowardsOn = False

        if not self._isDraggingTowardsOnDidChangeSinceLastMoveEvent:
            self._redrawLayers(animated=True)

        self._isDraggingTowardsOnDidChangeSinceLastMoveEvent = False
        self.toggled.emit(self.checked)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._redrawLayers()

    def sizeHint(self) -> QSize:
        hint = self._backgroundLayer.sizeHint()
        return QSize(
            hint.width() + 2 * QSwitch.DEFAULT_MARGIN,
            hint.height() + 2 * QSwitch.DEFAULT_MARGIN,
        )
