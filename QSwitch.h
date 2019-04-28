#include <QColor>
#include <QEasingCurve>
#include <QFrame>
#include <QMouseEvent>
#include <QParallelAnimationGroup>
#include <QResizeEvent>
#include <QString>

class QSwitchLayer : public QFrame {
    Q_OBJECT
    Q_PROPERTY(
        QColor backgroundColor READ backgroundColor WRITE setBackgroundColor)
    Q_PROPERTY(QColor borderColor READ borderColor WRITE setBorderColor)
    Q_PROPERTY(int borderRadius READ borderRadius WRITE setBorderRadius)
    Q_PROPERTY(
        int borderLineWidth READ borderLineWidth WRITE setBorderLineWidth)

public:
    explicit QSwitchLayer(QWidget *parent = nullptr);
    QColor backgroundColor() const;
    void setBackgroundColor(QColor newValue);
    QColor borderColor() const;
    void setBorderColor(QColor newValue);
    int borderRadius() const;
    void setBorderRadius(int newValue);
    int borderLineWidth() const;
    void setBorderLineWidth(int newValue);
    QColor disabledBackgroundColor() const;
    QColor disabledBorderColor() const;

private:
    QColor m_backgroundColor;
    QColor m_borderColor;
    int m_borderRadius = 0;
    int m_borderLineWidth = 0;
    const QColor m_disabledBackgroundColor;
    static inline const QString templateStyleSheet =
        "QSwitchLayer { background: rgba(%1, %2, %3, %4); border: %5px "
        "solid rgba(%6, %7, %8, %9); border-radius: %10px; }";

    void applyStyleSheet();
};

class QSwitch : public QFrame {
    Q_OBJECT
    Q_PROPERTY(bool checked READ isChecked WRITE setChecked)
    Q_PROPERTY(QColor tintColor READ tintColor WRITE setTintColor)

public:
    explicit QSwitch(QColor tintColor = defaultTintColor,
                     QWidget *parent = nullptr);
    bool isChecked() const;
    void setChecked(bool newValue);
    QColor tintColor() const;
    void setTintColor(QColor newValue);

signals:
    void toggled(bool checked);

protected:
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    QSize sizeHint() const override;

private:
    static inline constexpr const int animationDurationMilliSeconds = 400;
    static inline constexpr const int borderLineWidth = 1;
    static inline constexpr const double goldenRatio = 1.61803398875;
    static inline constexpr const double decreasedGoldenRatio = 1.38;
    static inline const QColor knobBackgroundColor =
        QColor(255, 255, 255, 255);
    static inline const QColor defaultTintColor = QColor(79, 220, 116, 255);
    static inline constexpr const int defaultMargin = 5;
    static inline constexpr const int minimumWidth = 32;
    static inline constexpr const int minimumHeight = 20;

    QEasingCurve makeBezierCurveOvershoot() const;
    QEasingCurve makeBezierCurveDefault() const;
    void redrawLayers(bool animated = false);

    bool m_isChecked = false;
    QColor m_tintColor;
    bool m_isMouseDown = false;
    bool m_didDrag = false;
    bool m_isDraggingTowardsOn = false;
    bool m_isDraggingTowardsOnDidChangeSinceLastMoveEvent = false;
    QParallelAnimationGroup *m_animations;
    QSwitchLayer *m_backgroundLayer;
    QFrame *m_knobLayer;
    QFrame *m_knobInsideLayer;
};
