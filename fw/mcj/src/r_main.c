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
* File Name    : r_main.c
* Version      : CodeGenerator for RL78/G12 V2.04.10.01 [13 Aug 2025]
* Device(s)    : R5F10268
* Tool-Chain   : CCRL
* Description  : This file implements main function.
* Creation Date: 05/07/2026
***********************************************************************************************************************/

/***********************************************************************************************************************
Includes
***********************************************************************************************************************/
#include "r_cg_macrodriver.h"
#include "r_cg_cgc.h"
#include "r_cg_port.h"
#include "r_cg_serial.h"
#include "r_cg_timer.h"
/* Start user code for include. Do not edit comment generated here */
#include "stdbool.h"
#include "tap_state_machine.h"
/* End user code. Do not edit comment generated here */
#include "r_cg_userdefine.h"

/***********************************************************************************************************************
Pragma directive
***********************************************************************************************************************/
/* Start user code for pragma. Do not edit comment generated here */
/* End user code. Do not edit comment generated here */

/***********************************************************************************************************************
Global variables and functions
***********************************************************************************************************************/
/* Start user code for global. Do not edit comment generated here */

volatile uint8_t rxd_timer;
volatile _Bool	 tx_ring_done = 1;

// 256 byte rx_ring buffer
static volatile uint8_t rx_ring_buf[256];
static volatile uint8_t rx_ring_read_pos;
static volatile uint8_t rx_ring_write_pos;
static volatile uint16_t rx_ring_count;

// 16 byte tx_ring buffer
static volatile uint8_t tx_ring_buf[16];
static volatile uint8_t tx_ring_read_pos;
static volatile uint8_t tx_ring_write_pos;
static volatile uint16_t tx_ring_count;

// JTAG
static uint8_t state;
static uint8_t state_to;
static uint8_t state_end_dr;
static uint8_t state_end_ir;

const uint8_t __far crc8_table[256] = { // x8 + x2 + x + 1, left shift
    0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15, 0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D,
    0x70, 0x77, 0x7E, 0x79, 0x6C, 0x6B, 0x62, 0x65, 0x48, 0x4F, 0x46, 0x41, 0x54, 0x53, 0x5A, 0x5D,
    0xE0, 0xE7, 0xEE, 0xE9, 0xFC, 0xFB, 0xF2, 0xF5, 0xD8, 0xDF, 0xD6, 0xD1, 0xC4, 0xC3, 0xCA, 0xCD,
    0x90, 0x97, 0x9E, 0x99, 0x8C, 0x8B, 0x82, 0x85, 0xA8, 0xAF, 0xA6, 0xA1, 0xB4, 0xB3, 0xBA, 0xBD,
    0xC7, 0xC0, 0xC9, 0xCE, 0xDB, 0xDC, 0xD5, 0xD2, 0xFF, 0xF8, 0xF1, 0xF6, 0xE3, 0xE4, 0xED, 0xEA,
    0xB7, 0xB0, 0xB9, 0xBE, 0xAB, 0xAC, 0xA5, 0xA2, 0x8F, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9D, 0x9A,
    0x27, 0x20, 0x29, 0x2E, 0x3B, 0x3C, 0x35, 0x32, 0x1F, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0D, 0x0A,
    0x57, 0x50, 0x59, 0x5E, 0x4B, 0x4C, 0x45, 0x42, 0x6F, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7D, 0x7A,
    0x89, 0x8E, 0x87, 0x80, 0x95, 0x92, 0x9B, 0x9C, 0xB1, 0xB6, 0xBF, 0xB8, 0xAD, 0xAA, 0xA3, 0xA4,
    0xF9, 0xFE, 0xF7, 0xF0, 0xE5, 0xE2, 0xEB, 0xEC, 0xC1, 0xC6, 0xCF, 0xC8, 0xDD, 0xDA, 0xD3, 0xD4,
    0x69, 0x6E, 0x67, 0x60, 0x75, 0x72, 0x7B, 0x7C, 0x51, 0x56, 0x5F, 0x58, 0x4D, 0x4A, 0x43, 0x44,
    0x19, 0x1E, 0x17, 0x10, 0x05, 0x02, 0x0B, 0x0C, 0x21, 0x26, 0x2F, 0x28, 0x3D, 0x3A, 0x33, 0x34,
    0x4E, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5C, 0x5B, 0x76, 0x71, 0x78, 0x7F, 0x6A, 0x6D, 0x64, 0x63,
    0x3E, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2C, 0x2B, 0x06, 0x01, 0x08, 0x0F, 0x1A, 0x1D, 0x14, 0x13,
    0xAE, 0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB, 0x96, 0x91, 0x98, 0x9F, 0x8A, 0x8D, 0x84, 0x83,
    0xDE, 0xD9, 0xD0, 0xD7, 0xC2, 0xC5, 0xCC, 0xCB, 0xE6, 0xE1, 0xE8, 0xEF, 0xFA, 0xFD, 0xF4, 0xF3
};

