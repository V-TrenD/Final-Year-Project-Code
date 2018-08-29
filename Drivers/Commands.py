## ISO 7816 Card commands
# @author Vusumuzi Dube
# @serial 13221796
# This file holds the information required to implement ISO7816 compliant commands for
# smart card communication

# ISO7816 Part 4
# Section 5
# For organizing interchange, this clause specifies the following basic features.
# 1) Command-response pairs
# 2) Data objects
# 3) Structures for applications and data
# 4) Security architecture

# 5.1 Command-response pairs


class CommandHeader:
    """

    """

    def __init__(self):
        """

        """
        CLA = None  # Class byte denoted CLA [1B]
        INS = None  # Instruction byte denoted INS [1B]
        # Parameter bytes denoted P1 - P2
        P1 = None
        P2 = None


class Command:
    """

    """

    def __init__(self):
        """

        """
        header = CommandHeader()
        Lc = None       # field Absent for encoding Nc = 0, present for encoding Nc > 0 0, 1 or 3
        DATA = None     # Command data field Absent if Nc = 0, present as a string of Nc bytes if Nc > 0 Nc
        Le = None       # field Absent for encoding Ne = 0, present for encoding Ne > 0 0, 1, 2 or 3
        """Nc denotes the number of bytes in the command data field. The Lc field encodes Nc.
            - If the Lc field is absent, then Nc is zero.
            - A short Lc field consists of one byte not set to '00'.
                • From '01' to 'FF', the byte encodes Nc from one to 255.
            - An extended Lc field consists of three bytes: one byte set to '00' followed by two bytes not set to '0000'.
                • From '0001' to 'FFFF', the two bytes encode Nc from one to 65 535.
        """
        Nc = None


class Response:
    """

    """

    def __init__(self):
        DATA = None     # Response data field Absent if Nr = 0, present as a string of Nr bytes if Nr > 0 Nr (at most Ne)
        # Response trailer Status bytes denoted SW1-SW2 2
        SW1 = None
        SW2 = None

if __name__ == '__main__':
    pass
