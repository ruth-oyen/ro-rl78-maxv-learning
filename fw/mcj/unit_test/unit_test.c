#include <stdio.h>

typedef unsigned char uint8_t;

/* Copied from fw/mcj/src/tap_state_machine.[ch]. */
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

    TAP_STATE_COUNT
};

static const char * const tsm_string[] =
{
    "TEST_LOGIC_RESET",
    "RUN_TEST_IDLE",

    "SELECT_DR_SCAN",
    "CAPTURE_DR",
    "SHIFT_DR",
    "EXIT1_DR",
    "PAUSE_DR",
    "EXIT2_DR",
    "UPDATE_DR",

    "SELECT_IR_SCAN",
    "CAPTURE_IR",
    "SHIFT_IR",
    "EXIT1_IR",
    "PAUSE_IR",
    "EXIT2_IR",
    "UPDATE_IR"
};

static enum TSM tsm;

uint8_t update_tap_state_machine(_Bool tms)
{

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


/* Code under test. */
// #define TMS_OUT (P2_bit.no0)
// #define TCK_OUT (P2_bit.no1)
// #define TDI_OUT (P2_bit.no2)
// #define TDO_IN  (P2_bit.no3)

typedef struct
{
    uint8_t len;   /* Number of P2 bytes in the path. */
    uint8_t start; /* First P2 byte in tms_pattern. */
} TAP_PATH;

/* TMS sequence: 111110101001100110110101011110111100 */
static const uint8_t tms_pattern[] =
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

static const TAP_PATH tap_path[TAP_STATE_COUNT][TAP_STATE_COUNT] =
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

int main(void)
{
    int test_count = 0;
    int error_count = 0;
    int passed_count = 0;
    int is_ok;
    int from;
    int to;
    int i;

    union
    {
        uint8_t raw;
        struct
        {
            uint8_t tms_out:1; /* LSB */
            uint8_t tck_out:1;
            uint8_t tdi_out:1; /* not used*/
            uint8_t tdo_in :1; /* not used*/
            uint8_t dummy  :4; /* not used*/
        }bit;
    } P2_current, P2_next;

    for(from = 0; from < TAP_STATE_COUNT; ++from)
    {
        for(to = 0; to < TAP_STATE_COUNT; ++to)
        {

            tsm = from;
            for(i=0; i < tap_path[from][to].len; i+=2)
            {
                /* Each TMS bit is encoded as a TCK-low/TCK-high P2 pair. */
                P2_current.raw = tms_pattern[tap_path[from][to].start + i];
                P2_next.raw    = tms_pattern[tap_path[from][to].start + i + 1];

                if(P2_current.bit.tms_out != P2_next.bit.tms_out) error_count++;
                if((P2_current.bit.tck_out == 0) && (P2_next.bit.tck_out == 1))
                {
                    /* Advance the TAP state on the TCK rising edge. */
                    update_tap_state_machine(P2_current.bit.tms_out);
                }
            }
            is_ok = to == tsm;
            passed_count += is_ok;
            printf("%03d(%2s): %02d, %02d, %02d, from=%-16s, to=%-16s, result=%-16s\n", test_count, is_ok?"OK":"NG", from, to, tsm, tsm_string[from], tsm_string[to], tsm_string[tsm]);
            test_count++;
        }
    }
    printf("Test Count  = %d\n", test_count);
    printf("Passed Count = %d\n", passed_count);
    printf("Error Count = %d\n", error_count);
    return 0;
}
