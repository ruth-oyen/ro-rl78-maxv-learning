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
* Creation Date: 21/07/2026
***********************************************************************************************************************/

#ifndef _USER_DEF_H
#define _USER_DEF_H

/***********************************************************************************************************************
User definitions
***********************************************************************************************************************/

/* Start user code for function. Do not edit comment generated here */
#define VERSION (0x00000100U)

#define L 0
#define H 1

extern void timer_10ms(void);

#define CMD_CTRL_GET_TEST	    (0x01U)
#define CMD_CTRL_GET_VERSION	(0x02U)
#define CMD_CTRL_GET_STATUS	    (0x03U)
#define CMD_CTRL_GET_CRC16	    (0x04U)
#define CMD_CTRL_GET_FLOW	    (0x05U)
#define CMD_CTRL_SET_TEST	    (0x11U)
#define CMD_CTRL_SET_STATUS	    (0x13U)
#define CMD_CTRL_SET_CRC16	    (0x14U)
#define CMD_CTRL_SET_FLOW	    (0x15U)

#define CMD_JTAG_FREQUENCY		(0x80U)
#define CMD_JTAG_TRST		    (0x81U)
#define CMD_JTAG_STATE		    (0x82U)
#define CMD_JTAG_ENDDR		    (0x83U)
#define CMD_JTAG_ENDIR		    (0x84U)
#define CMD_JTAG_RUNTEST		(0x85U)
#define CMD_JTAG_SDR		    (0x86U)
#define CMD_JTAG_SDR_TDO	    (0x87U)
#define CMD_JTAG_SIR		    (0x88U)
#define CMD_JTAG_SIR_TDO	    (0x89U)

#define CMD_JTAG_TRST_ABSEN		(0xF0U)
#define CMD_JTAG_TRST_ON		(0xF1U)
#define CMD_JTAG_TRST_OFF		(0xF2U)
#define CMD_JTAG_TRST_Z			(0xF3U)
#define CMD_JTAG_TRST_FORCE		(0xF4U)

#define CMD_IS_JTAG             (0x80U)

#define TMS_OUT                 (P2_bit.no0)
#define TCK_OUT                 (P2_bit.no1)
#define TDI_OUT                 (P2_bit.no2)
#define TDO_IN                  (P2_bit.no3)

#define RTSn					(P1_bit.no4)
#define RTS_GO					(0)
#define RTS_STOP				(1)

typedef struct
{
	uint8_t b0;
	uint8_t b1;
	uint8_t b2;
	uint8_t b3;
} BYTES;

typedef struct
{
	uint16_t w0;
	uint16_t w1;
} WORDS;

typedef union
{
	uint32_t dword;
	WORDS	words;
	BYTES	bytes;
} DATA_EXCHANGE;

typedef struct
{
    uint8_t length; /* Number of P2 bytes in the path. */
    uint8_t start;  /* First P2 byte in tms_pattern. */
} TAP_PATH;

/* End user code. Do not edit comment generated here */
#endif
