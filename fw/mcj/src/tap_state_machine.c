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
        case TEST_LOGIC_RESET: tsm = tms ? TEST_LOGIC_RESET : RUN_TEST_IDLE; break;
        case RUN_TEST_IDLE:    tsm = tms ? SELECT_DR_SCAN   : RUN_TEST_IDLE; break;

        case SELECT_DR_SCAN:   tsm = tms ? SELECT_IR_SCAN   : CAPTURE_DR; break;
        case CAPTURE_DR:       tsm = tms ? EXIT1_DR         : SHIFT_DR; break;
        case SHIFT_DR:         tsm = tms ? EXIT1_DR         : SHIFT_DR; break;
        case EXIT1_DR:         tsm = tms ? UPDATE_DR        : PAUSE_DR; break;
        case PAUSE_DR:         tsm = tms ? EXIT2_DR         : PAUSE_DR; break;
        case EXIT2_DR:         tsm = tms ? UPDATE_DR        : SHIFT_DR; break;
        case UPDATE_DR:        tsm = tms ? SELECT_DR_SCAN   : RUN_TEST_IDLE; break;

        case SELECT_IR_SCAN:   tsm = tms ? TEST_LOGIC_RESET : CAPTURE_IR; break;
        case CAPTURE_IR:       tsm = tms ? EXIT1_IR         : SHIFT_IR; break;
        case SHIFT_IR:         tsm = tms ? EXIT1_IR         : SHIFT_IR; break;
        case EXIT1_IR:         tsm = tms ? UPDATE_IR        : PAUSE_IR; break;
        case PAUSE_IR:         tsm = tms ? EXIT2_IR         : PAUSE_IR; break;
        case EXIT2_IR:         tsm = tms ? UPDATE_IR        : SHIFT_IR; break;
        case UPDATE_IR:        tsm = tms ? SELECT_DR_SCAN   : RUN_TEST_IDLE; break;
    }

    return tsm;
}
