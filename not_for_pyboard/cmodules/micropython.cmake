# This top-level micropython.cmake is responsible for listing
# the individual modules we want to include.
# Paths are absolute, and ${CMAKE_CURRENT_LIST_DIR} can be
# used to prefix subdirectories.


# Add the C example.
#include(${CMAKE_CURRENT_LIST_DIR}/cexample/micropython.cmake)


# Add the CAN.
include(${CMAKE_CURRENT_LIST_DIR}/esp32_can_soc_reader/micropython.cmake)

