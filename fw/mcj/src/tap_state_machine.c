/*
 * tap_state_machine.c
 *
 *  Created on: 14 Jun 2026
 *      Author: rutho
 */

#include "r_cg_macrodriver.h"
#include "tap_state_machine.h"

uint8_t update_tap_state_machine(_Bool tms)
{//TSM:TAP State Machine
    static enum TSM tsm;

    switch(tsm)
    {
        case STATE_TEST_LOGIC_RESET: tsm = tms ? STATE_TEST_LOGIC_RESET : STATE_RUN_TEST_IDLE;  break;
        case STATE_RUN_TEST_IDLE:    tsm = tms ? STATE_SELECT_DR_SCAN   : STATE_RUN_TEST_IDLE;  break;

        case STATE_SELECT_DR_SCAN:   tsm = tms ? STATE_SELECT_IR_SCAN   : STATE_CAPTURE_DR;     break;
        case STATE_CAPTURE_DR:       tsm = tms ? STATE_EXIT1_DR         : STATE_SHIFT_DR;       break;
        case STATE_SHIFT_DR:         tsm = tms ? STATE_EXIT1_DR         : STATE_SHIFT_DR;       break;
        case STATE_EXIT1_DR:         tsm = tms ? STATE_UPDATE_DR        : STATE_PAUSE_DR;       break;
        case STATE_PAUSE_DR:         tsm = tms ? STATE_EXIT2_DR         : STATE_PAUSE_DR;       break;
        case STATE_EXIT2_DR:         tsm = tms ? STATE_UPDATE_DR        : STATE_SHIFT_DR;       break;
        case STATE_UPDATE_DR:        tsm = tms ? STATE_SELECT_DR_SCAN   : STATE_RUN_TEST_IDLE;  break;

        case STATE_SELECT_IR_SCAN:   tsm = tms ? STATE_TEST_LOGIC_RESET : STATE_CAPTURE_IR;     break;
        case STATE_CAPTURE_IR:       tsm = tms ? STATE_EXIT1_IR         : STATE_SHIFT_IR;       break;
        case STATE_SHIFT_IR:         tsm = tms ? STATE_EXIT1_IR         : STATE_SHIFT_IR;       break;
        case STATE_EXIT1_IR:         tsm = tms ? STATE_UPDATE_IR        : STATE_PAUSE_IR;       break;
        case STATE_PAUSE_IR:         tsm = tms ? STATE_EXIT2_IR         : STATE_PAUSE_IR;       break;
        case STATE_EXIT2_IR:         tsm = tms ? STATE_UPDATE_IR        : STATE_SHIFT_IR;       break;
        case STATE_UPDATE_IR:        tsm = tms ? STATE_SELECT_DR_SCAN   : STATE_RUN_TEST_IDLE;  break;
    }

    return tsm;
}
