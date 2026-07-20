with open("ufm_increment.mif", "w", newline="\n") as f:
    f.write("WIDTH=16;\n")
    f.write("DEPTH=512;\n\n")
    f.write("ADDRESS_RADIX=HEX;\n")
    f.write("DATA_RADIX=HEX;\n\n")
    f.write("CONTENT BEGIN\n")

    for address in range(512):
        f.write(f"    {address:03X} : {address:04X};\n")

    f.write("END;\n")
