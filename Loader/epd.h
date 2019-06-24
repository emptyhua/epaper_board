/**
  ******************************************************************************
    @file    epd.h
    @author  Waveshare Team
    @version V1.0.0
    @date    23-January-2018
    @brief   This file provides e-Paper driver functions
              void EPD_SendCommand(byte command);
              void EPD_SendData(byte data);
              void EPD_WaitUntilIdle();
              void EPD_Send_1(byte c, byte v1);
              void EPD_Send_2(byte c, byte v1, byte v2);
              void EPD_Send_3(byte c, byte v1, byte v2, byte v3);
              void EPD_Send_4(byte c, byte v1, byte v2, byte v3, byte v4);
              void EPD_Send_5(byte c, byte v1, byte v2, byte v3, byte v4, byte v5);
              void EPD_Reset();
              void EPD_dispInit();

             varualbes:
              EPD_dispLoad;                - pointer on current loading function
              EPD_dispIndex;               - index of current e-Paper
              EPD_dispInfo EPD_dispMass[]; - array of e-Paper properties

  ******************************************************************************
*/

#include <SPI.h>


/* SPI pin definition --------------------------------------------------------*/
// SPI pin definition
#define CS_PIN           15
#define RST_PIN          5
#define DC_PIN           4
#define BUSY_PIN         16

/* Pin level definition ------------------------------------------------------*/
#define LOW             0
#define HIGH            1

#define GPIO_PIN_SET   1
#define GPIO_PIN_RESET 0


/* The procedure of sending a byte to e-Paper by SPI -------------------------*/
void EpdSpiTransferCallback(byte data)
{
  digitalWrite(CS_PIN, GPIO_PIN_RESET);
  SPI.transfer(data);
  digitalWrite(CS_PIN, GPIO_PIN_SET);
}

/* Sending a byte as a command -----------------------------------------------*/
void EPD_SendCommand(byte command)
{
  digitalWrite(DC_PIN, LOW);
  EpdSpiTransferCallback(command);
}

/* Sending a byte as a data --------------------------------------------------*/
void EPD_SendData(byte data)
{
  digitalWrite(DC_PIN, HIGH);
  EpdSpiTransferCallback(data);
}

/* Waiting the e-Paper is ready for further instructions ---------------------*/
void EPD_WaitUntilIdle()
{
  //0: busy, 1: idle
  while (digitalRead(BUSY_PIN) == 0) delay(100);
}

/* Send a one-argument command -----------------------------------------------*/
void EPD_Send_1(byte c, byte v1)
{
  EPD_SendCommand(c);
  EPD_SendData(v1);
}

/* Send a two-arguments command ----------------------------------------------*/
void EPD_Send_2(byte c, byte v1, byte v2)
{
  EPD_SendCommand(c);
  EPD_SendData(v1);
  EPD_SendData(v2);
}

/* Send a three-arguments command --------------------------------------------*/
void EPD_Send_3(byte c, byte v1, byte v2, byte v3)
{
  EPD_SendCommand(c);
  EPD_SendData(v1);
  EPD_SendData(v2);
  EPD_SendData(v3);
}

/* Send a four-arguments command ---------------------------------------------*/
void EPD_Send_4(byte c, byte v1, byte v2, byte v3, byte v4)
{
  EPD_SendCommand(c);
  EPD_SendData(v1);
  EPD_SendData(v2);
  EPD_SendData(v3);
  EPD_SendData(v4);
}

/* Send a five-arguments command ---------------------------------------------*/
void EPD_Send_5(byte c, byte v1, byte v2, byte v3, byte v4, byte v5)
{
  EPD_SendCommand(c);
  EPD_SendData(v1);
  EPD_SendData(v2);
  EPD_SendData(v3);
  EPD_SendData(v4);
  EPD_SendData(v5);
}


/* This function is used to 'wake up" the e-Paper from the deep sleep mode ---*/
void EPD_Reset()
{
  digitalWrite(RST_PIN, LOW);
  delay(200);

  digitalWrite(RST_PIN, HIGH);
  delay(200);
}

/* e-Paper initialization functions ------------------------------------------*/
int EPD_7in5__init() 
{
    EPD_Reset();
    EPD_Send_2(0x01, 0x37, 0x00);            //POWER_SETTING 
    EPD_Send_2(0x00, 0xCF, 0x08);            //PANEL_SETTING
    EPD_Send_3(0x06, 0xC7, 0xCC, 0x28);      //BOOSTER_SOFT_START
    EPD_SendCommand(0x4);                    //POWER_ON
    EPD_WaitUntilIdle();
    EPD_Send_1(0x30, 0x3C);                  //PLL_CONTROL
    EPD_Send_1(0x41, 0x00);                  //TEMPERATURE_CALIBRATION
    EPD_Send_1(0x50, 0x77);                  //VCOM_AND_DATA_INTERVAL_SETTING
    EPD_Send_1(0x60, 0x22);                  //TCON_SETTING
    EPD_Send_4(0x61, 0x02, 0x80, 0x01, 0x80);//TCON_RESOLUTION
    EPD_Send_1(0x82, 0x1E);                  //VCM_DC_SETTING: decide by LUT file
    EPD_Send_1(0xE5, 0x03);                  //FLASH MODE  

    EPD_SendCommand(0x10);//DATA_START_TRANSMISSION_1  
    delay(2);
    return 0;
}


/* Show image and turn to deep sleep mode (7.5 and 7.5b e-Paper) -------------*/
void EPD_showC()
{
  // Refresh
  EPD_SendCommand(0x12);//DISPLAY_REFRESH
  delay(100);
  EPD_WaitUntilIdle();

  // Sleep
  EPD_SendCommand(0x02);// POWER_OFF
  EPD_WaitUntilIdle();
  EPD_Send_1(0x07, 0xA5);// DEEP_SLEEP
}
