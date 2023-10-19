// Works! - Use board "ESP32 Dev Module" - see https://github.com/NoosaHydro/2.4inch_ESP32-2432S024 - Muse be DIO flash mode, 4mb, core 1 and events 1, "Minimal SPIFFS (1.9MB APP with OTA/190KB SPIFFS)"
// You must flash this the first time using Serial, before you can use OTA.
/* To use Serial, connect a USB TTL Serial adapter to the boards power and programming line as follows:-
 *  
 *  Programmer_Pin        ESP32-2432S024_Pin
 *  5v                    5v (red wire)
 *  GND                   GND (black wire)
 *  Rx                    Tx (yellow wire)
 *  Tx                    Rx (green wire)
 *  
 *  To program, you need to hold down the EN button (bottom), then press and release the RST (top) button (the serial monitor will report "waiting for download") on your COM port
*/


#include <Arduino.h>

#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include "networks_and_passwords.h"
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

#include <SerialID.h>  // So we know what code and version is running inside our MCUs - see https://github.com/gitcnd/SerialID
SerialIDset("\n#\tv1.01d-" __FILE__ "\t" __DATE__ "_" __TIME__ " using " WIFI_SSID);
const char* hname = "ESP32-LCD-01d";

// led dimming settings for ledcAttachPin
int freq = 2000;    // frequency
int channel = 0;    // aisle
int resolution = 8;   // Resolution

void setup_ota()
{
  WiFi.setHostname(hname); // call before begin
  ArduinoOTA.setHostname(hname); // Replaces the MAC.  i.e.  "ESP32-Dev-MagNav at 172.22.1.42 (ESP32 Dev Module)"
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("Connection Failed! OTA Disabled...");
    return;
    //delay(5000);
    //ESP.restart();
  }

  // Port defaults to 3232
  // ArduinoOTA.setPort(3232);

  // Hostname defaults to esp3232-[MAC]
  // ArduinoOTA.setHostname("myesp32");

  // No authentication by default
  // ArduinoOTA.setPassword("admin");

  // Password can be set with it's md5 value as well
  // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

  ArduinoOTA
    .onStart([]() {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
        type = "sketch";
      else // U_SPIFFS
        type = "filesystem";

      // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
      Serial.println("Start updating " + type);
    })
    .onEnd([]() {
      Serial.println("\nEnd");
    })
    .onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    })
    .onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

  ArduinoOTA.begin();

  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
} // setup_ota

int led = 4; // red
void setup()
{
  SerialIDshow(115200); // starts Serial and shows build info.
  setup_ota();

  //Initialize GPIO, turn off tricolor light
  pinMode(4, OUTPUT);
  pinMode(17, OUTPUT);
  pinMode(16, OUTPUT);
  digitalWrite(4, 0);
  digitalWrite(16, 0);
  digitalWrite(17, 0);
  ledcSetup(channel, freq, resolution); // set channel
  //ledcAttachPin(led, channel);  // Connect the channel to the corresponding pin
}

void delay_ota(int dly) {
  ArduinoOTA.handle();
  delay(dly);
}

int i=0;
void loop()
{
  digitalWrite(4, 0);  // red
  digitalWrite(16, 1);
  digitalWrite(17, 1);
  delay_ota(500);
  digitalWrite(4, 1);
  digitalWrite(16, 0); // green
  digitalWrite(17, 1);
  delay_ota(500);
  digitalWrite(4, 1);
  digitalWrite(16, 1);
  digitalWrite(17, 0); // blue
  delay_ota(500);
  
  digitalWrite(4, 1);
  digitalWrite(16, 0); // Cyan
  digitalWrite(17, 0); 
  delay_ota(500);
  digitalWrite(4, 0);
  digitalWrite(16, 0); // Yellow
  digitalWrite(17, 1);
  delay_ota(500);
  digitalWrite(4, 0);
  digitalWrite(16, 1); // Magenta
  digitalWrite(17, 0);
  delay_ota(500);
  digitalWrite(4, 0);  // white
  digitalWrite(16, 0);
  digitalWrite(17, 0);
  delay_ota(500);
  digitalWrite(4, 1);  // black
  digitalWrite(16, 1);
  digitalWrite(17, 1);
  delay_ota(500);
  ledcAttachPin(led, channel);
  // gradually brighten
   for (int dutyCycle = 255; dutyCycle >= 0; dutyCycle = dutyCycle - 5)
  {
    ledcWrite(channel, dutyCycle);  // output PWM
    delay_ota(100);
  }
  // gradually darken
  for (int dutyCycle = 0; dutyCycle <= 255; dutyCycle = dutyCycle + 5)
  {
    ledcWrite(channel, dutyCycle);  // output PWM
    delay_ota(100);
  }
  delay_ota(500);
  Serial.println(i++);
  ArduinoOTA.handle();

}