typedef struct
{
    uint8_t len;   /* Number of P2 bytes in the path. */
    uint8_t start; /* First P2 byte in tms_pattern. */
} TAP_PATH;

/* TMS sequence: 111110101001100110110101011110111100 */
static const uint8_t __far tms_pattern[] =
{
    0x01, 0x03, 0x01, 0x03, 0x01, 0x03, 0x01, 0x03,
    0x01, 0x03, 0x00, 0x02, 0x01, 0x03, 0x00, 0x02,
    0x01, 0x03, 0x00, 0x02, 0x00, 0x02, 0x01, 0x03,
    0x01, 0x03, 0x00, 0x02, 0x00, 0x02, 0x01, 0x03,
    0x01, 0x03, 0x00, 0x02, 0x01, 0x03, 0x01, 0x03,
    0x00, 0x02, 0x01, 0x03, 0x00, 0x02, 0x01, 0x03,
    0x00, 0x02, 0x01, 0x03, 0x01, 0x03, 0x01, 0x03,
    0x01, 0x03, 0x00, 0x02, 0x01, 0x03, 0x01, 0x03,
    0x01, 0x03, 0x01, 0x03, 0x00, 0x02, 0x00, 0x02
};

static const TAP_PATH __far tap_path[TAP_STATE_COUNT][TAP_STATE_COUNT] =
{
    {{ 0, 0}, { 2,10}, { 4,10}, { 6,10}, { 8,14}, { 8,10}, {10,10}, {12,40}, {10,44}, { 6,20}, { 8,20}, {10,20}, {10,28}, {12,34}, {14,34}, {12,28}},
    {{ 6, 0}, { 0, 0}, { 2, 0}, { 4, 8}, { 6,16}, { 6, 8}, { 8, 8}, {10, 8}, { 8,32}, { 4, 0}, { 6, 6}, { 8,22}, { 8, 6}, {10, 6}, {12, 6}, {10,30}},
    {{ 4, 0}, { 6, 6}, { 0, 0}, { 2,10}, { 4,18}, { 4,10}, { 6,10}, { 8,10}, { 6,20}, { 2, 0}, { 4, 8}, { 6,16}, { 6, 8}, { 8, 8}, {10, 8}, { 8,32}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 0, 0}, { 2,10}, { 2, 0}, { 4, 8}, { 6, 8}, { 4, 0}, { 8, 0}, {10, 2}, {12,60}, {12, 2}, {14, 2}, {16, 2}, {14,50}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 8, 4}, { 0, 0}, { 2, 0}, { 4, 8}, { 6, 8}, { 4, 0}, { 8, 0}, {10, 2}, {12,60}, {12, 2}, {14, 2}, {16, 2}, {14,50}},
    {{ 8, 0}, { 4, 8}, { 4, 0}, { 6, 6}, { 6,10}, { 0, 0}, { 2,10}, { 4,10}, { 2, 0}, { 6, 0}, { 8, 4}, {10,62}, {10, 4}, {12, 4}, {14, 4}, {12,52}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 8, 4}, { 4, 8}, { 6, 8}, { 0, 0}, { 2, 0}, { 4, 0}, { 8, 0}, {10, 2}, {12,60}, {12, 2}, {14, 2}, {16, 2}, {14,50}},
    {{ 8, 0}, { 4, 8}, { 4, 0}, { 6, 6}, { 2,10}, { 4,10}, { 6,10}, { 0, 0}, { 2, 0}, { 6, 0}, { 8, 4}, {10,62}, {10, 4}, {12, 4}, {14, 4}, {12,52}},
    {{ 6, 0}, { 2,10}, { 2, 0}, { 4, 8}, { 6,16}, { 6, 8}, { 8, 8}, {10, 8}, { 0, 0}, { 4, 0}, { 6, 6}, { 8,22}, { 8, 6}, {10, 6}, {12, 6}, {10,30}},
    {{ 2, 0}, { 4, 8}, { 6, 8}, { 8, 8}, {10,12}, {10, 8}, {12, 8}, {14,38}, {12,42}, { 0, 0}, { 2,10}, { 4,18}, { 4,10}, { 6,10}, { 8,10}, { 6,20}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 8, 4}, {10,62}, {10, 4}, {12, 4}, {14, 4}, {12,52}, { 8, 0}, { 0, 0}, { 2,10}, { 2, 0}, { 4, 8}, { 6, 8}, { 4, 0}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 8, 4}, {10,62}, {10, 4}, {12, 4}, {14, 4}, {12,52}, { 8, 0}, {10, 2}, { 0, 0}, { 2, 0}, { 4, 8}, { 6, 8}, { 4, 0}},
    {{ 8, 0}, { 4, 8}, { 4, 0}, { 6, 6}, { 8,22}, { 8, 6}, {10, 6}, {12, 6}, {10,30}, { 6, 0}, { 8, 4}, { 6,10}, { 0, 0}, { 2,10}, { 4,10}, { 2, 0}},
    {{10, 0}, { 6, 6}, { 6, 0}, { 8, 4}, {10,62}, {10, 4}, {12, 4}, {14, 4}, {12,52}, { 8, 0}, {10, 2}, { 4, 8}, { 6, 8}, { 0, 0}, { 2, 0}, { 4, 0}},
    {{ 8, 0}, { 4, 8}, { 4, 0}, { 6, 6}, { 8,22}, { 8, 6}, {10, 6}, {12, 6}, {10,30}, { 6, 0}, { 8, 4}, { 2,10}, { 4,10}, { 6,10}, { 0, 0}, { 2, 0}},
    {{ 6, 0}, { 2,10}, { 2, 0}, { 4, 8}, { 6,16}, { 6, 8}, { 8, 8}, {10, 8}, { 8,32}, { 4, 0}, { 6, 6}, { 8,22}, { 8, 6}, {10, 6}, {12, 6}, { 0, 0}}
};

