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
* Creation Date: 29/06/2026
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
#include "string.h"
#include "crc8.h"
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

FRAME rx_buf;
FRAME tx_buf;
volatile ERROR_STATUS error_status;
volatile uint8_t rxd_timer;
volatile _Bool txd_done;

/* End user code. Do not edit comment generated here */
void R_MAIN_UserInit(void);

/***********************************************************************************************************************
* Function Name: main
* Description  : This function implements main function.
* Arguments    : None
* Return Value : None
***********************************************************************************************************************/
void main(void)
{
    R_MAIN_UserInit();
    /* Start user code. Do not edit comment generated here */
    while (1U)
    {
    	idle();
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
	R_UART0_Receive(rx_buf.raw, sizeof(rx_buf.raw));
	R_TAU0_Channel0_Start();
    EI();
    /* End user code. Do not edit comment generated here */
}

/* Start user code for adding. Do not edit comment generated here */
void uart0_callback_sendend(void)
{
	R_UART0_Receive(rx_buf.raw, sizeof(rx_buf.raw));
	txd_done = 1;
}

void timer_1ms(void)
{
	static uint16_t cnt;
	EI();
	rxd_timer++;
}

void idle(void)
{
	static JTAG_PORT jtag_port;
	static enum MAIN main;
	static uint8_t bit_pos;
	switch(main)
    {
        case IDLE:
			rxd_timer = 0;
			txd_done  = 0;
			if(uart0_rx_count() >= 1)
			{
				main = WAIT_RX;
			}
			break;

        case WAIT_RX:
			if(rxd_timer > RXD_TIMEOUT)
			{
				error_status.error |= error_status.rxb_timeout_error |= 1;
				main = ERROR;
			}
			else if(uart0_rx_count() >= sizeof(FRAME))
			{
		        main = FRAME_CHECK;
			}
			break;
		
        case FRAME_CHECK:
			if(crc8(rx_buf.raw, sizeof(FRAME)-1) != rx_buf.common.crc)
			{
				error_status.error |= error_status.rxb_crc_error |= 1;
				main = ERROR;
			}
			else if(rx_buf.common.mode == 0)
			{ //JTAG
				if(rx_buf.jtag.length_minus_1 == 0) main = JTAG_LAST;
				else                                main = JTAG_LOOP;
			}
			else
			{ //CONTROL
		        main = CONTROL;
			}

			memset(&tx_buf, 0, sizeof(tx_buf));
			tx_buf.raw[0] = rx_buf.raw[0];
			bit_pos = 0;
			break;

		break;

        case JTAG_LOOP:
			jtag_port.bit.tms_out = L;
			jtag_port.bit.tck_out = L;
			jtag_port.bit.tdi_out = GET_DATA_BIT(rx_buf.jtag.data, bit_pos);
			P2 = jtag_port.raw; // TCK low 

			jtag_port.bit.tck_out = H;
			SET_DATA_BIT(tx_buf.jtag.data, bit_pos, TDO_IN);
			P1 = update_tap_state_machine(TMS_OUT);
			P2 = jtag_port.raw; // TCK high

			if(bit_pos == (rx_buf.jtag.length_minus_1 - 1)) main = JTAG_LAST;
			else                                            main = JTAG_LOOP;
			bit_pos++;
			break;

        case JTAG_LAST:
			jtag_port.bit.tms_out = rx_buf.jtag.tms;
			jtag_port.bit.tck_out = L;
			jtag_port.bit.tdi_out = GET_DATA_BIT(rx_buf.jtag.data, bit_pos);
			P2 = jtag_port.raw; // TCK low 

			jtag_port.bit.tck_out = H;
			SET_DATA_BIT(tx_buf.jtag.data, bit_pos, TDO_IN);
			P1 = update_tap_state_machine(TMS_OUT);
			P2 = jtag_port.raw; // TCK high

			tx_buf.common.error = error_status.error;
			tx_buf.common.crc = crc8(tx_buf.raw, sizeof(tx_buf.raw) - 1U);
			R_UART0_Send(tx_buf.raw, sizeof(tx_buf.raw));	
			main = WAIT_TX;
			break;

        case CONTROL:
			tx_buf.common.error = error_status.error;
			tx_buf.common.crc = crc8(tx_buf.raw, sizeof(tx_buf.raw) - 1U);
			R_UART0_Send(tx_buf.raw, sizeof(tx_buf.raw));	
			main = WAIT_TX;
			break;

        case ERROR:
			tx_buf.common.error = error_status.error;
			tx_buf.common.crc = crc8(tx_buf.raw, sizeof(tx_buf.raw) - 1U);
			R_UART0_Send(tx_buf.raw, sizeof(tx_buf.raw));	
			main = WAIT_TX;
			break;
		
		case WAIT_TX:
			if(txd_done == 1) main = IDLE;
			break;

    }
}

void uart0_callback_softwareoverrun(uint16_t rx_data)
{
	error_status.error |= error_status.rxb_softwareoverrun_error |= 1;
}

void uart0_callback_error(uint8_t err_type)
{
	error_status.error |= error_status.rxb_overrun_error |= !!(err_type & 0b00000001);
	error_status.error |= error_status.rxb_parity_error  |= !!(err_type & 0b00000010);
	error_status.error |= error_status.rxb_framing_error |= !!(err_type & 0b00000100);
}



/* End user code. Do not edit comment generated here */
