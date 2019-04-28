#include <QApplication>
#include <QColor>
#include <QHBoxLayout>
#include <QMainWindow>

#include "QSwitch.h"

int main(int argc, char *argv[]) {
    auto app = QApplication(argc, argv);

    auto switch1 = new QSwitch();
    auto switch2 = new QSwitch(QColor(20, 149, 252, 255));
    auto switch3 = new QSwitch(QColor(255, 64, 6, 255));
    auto switch4 = new QSwitch();

    switch1->setChecked(true);
    switch2->setChecked(true);
    switch3->setChecked(true);

    auto layoutSwitchesTop = new QHBoxLayout();
    layoutSwitchesTop->addStretch();
    layoutSwitchesTop->addWidget(switch1);
    layoutSwitchesTop->addStretch();
    layoutSwitchesTop->addWidget(switch2);
    layoutSwitchesTop->addStretch();
    layoutSwitchesTop->addWidget(switch3);
    layoutSwitchesTop->addStretch();

    auto layout = new QVBoxLayout();
    layout->addLayout(layoutSwitchesTop);
    layout->addWidget(switch4);
    layout->setStretch(1, 1);

    auto central_widget = new QWidget();
    central_widget->setLayout(layout);

    auto main_window = QMainWindow();
    main_window.setCentralWidget(central_widget);
    main_window.resize(300, 230);
    main_window.show();

    return app.exec();
}
