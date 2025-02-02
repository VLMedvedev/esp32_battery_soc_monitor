#!/bin/bash

get_idf
#~/esp/esp-idf/export.sh



cd micropython/ports/esp32

#make clean

export BUILD_VERBOSE=1
export USER_C_MODULES=../../../../cmodules/micropython.cmake
echo  $USER_C_MODULES

make V=1 BOARD=LOLIN_S2_MINI all

ls /dev/ttyACM*

esptool --port /dev/ttyACM0  erase_flash

idf.py -D MICROPY_BOARD=LOLIN_S2_MINI -B build-LOLIN_S2_MINI -p /dev/ttyACM0 flash

exit 0