typedef struct
{
	uint8_t b0;
	uint8_t b1;
	uint8_t b2;
	uint8_t b3;
} BYTES;

struct
{
	struct
	{// User-defined value
		union
		{
			uint32_t dword;
			BYTES	 bytes;
		} u;
	} udv;

	struct
	{// Version
		union
		{
			uint32_t dword;
			BYTES 	 bytes;
		} u;
	} ver;

	struct
	{// Status
		union
		{
			uint32_t dword;
			BYTES 	 bytes;
			struct
			{
				uint8_t err_invalid_command :1;
				uint8_t err_rx_crc8:1;
				uint8_t err_rx_ring_overflow:1;
			} bits;
		} u;
	} sts;

	struct
	{// CRC16
		union
		{
			uint32_t dword;
			BYTES 	 bytes;
			struct
			{
				uint16_t tx_crc16;
				uint16_t rx_crc16;
			} crc;
		} u;
	} crc;

	struct
	{
		union
		{
			uint32_t dword;
			BYTES	 bytes;
		}u;
	} flw;
} reg;

struct
{
	union
	{
		uint32_t dword;
		BYTES	bytes;
	}u;
} rxd, txd;

/* End user code. Do not edit comment generated here */
void R_MAIN_UserInit(void);

/***********************************************************************************************************************
* Function Name: main
* Description  : This function implements main function.
* Arguments    : None
* Return Value : None
***********************************************************************************************************************/

