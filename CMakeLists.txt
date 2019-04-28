cmake_minimum_required(VERSION 3.14)

if (APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "OS X deployment target" FORCE)

    option(WITH_BREW_QT "Build with Homebrew Qt" ON)
    if (WITH_BREW_QT)
        find_program(BREW_EXECUTABLE brew HINTS /usr/local/bin)
        if (${BREW_EXECUTABLE} STREQUAL "BREW_EXECUTABLE-NOTFOUND")
            message(STATUS "macOS: No Homebrew found.")
        else ()
            message(STATUS "macOS: Found Homebrew at ${BREW_EXECUTABLE}.")
            execute_process(COMMAND ${BREW_EXECUTABLE} --prefix qt OUTPUT_VARIABLE QT_PREFIX_PATH)
            string(REGEX REPLACE "\n$" "" QT_PREFIX_PATH_STRIPPED "${QT_PREFIX_PATH}")
            set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH};${QT_PREFIX_PATH_STRIPPED}")
            message(STATUS "macOS: Using Qt at ${QT_PREFIX_PATH_STRIPPED}.")
        endif ()
    endif ()
endif ()

enable_language(CXX)

set(CMAKE_CXX_STANDARD 17)

project(QSwitch-Demo LANGUAGES CXX VERSION 1.4.0)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)
find_package(Qt5 COMPONENTS Widgets REQUIRED)

cmake_policy(SET CMP0020 NEW)
cmake_policy(SET CMP0071 NEW)

add_executable(qswitch-demo WIN32 MACOSX_BUNDLE)

set(QSWITCH_DEMO_SOURCES
    "${CMAKE_CURRENT_LIST_DIR}/main.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/QSwitch.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/QSwitch.h"
    )

target_sources(qswitch-demo PRIVATE ${QSWITCH_DEMO_SOURCES})

set_target_properties(qswitch-demo PROPERTIES
    AUTOMOC ON
    )

target_link_libraries(qswitch-demo PRIVATE
    Qt5::Widgets
    )
