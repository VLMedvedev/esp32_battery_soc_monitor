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

// int byte_1 = 0;
//              switch (message.identifier)
//              {
//                case 0x18904001:
//                    //DALY https://robu.in/wp-content/uploads/2021/10/Daly-CAN-Communications-Protocol-V1.0-1.pdf
//                    byte_0 = message.data[6];
//                    break;
//                case 0x4210:
//                    //DEYE_2_HV
//                    byte_0 = message.data[6];
//                    break;
//                case 0x4211:
//                    //DEYE_2_HV
//                    byte_0 = message.data[6];
//                    break;
//                case 0x355:
//                    //PYLONTECH
//                    byte_0 = message.data[0];
//                  //  byte_1 = message.data[1];
//                    break;
//                case 0x313:
//                    //GROWATT
//                    byte_0 = message.data[6];
//                    break;
//                case 0x457:
//                    //GOODWE  250kbs
//                    byte_0 = message.data[0];
//                    break;
//                default:
//                    byte_0 = 155;
//                    break;
//              }
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



// Include MicroPython API.
#include "py/runtime.h"
// Used to get the time in the Timer class example.
#include "py/mphal.h"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "driver/twai.h"

// Interval:
#define POLLING_RATE_MS 1000
#define POLLING_SCAN_RATE_MS 100
#define MSG_ID          0x355   //11 bit standard format ID  SOC

#if MODULE_CAN_ENABLED

#include "driver/twai.h"

static int get_error_msg(uint32_t alerts_triggered){
  twai_status_info_t twaistatus;
  twai_get_status_info(&twaistatus);
  int error_number = 0;
    // Handle alerts
  if (alerts_triggered & TWAI_ALERT_ERR_PASS) {
    //("Alert: TWAI controller has become error passive.");
    error_number = 111;
  }
  if (alerts_triggered & TWAI_ALERT_BUS_ERROR) {
//    println("Alert: A (Bit, Stuff, CRC, Form, ACK) error has occurred on the bus.");
//    printf("Bus error count: %lu\n", twaistatus.bus_error_count);
    error_number = 112;
  }
  if (alerts_triggered & TWAI_ALERT_RX_QUEUE_FULL) {
//    Serial.println("Alert: The RX queue is full causing a received frame to be lost.");
//    Serial.printf("RX buffered: %lu\t", twaistatus.msgs_to_rx);
//    Serial.printf("RX missed: %lu\t", twaistatus.rx_missed_count);
//    Serial.printf("RX overrun %lu\n", twaistatus.rx_overrun_count);
    error_number = 113;
  }
  return error_number;
}

// This is the function which will be called from Python as esp32_soc.read_soc_level() return soc from can PYLONTECH.
static mp_obj_t can_scan_msg_id(void) {
    // Check if alert happened
    uint32_t alerts_triggered;
    twai_read_alerts(&alerts_triggered, pdMS_TO_TICKS(POLLING_SCAN_RATE_MS));
    twai_status_info_t twaistatus;
    twai_get_status_info(&twaistatus);
    char separator = ',';
    size_t size_str = 512;
    char out_string[size_str];
    size_t index = 0;
    //sizeof(response)

    if (alerts_triggered & TWAI_ALERT_RX_DATA) {
            // One or more messages received. Handle all.
        twai_message_t message;
        while (twai_receive(&message, 0) == ESP_OK) {
            index += snprintf(out_string + index, size_str - index, "%lx", message.identifier);
            if (!(message.rtr)) {
                for (int i = 0; i < message.data_length_code; i++) {
                    index += snprintf(out_string + index, size_str - index, ",%02x", message.data[i]);
                }
            }
            index += snprintf(out_string + index, size_str - index, "\n");
        }
    }

    return mp_obj_new_str(out_string, index);
}
//mp_obj_t mp_obj_new_str_from_cstr(const char *str); // // accepts null-terminated string, will check utf-8 (raises UnicodeError)
//mp_obj_t mp_obj_new_str(const char *data, size_t len); // will check utf-8 (raises UnicodeError)
//mp_obj_t mp_obj_new_bytes_from_vstr(vstr_t *vstr);
//mp_obj_t mp_obj_new_bytes(const byte *data, size_t len);
//mp_obj_t mp_obj_new_bytearray(size_t n, const void *items);
//mp_obj_t mp_obj_new_bytearray_by_ref(size_t n, void *items);

// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_0(can_scan_msg_id_obj, can_scan_msg_id);

// This is the function which will be called from Python as esp32_soc.read_soc_level() return soc from can PYLONTECH.
static mp_obj_t can_read_msg_id(mp_obj_t identifier_obj, mp_obj_t data_byte_number_obj) {
    int identifier = mp_obj_get_int(identifier_obj);
    int data_byte_number = mp_obj_get_int(data_byte_number_obj);
    // Check if alert happened
    uint32_t alerts_triggered;
    twai_read_alerts(&alerts_triggered, pdMS_TO_TICKS(POLLING_RATE_MS));
    twai_status_info_t twaistatus;
    twai_get_status_info(&twaistatus);
    // Check if message is received
  //  int error_number = get_error_msg(alerts_triggered);
  //  if ( error_number != 0) return mp_obj_new_int(error_number);
    if (alerts_triggered & TWAI_ALERT_RX_DATA) {
            // One or more messages received. Handle all.
        twai_message_t message;
        while (twai_receive(&message, 0) == ESP_OK) {
            int byte_0 = 155;
            if (message.identifier == identifier) {
                if (!(message.rtr)) {
                  byte_0 = message.data[data_byte_number];
                }
                return mp_obj_new_int(byte_0);
           }
        }
    }
    return mp_obj_new_int(123);
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_2(can_read_msg_id_obj, can_read_msg_id);

// This is the function which will be called from Python as esp32_soc.driver_init(rx, tx).
//static mp_obj_t can_driver_init(mp_obj_t rx_obj, mp_obj_t tx_obj, mp_obj_t speed_obj) {
static mp_obj_t can_driver_init(mp_obj_t rx_obj, mp_obj_t tx_obj) {
    // Extract the ints from the micropython input objects.
    // Pins used to connect to CAN bus transceiver:
//#define RX_PIN 37
//#define TX_PIN 39
    int rx_pin = mp_obj_get_int(rx_obj);
    int tx_pin = mp_obj_get_int(tx_obj);
    // Initialize configuration structures using macro initializers
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT((gpio_num_t)tx_pin, (gpio_num_t)rx_pin, TWAI_MODE_LISTEN_ONLY);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();


    twai_driver_uninstall();
    // Install TWAI driver
    if (twai_driver_install(&g_config, &t_config, &f_config) != ESP_OK) return mp_obj_new_int(1);
    // Start TWAI driver
    if (twai_start() != ESP_OK) return mp_obj_new_int(2);
    // Reconfigure alerts to detect frame receive, Bus-Off error and RX queue full states
    //uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA | TWAI_ALERT_ERR_PASS | TWAI_ALERT_BUS_ERROR | TWAI_ALERT_RX_QUEUE_FULL;
    uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA;
    if (twai_reconfigure_alerts(alerts_to_enable, NULL) != ESP_OK) return mp_obj_new_int(3);
    // TWAI driver is now successfully installed and started
    return mp_obj_new_int(4); // mp_const_false;
}
// Define a Python reference to the function above.
static MP_DEFINE_CONST_FUN_OBJ_2(can_driver_init_obj, can_driver_init);

// Define all attributes of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
static const mp_rom_map_elem_t esp32_soc_module_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_esp32_soc) },
        { MP_ROM_QSTR(MP_QSTR_driver_init), MP_ROM_PTR(&can_driver_init_obj) },
        { MP_ROM_QSTR(MP_QSTR_read_soc_level),    MP_ROM_PTR(&can_read_msg_id_obj) },
        { MP_ROM_QSTR(MP_QSTR_scan_can_id),    MP_ROM_PTR(&can_scan_msg_id_obj) },
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