uint8_t get(void)
{
	uint8_t res;
	while(rx_ring_count==0);
	DI(); res = rx_ring_buf[rx_ring_read_pos]; rx_ring_read_pos++; rx_ring_count--; EI();
	return res;
}

#define SET_TXRING(dat)	\
	while(tx_ring_count >= sizeof(tx_ring_buf)); \
	DI(); tx_ring_buf[tx_ring_write_pos] = dat ; tx_ring_write_pos = (tx_ring_write_pos + 1U) & 0x0FU; tx_ring_count++; EI();

void main(void)
{
    R_MAIN_UserInit();
    /* Start user code. Do not edit comment generated here */
	{	
		uint8_t i, len, start;
		static uint8_t cmd;
		static uint8_t rx_crc8, rx_crc8_calc, tx_crc8_calc;
		
		reg.ver.u.dword = VERSION;

 		while (1U)
  		{
			cmd = get();
			P4_bit.no1 = 1;

			if(!(CMD_IS_JTAG & cmd))
			{//CTRL
				rxd.u.bytes.b0 = get();
				rxd.u.bytes.b1 = get();
				rxd.u.bytes.b2 = get();
				rxd.u.bytes.b3 = get();
				rx_crc8 = get();

				rx_crc8_calc = 0x00;
				rx_crc8_calc = crc8_table[rx_crc8_calc ^ cmd];
				rx_crc8_calc = crc8_table[rx_crc8_calc ^ rxd.u.bytes.b0];
				rx_crc8_calc = crc8_table[rx_crc8_calc ^ rxd.u.bytes.b1];
				rx_crc8_calc = crc8_table[rx_crc8_calc ^ rxd.u.bytes.b2];
				rx_crc8_calc = crc8_table[rx_crc8_calc ^ rxd.u.bytes.b3];

				SET_TXRING(cmd);
				if(tx_ring_done)
				{
					DI();
					tx_ring_done = 0;
					TXD0 = tx_ring_buf[tx_ring_read_pos];
   		     		tx_ring_read_pos = (tx_ring_read_pos + 1U) & 0x0FU;
        			tx_ring_count--;
					EI();
				}

				if(rx_crc8 != rx_crc8_calc)
				{
					reg.sts.u.bits.err_rx_crc8 = 1;
					txd.u.dword	= 0xFFFFFFFFU;
				}
				else
				{
					txd.u.dword	= 0x00000000U;
					switch(cmd)
					{
						// CTRL GET COMMANDS
						case CMD_CTRL_GET_TEST: 	txd.u.dword	= reg.udv.u.dword; break;
						case CMD_CTRL_GET_VERSION:	txd.u.dword	= reg.ver.u.dword; break;
						case CMD_CTRL_GET_STATUS:	txd.u.dword	= reg.sts.u.dword; break;
						case CMD_CTRL_GET_CRC16:	txd.u.dword	= reg.crc.u.dword; break;
						case CMD_CTRL_GET_FLOW:		txd.u.dword	= reg.flw.u.dword; break;

						// CTRL SET COMMANDS
						case CMD_CTRL_SET_TEST:		reg.udv.u.dword  =  rxd.u.dword; break;
						case CMD_CTRL_SET_STATUS:	DI(); reg.sts.u.dword &= ~rxd.u.dword; EI(); break;
						case CMD_CTRL_SET_CRC16:	reg.crc.u.dword  =  rxd.u.dword; break;
						case CMD_CTRL_SET_FLOW:		reg.flw.u.dword  =  rxd.u.dword; break;
						default: reg.sts.u.bits.err_invalid_command = 1; txd.u.dword = 0xFFFFFFFFU; break;
    				}
				}

				tx_crc8_calc = 0x00;
				tx_crc8_calc = crc8_table[tx_crc8_calc ^ cmd];
				tx_crc8_calc = crc8_table[tx_crc8_calc ^ txd.u.bytes.b0];
				tx_crc8_calc = crc8_table[tx_crc8_calc ^ txd.u.bytes.b1];
				tx_crc8_calc = crc8_table[tx_crc8_calc ^ txd.u.bytes.b2];
				tx_crc8_calc = crc8_table[tx_crc8_calc ^ txd.u.bytes.b3];

				SET_TXRING(txd.u.bytes.b0);
				SET_TXRING(txd.u.bytes.b1);
				SET_TXRING(txd.u.bytes.b2);
				SET_TXRING(txd.u.bytes.b3);
				SET_TXRING(tx_crc8_calc);
       
				if(tx_ring_done)
				{
					DI();
					tx_ring_done = 0;
					TXD0 = tx_ring_buf[tx_ring_read_pos];
   		     		tx_ring_read_pos = (tx_ring_read_pos + 1U) & 0x0FU;
        			tx_ring_count--;
					EI();
				}
			}
			else
			{//JTAG
				switch(cmd)
				{
					case CMD_JTAG_FREQUENCY:
						break; // ignored in this version

					case CMD_JTAG_TRST:	
						update_tap_state_machine(H); P2 = 0b00000001; P2 = 0b00000011; //TMS=1 TCK=0->1
						update_tap_state_machine(H); P2 = 0b00000001; P2 = 0b00000011; //TMS=1 TCK=0->1
						update_tap_state_machine(H); P2 = 0b00000001; P2 = 0b00000011; //TMS=1 TCK=0->1
						update_tap_state_machine(H); P2 = 0b00000001; P2 = 0b00000011; //TMS=1 TCK=0->1
						update_tap_state_machine(H); P2 = 0b00000001; P2 = 0b00000011; //TMS=1 TCK=0->1
						state = 0;
						P1    = state;
						break;

					case CMD_JTAG_STATE:	
						state_to = get(); 
			            len      = tap_path[state][state_to].len;
						start    = state;
			            for(i=0; i < len; i++)
						{
							P2 = tms_pattern[tap_path[start][state_to].start + i];
							if(P2_bit.no1) P1 = state = update_tap_state_machine(P2_bit.no0);
						}
						break;

					case CMD_JTAG_ENDDR:
						state_end_dr = get(); 
						break;

					case CMD_JTAG_ENDIR:
						state_end_ir = get();
						break;

					case CMD_JTAG_RUNTEST:
						break;

					case CMD_JTAG_SDR:	
						break;

					case CMD_JTAG_SIR:
						break;
				}
			}

			P4_bit.no1 = 0;
   		}
	}
    /* End user code. Do not edit comment generated here */
}

