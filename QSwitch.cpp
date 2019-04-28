#include "QSwitch.h"

#include <QDebug>
#include <QGraphicsDropShadowEffect>
#include <QPoint>
#include <QPropertyAnimation>
#include <QSize>

QSwitchLayer::QSwitchLayer(QWidget *parent)
    : QFrame(parent),
      m_backgroundColor(this->palette().color(this->backgroundRole())),
      m_borderColor(this->disabledBorderColor()),
      m_disabledBackgroundColor(
          this->palette().color(this->backgroundRole())) {}

QColor QSwitchLayer::backgroundColor() const {
    return this->m_backgroundColor;
}

void QSwitchLayer::setBackgroundColor(QColor newValue) {
    this->m_backgroundColor = newValue;
    this->applyStyleSheet();
}

QColor QSwitchLayer::borderColor() const {
    return this->m_borderColor;
}

void QSwitchLayer::setBorderColor(QColor newValue) {
    this->m_borderColor = newValue;
    this->applyStyleSheet();
}

int QSwitchLayer::borderRadius() const {
    return this->m_borderRadius;
}

void QSwitchLayer::setBorderRadius(int newValue) {
    this->m_borderRadius = newValue;
    this->applyStyleSheet();
}

int QSwitchLayer::borderLineWidth() const {
    return this->m_borderLineWidth;
}

void QSwitchLayer::setBorderLineWidth(int newValue) {
    this->m_borderLineWidth = newValue;
    this->applyStyleSheet();
}

QColor QSwitchLayer::disabledBackgroundColor() const {
    return this->m_disabledBackgroundColor;
}

QColor QSwitchLayer::disabledBorderColor() const {
    return QColor(0, 0, 0, 51);
}

void QSwitchLayer::applyStyleSheet() {
    this->setStyleSheet(
        QSwitchLayer::templateStyleSheet.arg(this->m_backgroundColor.red())
            .arg(this->m_backgroundColor.green())
            .arg(this->m_backgroundColor.blue())
            .arg(this->m_backgroundColor.alpha())
            .arg(this->m_borderLineWidth)
            .arg(this->m_borderColor.red())
            .arg(this->m_borderColor.green())
            .arg(this->m_borderColor.blue())
            .arg(this->m_borderColor.alpha())
            .arg(this->m_borderRadius));
}

QSwitch::QSwitch(QColor tintColor, QWidget *parent)
    : QFrame(parent), m_tintColor(tintColor) {
    this->m_animations = new QParallelAnimationGroup(this);

    this->m_backgroundLayer = new QSwitchLayer(this);
    this->m_backgroundLayer->setObjectName("_backgroundLayer");
    this->m_backgroundLayer->setBorderLineWidth(QSwitch::borderLineWidth);
    this->setMinimumSize(QSwitch::minimumWidth + 2 * QSwitch::defaultMargin,
                         QSwitch::minimumHeight + 2 * QSwitch::defaultMargin);
    this->m_backgroundLayer->move(QSwitch::defaultMargin,
                                  QSwitch::defaultMargin);

    this->m_knobLayer = new QFrame(this);
    this->m_knobLayer->setObjectName("_knobLayer");
    auto knobLayerShadowEffect =
        new QGraphicsDropShadowEffect(this->m_knobLayer);
    knobLayerShadowEffect->setColor(QColor(0, 0, 0, 77));
    knobLayerShadowEffect->setBlurRadius(4);
    knobLayerShadowEffect->setOffset(0, 2);
    this->m_knobLayer->setGraphicsEffect(knobLayerShadowEffect);

    this->m_knobInsideLayer = new QFrame(this);
    this->m_knobInsideLayer->setObjectName("_knobInsideLayer");
    auto knobInsideLayerShadowEffect =
        new QGraphicsDropShadowEffect(this->m_knobInsideLayer);
    knobInsideLayerShadowEffect->setColor(QColor(0, 0, 0, 89));
    knobInsideLayerShadowEffect->setBlurRadius(4);
    knobInsideLayerShadowEffect->setOffset(0, 0);
    this->m_knobInsideLayer->setGraphicsEffect(knobInsideLayerShadowEffect);

    this->redrawLayers();
}

bool QSwitch::isChecked() const {
    return this->m_isChecked;
}

void QSwitch::setChecked(bool newValue) {
    this->m_isChecked = newValue;
    this->redrawLayers(true);
}

QColor QSwitch::tintColor() const {
    return this->m_tintColor;
}

void QSwitch::setTintColor(QColor newValue) {
    this->m_tintColor = newValue;
    this->redrawLayers();
}

void QSwitch::mousePressEvent([[maybe_unused]] QMouseEvent *event) {
    if (!this->isEnabled()) {
        return;
    }
    this->m_isMouseDown = true;
    this->redrawLayers(true);
}

