/*
 * tap_state_machine.h
 *
 *  Created on: 14 Jun 2026
 *      Author: rutho
 */

#ifndef TAP_STATE_MACHINE_H_
#define TAP_STATE_MACHINE_H_

uint8_t update_tap_state_machine(_Bool tms);

enum TSM
{
    TEST_LOGIC_RESET,
    RUN_TEST_IDLE,

    SELECT_DR_SCAN,
    CAPTURE_DR,
    SHIFT_DR,
    EXIT1_DR,
    PAUSE_DR,
    EXIT2_DR,
    UPDATE_DR,

    SELECT_IR_SCAN,
    CAPTURE_IR,
    SHIFT_IR,
    EXIT1_IR,
    PAUSE_IR,
    EXIT2_IR,
    UPDATE_IR,

    TAP_STATE_COUNT,
};

#endif /* TAP_STATE_MACHINE_H_ */
