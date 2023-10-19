/*

  DO NOT CHANGE THIS FILE!!

  Do this:-

  1. Copy this file to the NEW filename "my_networks_and_passwords.h"  
  2. Add the following into your .gitignore (so you never accidentally upload your passwords to github):
	   my_networks_and_passwords.h
  3. Edit the new my_networks_and_passwords.h file so it conly contains the following:-

	#define MOBILE_SSID "Your_Hotspit_SSID_Here"
	#define MOBILE_PASSWORD "your hotspot password here"

	#define WIFI_SSID "Your_WiFi SSID Here"
	#define WIFI_PASSWORD "your wifi password here"

  4. Leave this file here - it will use your private passwords, when they are found.

*/

#if defined __has_include
#  if __has_include ("my_networks_and_passwords.h")
#    include "my_networks_and_passwords.h"
#  endif
#endif

#ifndef WIFI_SSID

#define MOBILE_SSID "Your_Hotspit_SSID_Here"
#define MOBILE_PASSWORD "your hotspot password here"

#define WIFI_SSID "Your_WiFi SSID Here"
#define WIFI_PASSWORD "your wifi password here"

#endif