void QSwitch::mouseMoveEvent(QMouseEvent *event) {
    if (!this->m_isMouseDown) {
        return;
    }

    this->m_didDrag = true;

    auto oldIsDraggingTowardsOn = this->m_isDraggingTowardsOn;
    this->m_isDraggingTowardsOn =
        event->pos().x() >=
        static_cast<int>((this->width() - 2 * QSwitch::defaultMargin) / 2.0);

    if (oldIsDraggingTowardsOn != this->m_isDraggingTowardsOn) {
        this->m_isDraggingTowardsOnDidChangeSinceLastMoveEvent = true;
        this->redrawLayers(true);
    }
}

void QSwitch::mouseReleaseEvent([[maybe_unused]] QMouseEvent *event) {
    if (!this->isEnabled()) {
        return;
    }
    this->m_isMouseDown = false;

    if (!this->m_didDrag) {
        this->setChecked(!this->isChecked());
    } else {
        this->setChecked(this->m_isDraggingTowardsOn);
    }

    this->m_didDrag = false;
    this->m_isDraggingTowardsOn = false;

    if (!this->m_isDraggingTowardsOnDidChangeSinceLastMoveEvent) {
        this->redrawLayers(true);
    }

    this->m_isDraggingTowardsOnDidChangeSinceLastMoveEvent = false;
    emit this->toggled(this->isChecked());
}

void QSwitch::resizeEvent(QResizeEvent *event) {
    QFrame::resizeEvent(event);
    this->redrawLayers();
}

QSize QSwitch::sizeHint() const {
    auto hint = this->m_backgroundLayer->sizeHint();
    return QSize(hint.width() + 2 * QSwitch::defaultMargin,
                 hint.height() + 2 * QSwitch::defaultMargin);
}

QEasingCurve QSwitch::makeBezierCurveOvershoot() const {
    auto curve = QEasingCurve(QEasingCurve::BezierSpline);
    curve.addCubicBezierSegment(
        QPointF(0.25, 1.5), QPointF(0.5, 1.0), QPointF(1.0, 1.0));
    return curve;
}

QEasingCurve QSwitch::makeBezierCurveDefault() const {
    auto curve = QEasingCurve(QEasingCurve::BezierSpline);
    curve.addCubicBezierSegment(
        QPointF(0.25, 0.1), QPointF(0.25, 1.0), QPointF(1.0, 1.0));
    return curve;
}

