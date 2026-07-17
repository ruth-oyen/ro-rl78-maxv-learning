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
    STATE_TEST_LOGIC_RESET,
    STATE_RUN_TEST_IDLE,

    STATE_SELECT_DR_SCAN,
    STATE_CAPTURE_DR,
    STATE_SHIFT_DR,
    STATE_EXIT1_DR,
    STATE_PAUSE_DR,
    STATE_EXIT2_DR,
    STATE_UPDATE_DR,

    STATE_SELECT_IR_SCAN,
    STATE_CAPTURE_IR,
    STATE_SHIFT_IR,
    STATE_EXIT1_IR,
    STATE_PAUSE_IR,
    STATE_EXIT2_IR,
    STATE_UPDATE_IR,

    TAP_STATE_COUNT,
};

#endif /* TAP_STATE_MACHINE_H_ */
