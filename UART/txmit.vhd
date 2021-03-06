--/*******************************************************************
-- *
-- *    DESCRIPTION: UART transmitter module.
-- *    AUTHOR: Jim Jian
-- *    HISTORY: 1/14/97
-- *    QuickLogic's Application Notes and QuickNotes
-- *    (Digital UART Design Using Hardware Description Language)
-- *    http://www.quicklogic.com/support/anqn/
-- *
-- *    Modifications: (1) Added txclkcount so that the count for the clock
-- *                   divider can be easily changed.
-- *    Name: Josh Chong
-- *    Date: 10/30/99
-- *
-- *******************************************************************/

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

ENTITY txmit IS
--Number of bits for the count in the clock divider (default = 3 for mclkx16/16)
generic (txclkcount : positive := 3);  --Modification (1)
PORT (mclkx16: IN std_logic;
      write  : IN std_logic;
      reset  : IN std_logic;
      data   : IN std_logic_vector(7 downto 0);
      tx     : OUT std_logic;
      txrdy  : OUT std_logic);
END txmit;


ARCHITECTURE behave OF txmit IS
   CONSTANT paritymode : std_logic := '0';  -- initializing to 1 = odd parity, 0 = even parity
   SIGNAL write1, write2 : std_logic;
   SIGNAL txdone1, txdone : std_logic;
   SIGNAL thr, tsr : std_logic_vector(7 downto 0);
   SIGNAL tag1, tag2 : std_logic;
   SIGNAL txparity : std_logic;
   SIGNAL txclk : std_logic;
   SIGNAL paritycycle : std_logic;
   SIGNAL txdatardy : std_logic;
   SIGNAL cnt : std_logic_vector(txclkcount-1 downto 0);
BEGIN
   
--// Paritycycle = 1 on next to last cycle, this means when tsr[1] gets tag2.
paritycycle <= tsr(1) AND
               NOT (tag2 OR tag1 OR tsr(7) OR tsr(6) OR
                    tsr(5) OR tsr(4) OR tsr(3) OR tsr(2));

--// txdone = 1 when done shifting, this means when tx gets tag2.
txdone <= NOT (tag2 OR tag1 OR tsr(7) OR tsr(6) OR tsr(5) OR
               tsr(4) OR tsr(3) OR tsr(2) OR tsr(1) OR tsr(0));

--// Ready for new date to be written, when no data is in transmit hold register.
txrdy <= NOT txdatardy;

--//Latch data[7:0] into the transmit hold register at posedge of write.
  thr_write : PROCESS (write, data)
  BEGIN
     IF (write = '0') THEN
        thr <= data;
     END IF;
  END PROCESS;

--// Toggle txclk every 2^txclkcount counts, which divides the clock by
--// 2*2^txclkcount, to generate the baud clock
   baud_clock_gen : PROCESS (mclkx16, reset)
      variable count_indicator: std_logic_vector(txclkcount-1 downto 0);
   BEGIN
      count_indicator := (others => '0');
      IF (reset ='1') THEN
         txclk <= '0';
         cnt <= (others => '0');
      ELSIF (mclkx16='1') AND mclkx16'EVENT THEN
         IF (cnt = count_indicator) THEN
            txclk <= NOT txclk;
         END IF;
      cnt <= cnt + 1;
      END IF;
   END PROCESS;

   shift_out : PROCESS (txclk, reset)
   BEGIN
      IF (reset = '1') THEN
      	tsr <= (OTHERS => '0');
         tag2 <= '0';
         tag1 <= '0';
         txparity <= paritymode;
         tx <= '1';
         --idle_reset;
      ELSIF txclk = '1' AND txclk'EVENT THEN
         IF (txdone='1' AND txdatardy = '1') THEN
--          load_data;
            tsr <= thr;
            tag2 <= '1';
            tag1 <= '1';
            txparity <= paritymode;
            tx <= '0';

         ELSE
--          shift_data;
            tsr <= '0'&tsr(7 downto 1);
            tsr(7) <= tag1;
            tag1 <= tag2;
			tag2 <= '0';
            txparity <= txparity XOR tsr(0);
            IF (txdone = '1') THEN
               tx <= '1';
               ELSIF (paritycycle = '1') THEN
                  tx <= txparity;
               ELSE
                  tx <= tsr(0);
            END IF;
         END IF;
      END IF;
   END PROCESS;

   PROCESS (mclkx16, reset)
   BEGIN
      IF (reset='1') THEN
         txdatardy <= '0';
         write2 <= '1';
         write1 <= '1';
         txdone1 <= '1';
      ELSIF mclkx16 = '1' AND mclkx16'EVENT THEN
         IF (write1 = '1' AND write2 = '0') THEN
            txdatardy <= '1';
         ELSIF (txdone = '0' AND txdone1 = '1') THEN
            txdatardy <= '0';
         END IF;
         write2 <= write1;
         write1 <= write;
         txdone1 <= txdone;
      END IF;
   END PROCESS;
END behave;
