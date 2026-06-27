# This table is copied manually from the 5M40ZE64 BSDL file.
#
# In production software, BSDL should be parsed automatically because it is the
# official source for the boundary scan register layout. In this learning
# project, the table is written explicitly so you can see the relationship:
#
#     pin name -> boundary scan bit number
#
# Only the I/O cells are listed here. Internal cells are intentionally omitted
# because they are device-internal implementation details and are not needed for
# reading or driving board pins.

IR_LENGTH = 10

OPCODE = {
    "SAMPLE": "0000000101",
    "EXTEST": "0000001111",
    "IDCODE": "0000000110", # Not used here because IDCODE is selected by default after Test-Logic-Reset.
    "BYPASS": "1111111111", # Not used here because this board has only one JTAG device.
}

DR_LENGTH = {
    "SAMPLE": 240,
    "EXTEST": 240,
    "IDCODE": 32,
    "BYPASS": 1, # Not used here.
}

INPUT = {
    "IO1" :  39, "IO2" :  36, "IO3" :  33, "IO4" :  30, "IO5" :  27, "IO7" :  24, "IO9" :  21, "IO10":  12,
    "IO11":   6, "IO12":   3, "IO13":   0, "IO18": 237, "IO19": 234, "IO20": 231, "IO21": 228, "IO22": 225,
    "IO24": 222, "IO25": 219, "IO26": 198, "IO27": 195, "IO28": 192, "IO29": 189, "IO30": 186, "IO31": 183, 
    "IO32": 180, "IO33": 177, "IO34": 171, "IO35": 168, "IO36": 165, "IO37": 162, "IO38": 156, "IO40": 147,
    "IO42": 144, "IO43": 135, "IO44": 132, "IO45": 129, "IO46": 126, "IO47": 123, "IO48": 120, "IO49":  96,
    "IO50":  93, "IO51":  90, "IO52":  87, "IO53":  84, "IO54":  78, "IO55":  72, "IO56":  69, "IO58":  66,
    "IO59":  63, "IO60":  60, "IO61":  57, "IO62":  54, "IO63":  51, "IO64":  42,
}

CONTROL = {
    "IO1" :  40, "IO2" :  37, "IO3" :  34, "IO4" :  31, "IO5" :  28, "IO7" :  25, "IO9" :  22, "IO10":  13,
    "IO11":   7, "IO12":   4, "IO13":   1, "IO18": 238, "IO19": 235, "IO20": 232, "IO21": 229, "IO22": 226,
    "IO24": 223, "IO25": 220, "IO26": 199, "IO27": 196, "IO28": 193, "IO29": 190, "IO30": 187, "IO31": 184,
    "IO32": 181, "IO33": 178, "IO34": 172, "IO35": 169, "IO36": 166, "IO37": 163, "IO38": 157, "IO40": 148,
    "IO42": 145, "IO43": 136, "IO44": 133, "IO45": 130, "IO46": 127, "IO47": 124, "IO48": 121, "IO49":  97,
    "IO50":  94, "IO51":  91, "IO52":  88, "IO53":  85, "IO54":  79, "IO55":  73, "IO56":  70, "IO58":  67,
    "IO59":  64, "IO60":  61, "IO61":  58, "IO62":  55, "IO63":  52, "IO64":  43,
}

OUTPUT = {
    "IO1" :  41, "IO2" :  38, "IO3" :  35, "IO4" :  32, "IO5" :  29, "IO7" :  26, "IO9" :  23, "IO10":  14,
    "IO11":   8, "IO12":   5, "IO13":   2, "IO18": 239, "IO19": 236, "IO20": 233, "IO21": 230, "IO22": 227,
    "IO24": 224, "IO25": 221, "IO26": 200, "IO27": 197, "IO28": 194, "IO29": 191, "IO30": 188, "IO31": 185,
    "IO32": 182, "IO33": 179, "IO34": 173, "IO35": 170, "IO36": 167, "IO37": 164, "IO38": 158, "IO40": 149,
    "IO42": 146, "IO43": 137, "IO44": 134, "IO45": 131, "IO46": 128, "IO47": 125, "IO48": 122, "IO49":  98,
    "IO50":  95, "IO51":  92, "IO52":  89, "IO53":  86, "IO54":  80, "IO55":  74, "IO56":  71, "IO58":  68,
    "IO59":  65, "IO60":  62, "IO61":  59, "IO62":  56, "IO63":  53, "IO64":  44,
}
