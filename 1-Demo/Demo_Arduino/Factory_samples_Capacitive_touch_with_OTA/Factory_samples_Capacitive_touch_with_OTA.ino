// Works! Use board "ESP32 Dev Module" - see https://github.com/NoosaHydro/2.4inch_ESP32-2432S024, and a USB Serial device on the power header.  This is for the ESP32 2.4inch touch display board.

// NOTE!! *Must* be esp32 board version 2.0.14 - DO NOT USE 3.0.alpha2 (gives GPIO errors)

// Must be DIO flash mode, 4mb, core 1 and events 1, "Minimal SPIFFS (1.9MB APP with OTA/190KB SPIFFS)"
// You must flash this the first time using Serial, before you can use OTA.
// You need to copy User_Setup.h into your Arduino/libraries/TFT_eSPI folder for this to work, *, and
// You also need to copy the lv_conf.h file into your Arduino/libraries folder for this to work *
// * Yes, I know that's stupid, but I couldn't figure out how to get the LV_CONF_INCLUDE_SIMPLE stuff working... probably and Arduino bug not supporting preprocessor commands or #define scopes properly?

/* To use Serial, connect a USB TTL Serial adapter to the boards power and programming line as follows:-
 *  
 *  Programmer_Pin        ESP32-2432S024_Pin
 *  5v                    5v (red wire)
 *  GND                   GND (black wire)
 *  Rx                    Tx (yellow wire)
 *  Tx                    Rx (green wire)
 *  
 *  To program, you need to hold down the EN button (bottom), then press and release the RST (top) button (the serial monitor will report "waiting for download") on your COM port
 *  
*/

// This is the same program as the 2.4inch_ESP32-2432S024 ships with, excelt with the attition of:-
// 1. OTA (over the air programming), and
// 2. the LED flashes, and
// 3. demo of backlight dimming - CAUTION - this blocks the radio working.
// 4. show light sensor data - NOTE - does not appear to work; might be wired wrong?

// #define USE_BACKLIGHT_PWM 1 //  CAUTION - this blocks the radio working.

//#define LV_CONF_PATH "./here/"
//#define LV_CONF_INCLUDE_SIMPLE
//#include "lv_conf.h"
//#define LV_CONF_SKIP 1

#include <lvgl.h>
#include <TFT_eSPI.h>
#include "CST820.h"
#include <demos/lv_demos.h>

#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include "networks_and_passwords.h"
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

#include <SerialID.h>  // So we know what code and version is running inside our MCUs - see https://github.com/gitcnd/SerialID
#include "myenv.h" // see recipe.hooks.prebuild.0.pattern=\arduino_prebuild.bat in C:\Users\cnd\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.0.0-alpha2\platform.txt
SerialIDset("\n#\tv1.02j-" __FILE__ "\t" __DATE__ "_" __TIME__ " using " WIFI_SSID " by " ENV_USERNAME " on " ENV_COMPUTERNAME );
const char* hname = "ESP32-LCD-01j";

/*更改屏幕分辨率*/
static const uint16_t screenWidth = 240;
static const uint16_t screenHeight = 320;

// backlight led dimming settings for ledcAttachPin
int freq = 2000;    // frequency
int channel = 0;    // aisle
int resolution = 8;   // Resolution
#define BACKLIGHT_PIN 27
#define LIGHT_SENSOR_PIN 34

/*定义触摸屏引脚*/
#define I2C_SDA 33
#define I2C_SCL 32
#define TP_RST 25
#define TP_INT 21

static lv_disp_draw_buf_t draw_buf;
static lv_color_t *buf1;
static lv_color_t *buf2;

TFT_eSPI tft = TFT_eSPI();                      /* TFT实例 */
CST820 touch(I2C_SDA, I2C_SCL, TP_RST, TP_INT); /* 触摸实例 */

