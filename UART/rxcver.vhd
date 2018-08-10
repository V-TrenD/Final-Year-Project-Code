--/*******************************************************************
-- *
-- *    DESCRIPTION: UART receiver module. 
-- *    AUTHOR: Jim Jian 
-- *    HISTORY: 1/14/96    
-- *    QuickLogic's Application Notes and QuickNotes
-- *    (Digital UART Design Using Hardware Description Language)
-- *    http://www.quicklogic.com/support/anqn/
-- *
-- *    Modifications: (1) Added rxclkcount so that the count for the clock
-- *                   divider can be easily changed.
-- *                   (2) Corrected a bug that caused incorrect operation
-- *    Name: Josh Chong
-- *    Date: 10/30/99
-- *
-- *******************************************************************/

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

ENTITY rxcver IS
--Number of bits for the count in the clock divider (default = 3 for mclkx16/16)
generic (rxclkcount : positive := 3); --Modification (1)
PORT (mclkx16   : IN std_logic;  -- input clock, 16x baudrate clock used for synchronization
      read      : IN std_logic;  -- Read Strobe
      rx        : IN std_logic;  -- Receive Input Line
      reset     : IN std_logic;  -- Global Reset
      rxrdy     : OUT  std_logic;  -- Receiver data ready to read
      parityerr : OUT  std_logic;  -- Receiver parity error flag
      framingerr: OUT  std_logic;  -- Receiver framing error flag
      overrun   : OUT  std_logic;  -- Receiver overrun error flag
      data      : OUT  std_logic_vector(7 downto 0));  -- 8 bit output data bus
END rxcver;


ARCHITECTURE behave OF rxcver IS
   CONSTANT paritymode : std_logic := '0';  -- initializing to 1 = odd parity, 0 = even parity
   SIGNAL rxcnt : std_logic_vector(rxclkcount downto 0);  -- clock cycle count
   SIGNAL rx1, read1, read2, idle1 : std_logic;  -- delayed versions of rx, read, idle
   SIGNAL hunt  : std_logic;  -- hunting for start bit flag
   SIGNAL rhr : std_logic_vector(7 downto 0);  -- Receiver hold register
   SIGNAL rsr : std_logic_vector(7 downto 0);  -- Receiver serial -> parallel shift register
   SIGNAL rxparity  :  std_logic;  -- parity bit of received data
   SIGNAL paritygen :  std_logic;  -- generated parity of received data
   SIGNAL rxstop : std_logic;  -- stop bit of received data
   SIGNAL rxclk  : std_logic;  -- Receive data shift clock
   SIGNAL idle  :  std_logic;  -- ='1' when receiver is idling
   SIGNAL rxdatardy : std_logic;  -- = '1' when data is ready to be read
BEGIN

--// Idle requires async preset since it is clocked by rxclk, and it's  
--// value determines whether rxclk gets generated or not. 
--// Idle goes low when shifting in data. This is ensured because all bits 
--// of rsr are preset to all 1's when idle is high. Idle goes high again 
--// when rsr[0] = 0, i.e. when the low "rxstop" bit reach rsr[0]. 
--// Next rising edge of rxclk preset idle to high again, and generation of 
--// rxclk is disabled.
	idle_preset : PROCESS (rxclk, reset)
	BEGIN
       IF reset = '1' THEN
          idle <= '1';
       ELSIF rxclk'EVENT AND rxclk = '1' THEN
          idle <= (NOT idle) AND (NOT rsr(0));
       END IF;
    END PROCESS;

--		
--// Synchronizing rxclk to the centerpoint of low leading startbit.
--always @(posedge mclkx16)
--begin
--
--	// A start bit is eight clock times with rx=0 after a falling edge of rx. 
	rxclk_sync : PROCESS (mclkx16, reset)
	BEGIN
		IF reset = '1' THEN
			hunt <= '0';