/***********************************************************************************************************************
* Function Name: R_MAIN_UserInit
* Description  : This function adds user code before implementing main function.
* Arguments    : None
* Return Value : None
***********************************************************************************************************************/
void R_MAIN_UserInit(void)
{
    /* Start user code. Do not edit comment generated here */
	R_UART0_Start();
	R_TAU0_Channel0_Start();
    EI();
    /* End user code. Do not edit comment generated here */
}

/* Start user code for adding. Do not edit comment generated here */
#pragma interrupt uart0_rx_interrupt(vect=INTSR0)
static void __near uart0_rx_interrupt(void)
{ //set_rx_ring_buf()
	if (rx_ring_count < sizeof(rx_ring_buf))
	{
		rx_ring_buf[rx_ring_write_pos] = RXD0;
		rx_ring_write_pos++;
		rx_ring_count++;
	}
	else
	{// Ring Buffer Overflow Error
		reg.sts.u.bits.err_rx_ring_overflow = 1;
	}
}

#pragma interrupt uart0_tx_interrupt(vect=INTST0)
static void __near uart0_tx_interrupt(void)
{
    if (tx_ring_count != 0U)
    {
        TXD0 = tx_ring_buf[tx_ring_read_pos];
        tx_ring_read_pos = (tx_ring_read_pos + 1U) & 0x0FU;
        tx_ring_count--;
    }
	else
	{
		tx_ring_done = 1;
	}
}

void timer_10ms(void)
{
}

/* End user code. Do not edit comment generated here */
