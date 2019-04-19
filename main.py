#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import sys

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QGraphicsDropShadowEffect

kGoldenRatio = 1.61803398875


class QSwitch(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True
        self.setMinimumSize(32, 20)
        self.setUpLayers()

    def setUpLayers(self) -> None:
        self.knob = QFrame(self)
        self.knob.setObjectName('knob')
        ef = QGraphicsDropShadowEffect()
        ef.setColor(QColor(0, 0, 0, 77))
        ef.setBlurRadius(3)
        ef.setOffset(0, 2)
        self.knob.setGraphicsEffect(ef)

        self.knobInside = QFrame(self)
        self.knobInside.setObjectName('knobInside')
        ef2 = QGraphicsDropShadowEffect()
        ef2.setColor(QColor(0, 0, 0, 89))
        ef2.setBlurRadius(4)
        ef2.setOffset(0, 0)
        self.knobInside.setGraphicsEffect(ef2)

        self.reloadLayerSize()
        self.reloadLayer()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.reloadLayerSize()

    def reloadLayer(self) -> None:
        pass

    def reloadLayerSize(self) -> None:
        self.setStyleSheet('QSwitch {{ border: 1px solid rgba(0, 0, 0, 51); border-radius: {0}px; }}'.format(int(self.height() / 2) - 1))

        self.knob.resize(int((self.width() - 2) * (1 / kGoldenRatio)), self.height() - 2)
        self.knob.move(1, 1)
        self.knob.setStyleSheet('QFrame#knob {{ background-color: white; border-radius: {0}px; }}'.format(int(self.knob.height() / 2) - 1))

        self.knobInside.resize(int((self.width() - 2) * (1 / kGoldenRatio)), self.height() - 2)
        self.knobInside.move(1, 1)
        self.knobInside.setStyleSheet('QFrame#knobInside {{ background-color: white; border-radius: {0}px; }}'.format(int(self.knobInside.height() / 2) - 1))

        self.setMaximumHeight(self.knob.width() + 2)


def main(argv: List[str]) -> int:
    app = QApplication(argv)

    switch1 = QSwitch()
    switch2 = QSwitch()

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