--          set rxcnt to 1
            rxcnt(rxclkcount downto 1) <= "0";
            rxcnt(0) <= '1';
			rx1 <= '1';
			rxclk <= '0';
		ELSIF (mclkx16 = '1') AND mclkx16'EVENT THEN
			IF (idle = '1' AND rx = '0' AND rx1 = '1') THEN
               hunt <= '1';
			ELSE
			   IF (idle = '0' OR rx = '1') THEN
			      hunt <= '0';
               END IF;
               IF (idle = '0' OR hunt = '1') THEN
                  rxcnt <= rxcnt + 1;
               ELSE
--                set rxcnt to 1
                  rxcnt(rxclkcount downto 1) <= "0";
                  rxcnt(0) <= '1';
               END IF;
            END IF;
            rx1 <= rx;
            rxclk <= rxcnt(rxclkcount);		
	    END IF;
	END PROCESS;		

-- When not idling, sample data at the rx input, and generate parity.
   sample_data : PROCESS (rxclk, reset)
   BEGIN
      IF (reset = '1') THEN
      -- idle_reset   
         rsr <= "11111111";  -- All 1's ensure that idle stays low during data shifting.
         rxparity <= '1';  -- Preset to high to ensure idle = 0 during data shifting.
   	     paritygen <= paritymode;  --Preset paritygen to parity mode.
   	     rxstop <= '0';
      ELSIF (rxclk = '1') AND (rxclk'EVENT) THEN
         IF (idle = '1') THEN
            -- idle_reset
            rsr <= "11111111";  -- All 1's ensure that idle stays low during data shifting.
   	        rxparity <= '1';  -- Preset to high to ensure idle = 0 during data shifting.          
            paritygen <= paritymode;  -- Preset paritygen to parity mode.
   	        rxstop <= '0';
         ELSE
  	        -- shift_data
  	        rsr <= '0'&rsr(7 downto 1);  -- Right shift receive shift register.     
            rsr(7) <= rxparity;  -- Load rsr[7] with rxparity.
            rxparity <= rxstop;  -- Load rxparity with rxstop.
            rxstop <= rx;  -- Load rxstop with rx. At 1'st shift rxstop gets low "start bit". 
            paritygen <= paritygen XOR rxstop;  -- Generate parity as data are shifted.
         END IF;
      END IF;
   END PROCESS;

-- Generate status & error flags.
   generate_flag : PROCESS (mclkx16, reset)
   BEGIN
      IF (reset = '1') THEN
          rhr <= "00000000";
          rxdatardy <= '0';
          overrun <= '0';
          parityerr <= '0';
          framingerr <= '0';
          idle1 <= '1';
          read2 <= '1';
          read1 <= '1';
      ELSIF (mclkx16 = '1') AND (mclkx16'EVENT) THEN
         IF (idle = '1' AND idle1 = '0') THEN
            IF (rxdatardy = '1') THEN
               overrun <= '1';
            ELSE
               overrun <= '0';  -- No overrun error, since holding register is empty.
               rhr <= rsr;  -- Update holding register with contents of shift register.
               parityerr <= paritygen;  -- paritygen = 1, if parity error.
               framingerr <= NOT rxstop;  -- Framingerror, if stop bit is not 1.
               rxdatardy <= '1';  -- Data is ready for reading flag.
            END IF;

--         END IF;  --Modification (2) Changed to elsif to get receiver to receive properly
		 elsIF (read2 = '0' AND read1 = '1') THEN
--         IF (read2 = '0' AND read1 = '1') THEN

            rxdatardy  <= '0';
            parityerr  <= '0';
            framingerr <= '0';
            overrun    <= '0';
         END IF;

         idle1 <= idle;  -- idle delayed 1 cycle for edge detect.
         read2 <= read1;  -- 2 cycle delayed version of read, used for edge detection.
         read1 <= read;  -- 1 cycle delayed version of read, used for edge detection.
      END IF;
   END PROCESS;

   rxrdy <= rxdatardy;

   latch_data : PROCESS (read, rhr)
   BEGIN
      IF (read = '1') THEN
         data <= rhr;
      END IF;
   END PROCESS;
END behave;
