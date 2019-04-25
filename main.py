#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from qswitch import QSwitch


def main(argv: List[str]) -> int:
    app = QApplication(argv)

    switch1 = QSwitch()
    switch2 = QSwitch(tintColor=QColor(20, 149, 252, 255))
    switch3 = QSwitch(tintColor=QColor(255, 64, 6, 255))
    switch4 = QSwitch()

    switch1.checked = True
    switch2.checked = True
    switch3.checked = True

    layoutSwitchesTop = QHBoxLayout()
    layoutSwitchesTop.addStretch()
    layoutSwitchesTop.addWidget(switch1)
    layoutSwitchesTop.addStretch()
    layoutSwitchesTop.addWidget(switch2)
    layoutSwitchesTop.addStretch()
    layoutSwitchesTop.addWidget(switch3)
    layoutSwitchesTop.addStretch()

    layout = QVBoxLayout()
    layout.addLayout(layoutSwitchesTop)
    layout.addWidget(switch4)
    layout.setStretch(1, 1)

    central_widget = QWidget()
    central_widget.setLayout(layout)

    main_window = QMainWindow()
    main_window.setCentralWidget(central_widget)
    main_window.resize(300, 230)
    main_window.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
