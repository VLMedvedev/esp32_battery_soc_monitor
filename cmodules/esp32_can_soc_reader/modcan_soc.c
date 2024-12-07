//
// Created by medvedev on 11/28/24.

    /*Growatt
     *
     * ID=0x313 - Send by the battery and include some of current statuses
    [D0:D1] = System voltage * 0.1V
    [D2:D3] = Total current * 0.1A passing trough the ARK BMS. If the value is greater than 0 - charging, if it lower than 0 discharging.
    [D4:D5] = unknown
    [D6] = SOC in %
     *PYLONTECH
     * ID:=0x355
    [D0:D1] = SOC Value (data type : 16bit unsigned int, byte order : little endian, scale factor : 1, unit : %)
     */
//
/* ESP32 TWAI receive example.
  Receive messages and sends them over serial.

  Connect a CAN bus transceiver to the RX/TX pins.
  For example: SN65HVD230

  TWAI_MODE_LISTEN_ONLY is used so that the TWAI controller will not influence the bus.

  The API gives other possible speeds and alerts:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/twai.html

  created 05-11-2022 by Stephan Martin (designer2k2)
*/

// Include MicroPython API.
#include "py/runtime.h"
// Used to get the time in the Timer class example.
#include "py/mphal.h"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "driver/twai.h"

// Interval:
#define POLLING_RATE_MS 1000
#define MSG_ID          0x355   //11 bit standard format ID  SOC

#if MODULE_CAN_ENABLED

#include "driver/twai.h"

// This is the function which will be called from Python as esp32_soc.driver_init(rx, tx).
static mp_obj_t can_driver_init(mp_obj_t rx_obj, mp_obj_t tx_obj) {
    // Extract the ints from the micropython input objects.
    // Pins used to connect to CAN bus transceiver:
//#define RX_PIN 37
//#define TX_PIN 39
    int rx_pin = mp_obj_get_int(rx_obj);
    int tx_pin = mp_obj_get_int(tx_obj);
    // Calculate the addition and convert to MicroPython object.
    // Initialize configuration structures using macro initializers
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT((gpio_num_t)tx_pin, (gpio_num_t)rx_pin, TWAI_MODE_LISTEN_ONLY);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();  //Look in the api-reference for other speed sets.
//TWAI_STD_ID_MASK

// Filter IDs 0x355 and 0x313:
// MSG_ID_PYLON MSG_ID_GROWATT
// 0x355 = 0011 0101 0101
// 0x313 = 0011 0001 0011
// AND for acceptance_code
// 0x311 = 0011 0001 0001
//NOT XOR for acceptance_mask 0 - ignore 1 - check it  is bit in acceptance_code
// 0x7B9 = 0111 1011 1001
// To match these two IDs, we need a mask that allows differences in the positions where they differ.

//uint32_t acceptance_code = (MSG_ID_PYLON & MSG_ID_GROWATT);
//Serial.printf("acceptance_code: %lx", acceptance_code);
//uint32_t acceptance_mask = (MSG_ID_PYLON ^ MSG_ID_GROWATT);
//acceptance_mask = ~(acceptance_mask);
//acceptance_mask = (acceptance_mask & 0x0FFF);
//Serial.printf(" acceptance_mask: %lx", acceptance_mask);

// twai_filter_config_t f_config;
// f_config.single_filter = true;  // Use a single filter mode
// f_config.acceptance_code = acceptance_code;  // Common bits = 0x311
// f_config.acceptance_mask = acceptance_mask;  // Mask to ignore the bits 6,2,1
// f_config.acceptance_code = 0x311;  // Common bits = 0x311
// f_config.acceptance_mask = 0xFB9;  // Mask to ignore the bits 6,2,1

// twai_filter_config_t f_config = {
//                       .acceptance_code = (acceptance_code << 21),
//                       .acceptance_mask = (acceptance_mask << 21),
//                       .single_filter = true
// };

    //twai_filter_config_t f_config = {
    //                    .acceptance_code = (0x311 << 21),
    //                    .acceptance_mask = ~(0x7B9 << 21),
    //                    .single_filter = true
    //};
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    // Install TWAI driver
    if (twai_driver_install(&g_config, &t_config, &f_config) != ESP_OK) return mp_const_false;
    // Start TWAI driver
    if (twai_start() != ESP_OK) return mp_const_false;
    // Reconfigure alerts to detect frame receive, Bus-Off error and RX queue full states
    //uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA | TWAI_ALERT_ERR_PASS | TWAI_ALERT_BUS_ERROR | TWAI_ALERT_RX_QUEUE_FULL;
    uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA;
    if (twai_reconfigure_alerts(alerts_to_enable, NULL) != ESP_OK) return mp_const_false;
    // TWAI driver is now successfully installed and started
    return mp_const_true; // mp_const_false;
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_2(can_driver_init_obj, can_driver_init);

// This is the function which will be called from Python as esp32_soc.read_soc_level() return soc from can PYLONTECH.
static mp_obj_t can_read_soc_level() {
    int counter_error = 0;
    int soc = 123;
    // Check if alert happened
    uint32_t alerts_triggered;
    twai_read_alerts(&alerts_triggered, pdMS_TO_TICKS(POLLING_RATE_MS));
    // Check if message is received
    if (alerts_triggered & TWAI_ALERT_RX_DATA) {
            // One or more messages received. Handle all.
        twai_message_t message;
        while (twai_receive(&message, 0) == ESP_OK) {
           if (!(message.rtr)) {
              int byte_0 = 0;
             // int byte_1 = 0;
              switch (message.identifier)
              {
                case 0x18904001:
                    //DALY https://robu.in/wp-content/uploads/2021/10/Daly-CAN-Communications-Protocol-V1.0-1.pdf
                    byte_0 = message.data[6];
                    break;
                case 0x4210:
                    //DEYE_2_HV
                    byte_0 = message.data[6];
                    break;
                case 0x4211:
                    //DEYE_2_HV
                    byte_0 = message.data[6];
                    break;
                case 0x355:
                    //PYLONTECH
                    byte_0 = message.data[0];
                  //  byte_1 = message.data[1];
                    break;
                case 0x313:
                    //GROWATT
                    byte_0 = message.data[6];
                    break;
                case 0x457:
                    //GOODWE  250kbs
                    byte_0 = message.data[0];
                    break;
                default:
                    byte_0 = 155;
                    break;
              }
              soc = byte_0;
              if (soc != 155) return mp_obj_new_int(soc);
           }
        }
    }
    else return mp_obj_new_int(soc);
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_1(can_read_soc_level_obj, can_read_soc_level);

// Define all attributes of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
static const mp_rom_map_elem_t esp32_soc_module_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_esp32_soc) },
        { MP_ROM_QSTR(MP_QSTR_driver_init), MP_ROM_PTR(&can_driver_init_obj) },
        { MP_ROM_QSTR(MP_QSTR_read_soc_level),    MP_ROM_PTR(&can_read_soc_level_obj) },
};
static MP_DEFINE_CONST_DICT(esp32_soc_module_globals, esp32_soc_module_globals_table);

// Define module object.
const mp_obj_module_t esp32_soc_user_cmodule = {
        .base = { &mp_type_module },
        .globals = (mp_obj_dict_t *)&esp32_soc_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_esp32_soc, esp32_soc_user_cmodule);


#endif // MODULE_CAN_ENABLED