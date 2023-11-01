
# This file is part of MicroPython M5Stack package
# Copyright (c) 2017 Mika Tuupola
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#
# Project home:
#   https://github.com/tuupola/micropython-m5stacj

from micropython import const

BUTTON_A_PIN = const(39)	# was 39
BUTTON_B_PIN = const(38)	# was 38
BUTTON_C_PIN = const(37)	# was 37
SPEAKER_PIN = const(26)		# was 25

TFT_LED_PIN = const(27)		# was 32
TFT_DC_PIN = const(2)		# was 27
TFT_CS_PIN = const(15)		# was 14
TFT_MOSI_PIN = const(13)	# was 23
TFT_CLK_PIN = const(14)		# was 18
TFT_RST_PIN = const(17)		# was 33
TFT_MISO_PIN = const(12) 	# was 19

# See /home/cnd/Downloads/Arduino/2.4inch_ESP32-2432S024/1-Demo/Demo_Arduino/Factory_samples_Capacitive_touch_with_OTA/User_Setup.h

#define ESP32_DMA
#define TFT_MISO 12
#define TFT_MOSI 13 // In some display driver board, it might be written as "SDA" and so on.
#define TFT_SCLK 14
#define TFT_CS   15  // Chip select control pin
#define TFT_DC   2  // Data Command control pin
#define TFT_RST  -1  // Reset pin (could connect to Arduino RESET pin)
#define TFT_BL   27  // LED back-light

#define TOUCH_CS 33     // Chip select pin (T_CS) of touch screen


#define SPI_FREQUENCY  55000000 // STM32 SPI1 only (SPI2 maximum is 27MHz)
# Optional reduced SPI frequency for reading TFT
#define SPI_READ_FREQUENCY  20000000
# The XPT2046 requires a lower SPI clock rate of 2.5MHz so we define that here:
#define SPI_TOUCH_FREQUENCY  2500000  //2500000
