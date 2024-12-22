ESP32_SOC_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(ESP32_SOC_MOD_DIR)/modcan_soc.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(ESP32_SOC_MOD_DIR)
