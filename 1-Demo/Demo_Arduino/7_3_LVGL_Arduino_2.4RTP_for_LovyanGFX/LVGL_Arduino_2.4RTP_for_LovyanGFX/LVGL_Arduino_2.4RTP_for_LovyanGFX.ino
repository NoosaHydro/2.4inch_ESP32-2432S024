#include <Arduino.h>
#include <lvgl.h>
#include <demos\lv_demos.h>
#define LGFX_USE_V1
#include <LovyanGFX.hpp>

static const uint32_t screenWidth  = 320;
static const uint32_t screenHeight = 480;
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[2][480 * 29]; 

class LGFX : public lgfx::LGFX_Device{
  lgfx::Panel_ST7796  _panel_instance;
  lgfx::Bus_SPI       _bus_instance;
  lgfx::Light_PWM     _light_instance;
  lgfx::Touch_XPT2046 _touch_instance;
//----------------------------------------------------------------------  
public:LGFX(void){{            // バス制御の設定を行います。
  auto cfg = _bus_instance.config();// バス設定用の構造体を取得します。
                               // SPIバスの設定
  cfg.spi_host   = SPI2_HOST;  // 使用するSPIを選択 (VSPI_HOST or HSPI_HOST)
  cfg.spi_mode   = 0;          // SPI通信モードを設定 (0 ~ 3)
  cfg.freq_write = 80000000;   // 送信時のSPIクロック(最大80MHz,80MHzを整数割値に丸め)
  cfg.freq_read  = 16000000;   // 受信時のSPIクロック
  cfg.spi_3wire  = false;      // 受信をMOSIピンで行う場合はtrueを設定
  cfg.use_lock   = true;       // トランザクションロックを使用する場合はtrueを設定
  cfg.dma_channel=  1;         // 使用DMAチャンネル設定(1or2,0=disable)(0=DMA不使用)
  cfg.dma_channel = SPI_DMA_CH_AUTO;  //开启DMA,效果同上
  cfg.pin_sclk   = 14;         // SPIのSCLKピン番号を設定 SCK
  cfg.pin_mosi   = 13;         // SPIのMOSIピン番号を設定 SDI
  cfg.pin_miso   = 12;         // SPIのMISOピン番号を設定 (-1 = disable) SDO
  cfg.pin_dc     =  2;         // SPIのD/C ピン番号を設定 (-1 = disable) RS
  // SDカードと共通のSPIバスを使う場合、MISOは省略せず必ず設定してください。
  _bus_instance.config(cfg);   // 設定値をバスに反映します。
  _panel_instance.setBus(&_bus_instance);// バスをパネルにセットします。
  }
  {                            // 表示パネル制御の設定を行います。
  auto cfg = _panel_instance.config();// 表示パネル設定用の構造体を取得します。
  cfg.pin_cs          =    15; // CS  が接続されているピン番号(-1 = disable)
  cfg.pin_rst         =    -1; // RST が接続されているピン番号(-1 = disable)
  cfg.pin_busy        =    -1; // BUSYが接続されているピン番号(-1 = disable)
  cfg.memory_width    =   320; // ドライバICがサポートしている最大の幅
  cfg.memory_height   =   480; // ドライバICがサポートしている最大の高さ
  cfg.panel_width     =   320; // 実際に表示可能な幅
  cfg.panel_height    =   480; // 実際に表示可能な高さ
  cfg.offset_x        =     0; // パネルのX方向オフセット量
  cfg.offset_y        =     0; // パネルのY方向オフセット量
  cfg.offset_rotation =     0; // 回転方向の値のオフセット 0~7 (4~7は上下反転)
  cfg.dummy_read_pixel=     8; // ピクセル読出し前のダミーリードのビット数
  cfg.dummy_read_bits =     1; // ピクセル外のデータ読出し前のダミーリードのビット数
  cfg.readable        = false; // データ読出しが可能な場合 trueに設定
  cfg.invert          = false; // パネルの明暗が反転場合 trueに設定
  cfg.rgb_order       = false; // パネルの赤と青が入れ替わる場合 trueに設定 ok
  cfg.dlen_16bit      = false; // データ長16bit単位で送信するパネル trueに設定
  cfg.bus_shared      = false; // SDカードとバスを共有 trueに設定
  _panel_instance.config(cfg);
  }
  { // バックライト制御の設定を行います。(必要なければ削除）
  auto cfg = _light_instance.config();// バックライト設定用の構造体を取得します。
  cfg.pin_bl = 27;             // バックライトが接続されているピン番号 BL
  cfg.invert = false;          // バックライトの輝度を反転させる場合 true
  cfg.freq   = 44100;          // バックライトのPWM周波数
  cfg.pwm_channel = 7;         // 使用するPWMのチャンネル番号
  _light_instance.config(cfg);
  _panel_instance.setLight(&_light_instance);//バックライトをパネルにセットします。
  }
  { // タッチスクリーン制御の設定を行います。（必要なければ削除）
  auto cfg = _touch_instance.config();
  cfg.x_min      = 222;    // タッチスクリーンから得られる最小のX値(生の値) 360  222
  cfg.x_max      = 3367;   // タッチスクリーンから得られる最大のX値(生の値) 4200 3367
  cfg.y_min      = 192;    // タッチスクリーンから得られる最小のY値(生の値) 180  192
  cfg.y_max      = 3732;   // タッチスクリーンから得られる最大のY値(生の値) 3900 3732
  cfg.pin_int    = -1;     // INTが接続されているピン番号, TP IRQ
  cfg.bus_shared = true;   // 画面と共通のバスを使用している場合 trueを設定
  cfg.offset_rotation = 6; // 表示とタッチの向きのが一致しない場合の調整 0~7の値で設定 4
  // SPI接続の場合
  cfg.spi_host = SPI2_HOST;// 使用するSPIを選択 (HSPI_HOST or VSPI_HOST)
  cfg.freq = 1000000;      // SPIクロックを設定
  cfg.pin_sclk = 14;       // SCLKが接続されているピン番号, TP CLK
  cfg.pin_mosi = 13;       // MOSIが接続されているピン番号, TP DIN
  cfg.pin_miso = 12;       // MISOが接続されているピン番号, TP DOUT
  cfg.pin_cs   = 33;       // CS  が接続されているピン番号, TP CS
  _touch_instance.config(cfg);
  _panel_instance.setTouch(&_touch_instance);  // タッチスクリーンをパネルにセットします。
  }
  setPanel(&_panel_instance);// 使用するパネルをセットします。
  }
};

