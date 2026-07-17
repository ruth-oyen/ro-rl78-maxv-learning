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
* Creation Date: 28/06/2026
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
uint8_t rx_buf[RX_BUF_SIZE];
uint8_t tx_buf[RX_BUF_SIZE];
enum ERR err = ERR_NONE;
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
    	;
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
	R_UART0_Receive(rx_buf, sizeof(rx_buf));
	R_TAU0_Channel0_Start();
    EI();
    /* End user code. Do not edit comment generated here */
}

/* Start user code for adding. Do not edit comment generated here */
void uart0_callback_receiveend(void)
{
	static uint8_t pre_tck_out;
	pre_tck_out = TCK_OUT;
	P2 = rx_buf[0];
	NOP();
	tx_buf[0] = P2;
	R_UART0_Send(tx_buf, sizeof(tx_buf));
	if((pre_tck_out == L) && (TCK_OUT == H))
	{
		P1 = update_tap_state_machine(TMS_OUT);
	}
}

void uart0_callback_sendend(void)
{
	R_UART0_Receive(rx_buf, sizeof(rx_buf));
}

void timer_1ms(void)
{
	static uint16_t cnt;
	EI();
	if(err != ERR_NONE)
	{
		P1 = cnt & 1 ? err : 0;
	}
	//++P1;
	cnt++;
}


void timer_1us(void)
{
	EI();
}

void uart0_callback_softwareoverrun(uint16_t rx_data)
{
	err = ERR_UART_RX;
}

void uart0_callback_error(uint8_t err_type)
{
	err = ERR_UART_TX;
}



/* End user code. Do not edit comment generated here */