#if LV_USE_LOG != 0
/* 串行调试 */
void my_print(const char *buf)
{
    Serial.printf(buf);
    Serial.flush();
}
#endif
//_______________________
void lv_example_btn(void)
{
    /*要转换的属性*/
    static lv_style_prop_t props[] = {
        LV_STYLE_TRANSFORM_WIDTH, LV_STYLE_TRANSFORM_HEIGHT, LV_STYLE_TEXT_LETTER_SPACE};

    /*Transition descriptor when going back to the default state.
     *Add some delay to be sure the press transition is visible even if the press was very short*/
    static lv_style_transition_dsc_t transition_dsc_def;
    lv_style_transition_dsc_init(&transition_dsc_def, props, lv_anim_path_overshoot, 250, 100, NULL);

    /*Transition descriptor when going to pressed state.
     *No delay, go to presses state immediately*/
    static lv_style_transition_dsc_t transition_dsc_pr;
    lv_style_transition_dsc_init(&transition_dsc_pr, props, lv_anim_path_ease_in_out, 250, 0, NULL);

    /*Add only the new transition to he default state*/
    static lv_style_t style_def;
    lv_style_init(&style_def);
    lv_style_set_transition(&style_def, &transition_dsc_def);

    /*Add the transition and some transformation to the presses state.*/
    static lv_style_t style_pr;
    lv_style_init(&style_pr);
    lv_style_set_transform_width(&style_pr, 10);
    lv_style_set_transform_height(&style_pr, -10);
    lv_style_set_text_letter_space(&style_pr, 10);
    lv_style_set_transition(&style_pr, &transition_dsc_pr);

    lv_obj_t *btn1 = lv_btn_create(lv_scr_act());
    lv_obj_align(btn1, LV_ALIGN_CENTER, 0, -80);
    lv_obj_add_style(btn1, &style_pr, LV_STATE_PRESSED);
    lv_obj_add_style(btn1, &style_def, 0);

    lv_obj_t *label = lv_label_create(btn1);
    lv_label_set_text(label, "btn1");

    /*Init the style for the default state*/
    static lv_style_t style;
    lv_style_init(&style);

    lv_style_set_radius(&style, 3);

    lv_style_set_bg_opa(&style, LV_OPA_100);
    lv_style_set_bg_color(&style, lv_palette_main(LV_PALETTE_BLUE));
    lv_style_set_bg_grad_color(&style, lv_palette_darken(LV_PALETTE_BLUE, 2));
    lv_style_set_bg_grad_dir(&style, LV_GRAD_DIR_VER);

    lv_style_set_border_opa(&style, LV_OPA_40);
    lv_style_set_border_width(&style, 2);
    lv_style_set_border_color(&style, lv_palette_main(LV_PALETTE_GREY));

    lv_style_set_shadow_width(&style, 8);
    lv_style_set_shadow_color(&style, lv_palette_main(LV_PALETTE_GREY));
    lv_style_set_shadow_ofs_y(&style, 8);

    lv_style_set_outline_opa(&style, LV_OPA_COVER);
    lv_style_set_outline_color(&style, lv_palette_main(LV_PALETTE_BLUE));

    lv_style_set_text_color(&style, lv_color_white());
    lv_style_set_pad_all(&style, 10);

    /*Init the pressed style*/
    static lv_style_t style_pr_2;
    lv_style_init(&style_pr_2);

    /*Ad a large outline when pressed*/
    lv_style_set_outline_width(&style_pr_2, 30);
    lv_style_set_outline_opa(&style_pr_2, LV_OPA_TRANSP);

    lv_style_set_translate_y(&style_pr_2, 5);
    lv_style_set_shadow_ofs_y(&style_pr_2, 3);
    lv_style_set_bg_color(&style_pr_2, lv_palette_darken(LV_PALETTE_BLUE, 2));
    lv_style_set_bg_grad_color(&style_pr_2, lv_palette_darken(LV_PALETTE_BLUE, 4));

    /*Add a transition to the the outline*/
    static lv_style_transition_dsc_t trans;
    static lv_style_prop_t props2[] = {LV_STYLE_OUTLINE_WIDTH, LV_STYLE_OUTLINE_OPA};
    lv_style_transition_dsc_init(&trans, props2, lv_anim_path_linear, 300, 0, NULL);

    lv_style_set_transition(&style_pr_2, &trans);

    lv_obj_t *btn2 = lv_btn_create(lv_scr_act());
    lv_obj_remove_style_all(btn2); /*Remove the style coming from the theme*/
    lv_obj_add_style(btn2, &style, 0);
    lv_obj_add_style(btn2, &style_pr_2, LV_STATE_PRESSED);
    lv_obj_set_size(btn2, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_center(btn2);

    lv_obj_t *label2 = lv_label_create(btn2);
    lv_label_set_text(label2, "Button");
    lv_obj_center(label2);
}
//_______________________
/* 显示器刷新 */
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p)
{
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    //tft.startWrite();
    tft.pushImageDMA(area->x1, area->y1, w, h, (uint16_t *)color_p);
    //tft.endWrite();

    lv_disp_flush_ready(disp);
}

/*读取触摸板*/
void my_touchpad_read(lv_indev_drv_t *indev_driver, lv_indev_data_t *data)
{

    bool touched;
    uint8_t gesture;
    uint16_t touchX, touchY;

    touched = touch.getTouch(&touchX, &touchY, &gesture);

    if (!touched)
    {
        data->state = LV_INDEV_STATE_REL;
    }
    else
    {
        data->state = LV_INDEV_STATE_PR;

        /*Set the coordinates*/
        data->point.x = touchX;
        data->point.y = touchY;
    }
}



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

void delay_ota(int dly) {
  ArduinoOTA.handle();
  delay(dly);
} // delay_ota

void test_adc() {
  for (int i=0; i<40; i++) {  Serial.println("D pin to A chan: " + String(i) + "=" + String(digitalPinToAnalogChannel(i)));  }  
  
  for (int j=0; j<10; j++) {  
    Serial.println();
    for (int i=0; i<40; i++) {  
      if(digitalPinToAnalogChannel(i) >= 0) {
        Serial.printf("pin(%d)=%u ", i, analogRead(i));
      }
    }          
      Serial.println();
      delay(1000);
  }
} 