void QSwitch::redrawLayers(bool animated) {
    this->m_backgroundLayer->resize(this->width() - 2 * QSwitch::defaultMargin,
                                    this->height() -
                                        2 * QSwitch::defaultMargin);
    this->m_backgroundLayer->setBorderRadius(
        ((this->height() - 2 * QSwitch::defaultMargin) / 2) - 1);

    this->m_animations->clear();

    if ((this->m_didDrag && this->m_isDraggingTowardsOn) ||
        (!this->m_didDrag && this->isChecked())) {
        auto animationBackgroundColor =
            new QPropertyAnimation(this->m_backgroundLayer, "backgroundColor");
        animationBackgroundColor->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationBackgroundColor->setStartValue(
            this->m_backgroundLayer->backgroundColor());
        animationBackgroundColor->setEndValue(this->tintColor());
        if (this->m_didDrag) {
            animationBackgroundColor->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationBackgroundColor->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationBackgroundColor);

        auto animationBorderColor =
            new QPropertyAnimation(this->m_backgroundLayer, "borderColor");
        animationBorderColor->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationBorderColor->setStartValue(
            this->m_backgroundLayer->borderColor());
        animationBorderColor->setEndValue(this->tintColor());
        if (this->m_didDrag) {
            animationBorderColor->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationBorderColor->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationBorderColor);
    } else {
        auto animationBackgroundColor =
            new QPropertyAnimation(this->m_backgroundLayer, "backgroundColor");
        animationBackgroundColor->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationBackgroundColor->setStartValue(
            this->m_backgroundLayer->backgroundColor());
        animationBackgroundColor->setEndValue(
            this->m_backgroundLayer->disabledBackgroundColor());
        if (this->m_didDrag) {
            animationBackgroundColor->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationBackgroundColor->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationBackgroundColor);

        auto animationBorderColor =
            new QPropertyAnimation(this->m_backgroundLayer, "borderColor");
        animationBorderColor->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationBorderColor->setStartValue(
            this->m_backgroundLayer->borderColor());
        animationBorderColor->setEndValue(
            this->m_backgroundLayer->disabledBorderColor());
        if (this->m_didDrag) {
            animationBorderColor->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationBorderColor->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationBorderColor);
    }

    auto knobWidth =
        static_cast<int>((this->width() - 2 * QSwitch::defaultMargin -
                          2 * QSwitch::borderLineWidth) *
                         (1 / QSwitch::goldenRatio));
    auto roundKnobWidth = knobWidth;
    if (this->m_isMouseDown) {
        knobWidth =
            static_cast<int>((this->width() - 2 * QSwitch::defaultMargin -
                              2 * QSwitch::borderLineWidth) *
                             (1 / QSwitch::decreasedGoldenRatio));
    }

    if (animated) {
        auto animationSizeKnob =
            new QPropertyAnimation(this->m_knobLayer, "size");
        animationSizeKnob->setDuration(QSwitch::animationDurationMilliSeconds);
        animationSizeKnob->setStartValue(this->m_knobLayer->size());
        animationSizeKnob->setEndValue(
            QSize(knobWidth,
                  this->height() - 2 * QSwitch::defaultMargin -
                      2 * QSwitch::borderLineWidth));
        if (this->m_didDrag) {
            animationSizeKnob->setEasingCurve(this->makeBezierCurveDefault());
        } else {
            animationSizeKnob->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationSizeKnob);
    } else {
        this->m_knobLayer->resize(knobWidth,
                                  this->height() - 2 * QSwitch::defaultMargin -
                                      2 * QSwitch::borderLineWidth);
    }

    auto knobX = [this, knobWidth]() -> int {
        if ((!this->m_didDrag && !this->isChecked()) ||
            (this->m_didDrag && !this->m_isDraggingTowardsOn)) {
            return QSwitch::defaultMargin + QSwitch::borderLineWidth;
        } else {
            return this->width() - knobWidth - QSwitch::borderLineWidth -
                   QSwitch::defaultMargin;
        }
    }();

    if (animated) {
        auto animationPosKnob =
            new QPropertyAnimation(this->m_knobLayer, "pos");
        animationPosKnob->setDuration(QSwitch::animationDurationMilliSeconds);
        animationPosKnob->setStartValue(this->m_knobLayer->pos());
        animationPosKnob->setEndValue(
            QPoint(knobX, QSwitch::defaultMargin + QSwitch::borderLineWidth));
        if (this->m_didDrag) {
            animationPosKnob->setEasingCurve(this->makeBezierCurveDefault());
        } else {
            animationPosKnob->setEasingCurve(this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationPosKnob);
    } else {
        this->m_knobLayer->move(
            knobX, QSwitch::defaultMargin + QSwitch::borderLineWidth);
        this->m_knobLayer->setStyleSheet(
            QString("QFrame#_knobLayer { background-color: white; "
                    "border-radius: %1px; }")
                .arg(this->m_knobLayer->height() / 2 - 1));
    }

    if (animated) {
        auto animationSizeKnobInside =
            new QPropertyAnimation(this->m_knobInsideLayer, "size");
        animationSizeKnobInside->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationSizeKnobInside->setStartValue(
            this->m_knobInsideLayer->size());
        animationSizeKnobInside->setEndValue(
            QSize(knobWidth,
                  this->height() - 2 * QSwitch::defaultMargin -
                      2 * QSwitch::borderLineWidth));
        if (this->m_didDrag) {
            animationSizeKnobInside->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationSizeKnobInside->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationSizeKnobInside);
    } else {
        this->m_knobInsideLayer->resize(knobWidth,
                                        this->height() -
                                            2 * QSwitch::defaultMargin -
                                            2 * QSwitch::borderLineWidth);
    }

    if (animated) {
        auto animationPosKnobInside =
            new QPropertyAnimation(this->m_knobInsideLayer, "pos");
        animationPosKnobInside->setDuration(
            QSwitch::animationDurationMilliSeconds);
        animationPosKnobInside->setStartValue(this->m_knobInsideLayer->pos());
        animationPosKnobInside->setEndValue(
            QPoint(knobX, QSwitch::defaultMargin + QSwitch::borderLineWidth));
        if (this->m_didDrag) {
            animationPosKnobInside->setEasingCurve(
                this->makeBezierCurveDefault());
        } else {
            animationPosKnobInside->setEasingCurve(
                this->makeBezierCurveOvershoot());
        }
        this->m_animations->addAnimation(animationPosKnobInside);
    } else {
        this->m_knobInsideLayer->move(
            knobX, QSwitch::defaultMargin + QSwitch::borderLineWidth);
        this->m_knobInsideLayer->setStyleSheet(
            QString("QFrame#_knobInsideLayer { background-color: white; "
                    "border-radius: %1px; }")
                .arg(this->m_knobInsideLayer->height() / 2 - 1));
    }

    this->m_animations->start();

    this->setMaximumHeight(roundKnobWidth + 2 * QSwitch::defaultMargin +
                           2 * QSwitch::borderLineWidth);
}
