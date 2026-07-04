/***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products.
* No other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws. 
* THIS SOFTWARE IS PROVIDED "AS IS" AND RENESAS MAKES NO WARRANTIES REGARDING THIS SOFTWARE, WHETHER EXPRESS, IMPLIED
* OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
* NON-INFRINGEMENT.  ALL SUCH WARRANTIES ARE EXPRESSLY DISCLAIMED.TO THE MAXIMUM EXTENT PERMITTED NOT PROHIBITED BY
* LAW, NEITHER RENESAS ELECTRONICS CORPORATION NOR ANY OF ITS AFFILIATED COMPANIES SHALL BE LIABLE FOR ANY DIRECT,
* INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES FOR ANY REASON RELATED TO THIS SOFTWARE, EVEN IF RENESAS OR
* ITS AFFILIATES HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
* Renesas reserves the right, without notice, to make changes to this software and to discontinue the availability 
* of this software. By using this software, you agree to the additional terms and conditions found by accessing the 
* following link:
* http://www.renesas.com/disclaimer
*
* Copyright (C) 2011, 2025 Renesas Electronics Corporation. All rights reserved.
***********************************************************************************************************************/

/***********************************************************************************************************************
* File Name    : r_cg_userdefine.h
* Version      : CodeGenerator for RL78/G12 V2.04.10.01 [13 Aug 2025]
* Device(s)    : R5F10268
* Tool-Chain   : CCRL
* Description  : This file includes user definition.
* Creation Date: 30/06/2026
***********************************************************************************************************************/

#ifndef _USER_DEF_H
#define _USER_DEF_H

/***********************************************************************************************************************
User definitions
***********************************************************************************************************************/

/* Start user code for function. Do not edit comment generated here */
#define L 0
#define H 1

extern void uart0_callback_receiveend(void);
extern void uart0_callback_softwareoverrun(uint16_t rx_data);
extern void uart0_callback_error(uint8_t err_type);
extern void timer_1ms(void);
extern void idle(void);
extern uint16_t uart0_rx_count(void);

#define TMS_OUT (P2_bit.no0)
#define TCK_OUT (P2_bit.no1)
#define TDI_OUT (P2_bit.no2)
#define TDO_IN  (P2_bit.no3)
#define RXD_TIMEOUT (2) //ms
#define GET_DATA_BIT(data, bit) (((data)[(bit) >> 3U] >> ((bit) & 7U)) & 1U)
#define SET_DATA_BIT(data, bit, value) ((data)[(bit) >> 3U] |= (uint8_t)(((value) & 1U) << ((bit) & 7U)))

typedef struct
{
    uint8_t error                     : 1;
    uint8_t rxb_softwareoverrun_error : 1;
    uint8_t rxb_overrun_error         : 1;
    uint8_t rxb_parity_error          : 1; // never occurred current spec
    uint8_t rxb_framing_error         : 1;
    uint8_t rxb_timeout_error         : 1;
    uint8_t rxb_crc_error             : 1;
    uint8_t invalid_frame_error       : 1;
} ERROR_STATUS;

#pragma pack
typedef union
{
    uint8_t raw[10]; // lol, I can't find a clean way to avoid hard-coding this 10.

    struct
    {
        uint8_t length_minus_1 : 6;
        uint8_t tms            : 1;
        uint8_t mode           : 1;

        uint8_t data[8];
        uint8_t crc;
    } jtag;

    struct
    {
        uint8_t command  : 6;
        uint8_t reserved : 1;
        uint8_t mode     : 1;

        uint32_t address;
        uint32_t data;
        uint8_t crc;
    } control;
    
    struct
    {
        uint8_t unused0 : 6;
        uint8_t error   : 1;
        uint8_t mode    : 1;
        uint8_t unused1[8];
        uint8_t crc;
    } common;
} FRAME;
#pragma unpack

typedef union
{
    uint8_t raw;
    struct
    {
        uint8_t tms_out : 1; /* P20 */
        uint8_t tck_out : 1; /* P21 */
        uint8_t tdi_out : 1; /* P22 */
        uint8_t tdo_in  : 1; /* P23: input */
        uint8_t unused  : 4;
    } bit;
} JTAG_PORT;

enum MAIN
{
    IDLE,
    WAIT_RX,
    FRAME_CHECK,
    JTAG_LOOP,
    JTAG_LAST,
    CONTROL,
    ERROR,
    WAIT_TX,
};


/* End user code. Do not edit comment generated here */
#endif
