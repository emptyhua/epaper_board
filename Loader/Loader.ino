#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "epd.h"        // e-Paper driver

const char* ssid = "CubeCloud";
const char* password = "WiFi Passwrod";
const char* imageURL = "http://server-ip/epaper-board.image";
const int imageSize = 640 * 384;
 
void setup(void) {
  // SPI initialization
  pinMode(CS_PIN  , OUTPUT);
  pinMode(RST_PIN , OUTPUT);
  pinMode(DC_PIN  , OUTPUT);
  pinMode(BUSY_PIN,  INPUT);
  SPI.begin();
  
  Serial.begin(115200);
  // Serial.setDebugOutput(true);

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
}

void downloadImage(void) {
  HTTPClient http;
  http.setTimeout(10000);
  http.begin(imageURL);
  Serial.print("[HTTP] GET...\n");
  // start connection and send HTTP header
  int httpCode = http.GET();
  if (httpCode > 0) {
    // HTTP header has been send and Server response header has been handled
    Serial.printf("[HTTP] GET... code: %d\n", httpCode);

    // file found at server
    if (httpCode == HTTP_CODE_OK) {

      // get lenght of document (is -1 when Server sends no Content-Length header)
      int len = http.getSize();
      Serial.printf("[HTTP] response size %d\n", len);
      
      int loadedSize = 0;
      // create buffer for read
      uint8_t buff[512] = { 0 };

      // get tcp stream
      WiFiClient * stream = http.getStreamPtr();

      long start = millis();
      // read all data from server
      while (http.connected() && (len > 0 || len == -1) && millis() - start < 10*1000) {  
        // get available data size
        size_t size = stream->available();
        if (size) {
          int c = stream->readBytes(buff, ((size > sizeof(buff)) ? sizeof(buff) : size));
          for (int i = 0; i < c; i ++) {
            uint8_t bdata = buff[i];
            for (uint8_t j = 0; j < 2 && loadedSize < imageSize; j++) {
              uint8_t cmd = 0;
              for (uint8_t x = 0; x < 2; x++) {
                if (x == 1) {
                  cmd = cmd << 4;
                }
                
                if ((bdata & 0x40) == 0x40) {
                  cmd |= 0x03;
                } else if ((bdata & 0x80) == 0x80) {
                  cmd |= 0x04;
                }
          
                bdata = bdata << 2;
                loadedSize ++;
              }
              EPD_SendData(cmd);
            }
          }

          if (len > 0) {
            len -= c;
          }
        }
        // delay(1);
        yield();
      }

      Serial.println();
      Serial.print("[HTTP] connection closed or file end.\n");
    }
  } else {
    Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void loop(void) {
  //Serial.println("[WiFi] connect");
  //WiFi.mode(WIFI_STA);
  //WiFi.begin(ssid, password);
  
  while ((WiFi.status() != WL_CONNECTED)) {
    yield();
  }
  
  EPD_7in5__init();
  downloadImage();
  EPD_showC();

  //Serial.println("[WiFi] disconnect");
  //WiFi.disconnect();
  //delay(100);
  
  //WiFi.mode(WIFI_OFF);
  //Serial.println("[WiFi] sleep");
  //WiFi.forceSleepBegin();
  //delay(100);
  
  long start = millis();
  while( millis() - start < 2*60*1000){
    yield();
  }
  
  // Serial.println("[WiFi] wake");
  // WiFi.forceSleepWake();
  // delay(100);
}
