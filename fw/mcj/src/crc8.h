/*
 * crc8.h
 *
 *  Created on: 2023/08/13
 *      Author: y-okubo
 */
#ifndef CRC8_H_
#define CRC8_H_

#include "r_cg_macrodriver.h"
#define USE_CRC8_TABLE
#define CRC8_GP  (0x07) // x8 + x2 + x + 1
extern uint8_t crc8(const uint8_t *, uint8_t);

#endif /* CRC8_H_ */