void setup()
{
    //Serial.begin(115200); /*初始化串口*/
    SerialIDshow(115200); // starts Serial and shows build info.
    //test_adc();
    setup_ota();

    String LVGL_Arduino = "Hello Arduino! ";
    LVGL_Arduino += String('V') + lv_version_major() + "." + lv_version_minor() + "." + lv_version_patch();

    Serial.println(LVGL_Arduino);
    Serial.println("I am LVGL_Arduino");

    //Initialize GPIO, turn off (1=off) tricolor light
    pinMode(4, OUTPUT); // Red
    pinMode(17, OUTPUT); // Green
    pinMode(16, OUTPUT); // Blue
    digitalWrite(4, 1); // Red
    digitalWrite(16, 1);  // Green
    digitalWrite(17, 1);  // Blue


    lv_init();

#if LV_USE_LOG != 0
    lv_log_register_print_cb(my_print); /* 用于调试的注册打印功能 */
#endif
    pinMode(BACKLIGHT_PIN, OUTPUT);
    digitalWrite(BACKLIGHT_PIN, LOW);
    tft.begin();        /*初始化*/
    tft.setRotation(0); /* 旋转 */
    tft.initDMA();      /* 初始化DMA */

    touch.begin(); /*初始化触摸板*/
    digitalWrite(BACKLIGHT_PIN, HIGH);
    tft.fillScreen(TFT_RED);      digitalWrite(4, 0);  digitalWrite(16, 1); digitalWrite(17, 1); // red LED too!
    delay_ota(500);
    tft.fillScreen(TFT_GREEN);    digitalWrite(4, 1);  digitalWrite(16, 0); digitalWrite(17, 1); // green LED too!
    delay_ota(500);
    tft.fillScreen(TFT_BLUE);     digitalWrite(4, 1);  digitalWrite(16, 1);  digitalWrite(17, 0); // blue LED too!
    delay_ota(500);
    tft.fillScreen(TFT_BLACK);
    digitalWrite(4, 0);  digitalWrite(16, 0); digitalWrite(17, 0); // white LED
    delay_ota(500);

    buf1 = (lv_color_t *)heap_caps_malloc(sizeof(lv_color_t) * screenWidth * 200 , MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);//screenWidth * screenHeight/2
    buf2 = (lv_color_t *)heap_caps_malloc(sizeof(lv_color_t) * screenWidth * 200 , MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);

    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, screenWidth * 200);

    /*初始化显示*/
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    /*将以下行更改为显示分辨率*/
    disp_drv.hor_res = screenWidth;
    disp_drv.ver_res = screenHeight;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    /*初始化（虚拟）输入设备驱动程序*/
    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = my_touchpad_read;
    lv_indev_drv_register(&indev_drv);

#if 0
    /* 创建简单标签 */
//    lv_obj_t *label = lv_label_create( lv_scr_act() );
//    lv_label_set_text( label, LVGL_Arduino.c_str() );
//    lv_obj_align( label, LV_ALIGN_CENTER, 0, 0 );
     lv_example_btn();
#else
    /* 尝试lv_examples Arduino库中的一个示例
       请确保按照上面所写的内容将其包括在内。
    lv_example_btn_1();
   */

    // uncomment one of these demos
    lv_demo_widgets(); // OK
    //lv_demo_benchmark(); // OK

    //  lv_demo_keypad_encoder();     // works, but I haven't an encoder
    //  lv_demo_music();              // NOK
    //  lv_demo_printer();
    //  lv_demo_stress();             // seems to be OK
#endif

#ifdef USE_BACKLIGHT_PWM
    ledcSetup(channel, freq, resolution); // set channel
#endif    
   // pinMode(LIGHT_SENSOR_PIN,INPUT);
   //pinMode(LIGHT_SENSOR_PIN, INPUT_ANALOG);

    

    Serial.println("Setup done");
    tft.startWrite();
}

void dim_bl() {
  ledcAttachPin(BACKLIGHT_PIN, channel);

  // gradually darken
  for (int dutyCycle = 0; dutyCycle <= 255; dutyCycle = dutyCycle + 5)
  {
    ledcWrite(channel, dutyCycle);  // output PWM
    delay_ota(100);
  }

  // gradually brighten
   for (int dutyCycle = 255; dutyCycle >= 0; dutyCycle = dutyCycle - 5)
  {
    ledcWrite(channel, dutyCycle);  // output PWM
    delay_ota(100);
  }  
} // dim_bl

int ctr=0; int loopr=0;
void loop()
{
    lv_timer_handler(); /* 让GUI完成它的工作 */
    delay_ota(5);
    if(ctr++>200) {
      ctr=0; loopr++;
      Serial.print("hi "); Serial.println(analogRead(LIGHT_SENSOR_PIN)); //Serial.println(loopr);
      digitalWrite(4, loopr&1); // Red
      digitalWrite(16, loopr&2);  // Green
      digitalWrite(17, loopr&4);  // Blue    
#ifdef USE_BACKLIGHT_PWM
      dim_bl(); // blocks wifi ?
#endif       
    }
}