LGFX tft; // 準備したクラスのインスタンスを作成します。

//=====================================================================
// Display flushing
void my_disp_flush( lv_disp_drv_t *disp, const lv_area_t *area, 
                    lv_color_t *color_p) {
  if (tft.getStartCount()==0){  // Run if not already started
    tft.startWrite();
  } 
  tft.pushImageDMA( area->x1
                  , area->y1
                  , area->x2 - area->x1 + 1
                  , area->y2 - area->y1 + 1
                  , ( lgfx::swap565_t* )&color_p->full);
  lv_disp_flush_ready(disp);
}

void init_display() {
  static lv_disp_drv_t disp_drv;     // Descriptor of a display driver
  lv_disp_drv_init(&disp_drv);       // Basic initialization
  disp_drv.flush_cb = my_disp_flush; // Set your driver function
  disp_drv.draw_buf = &draw_buf;     // Assign the buffer
  disp_drv.hor_res  = screenWidth;   // horizontal resolution
  disp_drv.ver_res  = screenHeight;  // vertical resolution
  lv_disp_drv_register(&disp_drv);   // Finally register the driver
  lv_disp_set_bg_color(NULL,lv_color_hex(0x0000));// background black
}

//===================================================================== 
void my_touchpad_read( lv_indev_drv_t * indev_driver, 
                       lv_indev_data_t * data ){
  uint16_t touchX, touchY;
  bool touched = tft.getTouch( &touchX, &touchY);
  Serial.print(touchX);Serial.print(" ");Serial.println(touchY);
  if(touched){
    if(touchX < screenWidth && touchY < screenHeight){
      data->state = LV_INDEV_STATE_PR;
      data->point.x = touchX;
      data->point.y = touchY;
      Serial.printf("%d,%d\n", touchX, touchY);
    }
    else{ data->state = LV_INDEV_STATE_REL;}
  }
}

//Initialize the input device driver
void init_touch() {
  static lv_indev_drv_t indev_drv;
  lv_indev_drv_init(&indev_drv);
  indev_drv.type = LV_INDEV_TYPE_POINTER;
  indev_drv.read_cb = my_touchpad_read;
  lv_indev_drv_register(&indev_drv);
}

//=====================================================================
void setup(){
  adc_power_acquire(); // Bug fixes for GPIO39 and GPIO36
  Serial.begin(115200);
  tft.begin();
  tft.setRotation(0);       // USB Right 1
//tft.setRotation(3);       // USB Left  3
  tft.setBrightness(200);
  tft.setSwapBytes(true);
  lv_init();
  lv_disp_draw_buf_init(&draw_buf,buf[0],buf[1],480*29);
  init_display();
  init_touch();
  tft.fillScreen(0x0000);         // 黑
  delay(500);
  tft.fillScreen(0xF800);         // 红
  delay(500);
  tft.fillScreen(0x07E0);         // 绿
  delay(500);
  tft.fillScreen(0x001F);         // 蓝
  delay(500);
  touch_calibrate();//屏幕校准
//  tft.clear(0x0000);         // 黑
//  delay(1000);
//  tft.clear(0xF800);         // 红
//  delay(1000);
//  tft.clear(0x07E0);         // 绿
//  delay(1000);
//  tft.clear(0x001F);         // 蓝
//  delay(1000);
  
  //lv_demo_music();            // lv_demo_music
  //lv_demo_keypad_encoder();   // lv_demo_keypad_encoder
  //lv_demo_benchmark();        // lv_demo_benchmark
  //lv_demo_stress();           // lv_demo_stress
  lv_demo_widgets();            // lv_demo_widget *** NG ***
}

//=====================================================================
void loop(){
  lv_timer_handler(); delay(5);
}
//=====================================================================
void touch_calibrate()//屏幕校准
{
  uint16_t calData[5];
  uint8_t calDataOK = 0;

  //校准
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(20, 0);
  tft.setTextFont(2);
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);

  tft.println("按指示触摸角落");

  tft.setTextFont(1);
  tft.println();

  tft.calibrateTouch(calData, TFT_MAGENTA, TFT_BLACK, 15);

  Serial.println(); Serial.println();
  Serial.println("//在setup()中使用此校准代码:");
  Serial.print("uint16_t calData[5] = ");
  Serial.print("{ ");

  for (uint8_t i = 0; i < 5; i++)
  {
    Serial.print(calData[i]);
    if (i < 4) Serial.print(", ");
  }

  Serial.println(" };");
  Serial.print("  tft.setTouch(calData);");
  Serial.println(); Serial.println();

  tft.fillScreen(TFT_BLACK);
  
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.println("XZ OK!");
  tft.println("Calibration code sent to Serial port.");

}
