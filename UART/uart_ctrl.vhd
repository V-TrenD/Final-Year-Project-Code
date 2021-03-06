---------------------------------------------------------------------------
-- UART Control
-- Author       : Josh Chong
-- Date         : November 12, 1999
-- File Name    : uart_ctrl.vhd
-- Description  : A badic controller for the UART.  It incorporates a
--                transmit and receive FIFO (from Max+Plus II's MegaWizard
--                plug-in manager).  Note that no checking is done to see
--                whether the FIFOs are overflowing or not.  This strictly
--                handles the transmitting and receiving of the data.
---------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
--use ieee.std_logic_unsigned.all;
library work;
use work.uart_ctrl_pkg.all;

entity uart_ctrl is
port (
   clock      : in std_logic;
   reset      : in std_logic;
   receive    : in std_logic;
   datain     : in std_logic_vector(7 downto 0);
   dataout    : out std_logic_vector(7 downto 0);
   transmit   : out std_logic;
   write_data : in std_logic;
   read_data  : in std_logic;
   parityerr  : OUT  std_logic;
   framingerr : OUT  std_logic;
   overrun    : OUT  std_logic);
end entity;

   
architecture control of uart_ctrl is

-- Signals for controlling the UART
   signal write_sig: std_logic;
   signal txrdy_sig: std_logic;
   signal read_sig: std_logic;
   signal rxrdy_sig: std_logic;
-- Signals from the Transmit FIFO
   signal TXfifo_out: std_logic_vector(7 downto 0);
   signal TXwrreq: std_logic;
   signal TXrdreq: std_logic;
   signal TXempty: std_logic;
   signal TXfull: std_logic;  --Not used in ctrl
   signal TXfifo_used: std_logic_vector(3 downto 0);  --Not used in ctrl
-- Signals from the Receive FIFO
   signal RXfifo_in: std_logic_vector(7 downto 0);
   signal RXwrreq: std_logic;
   signal RXrdreq: std_logic;
   signal RXempty: std_logic;
   signal RXfull: std_logic;  --Not used in ctrl
   signal RXfifo_used: std_logic_vector(3 downto 0);  --Not used in ctrl
-- For use in transmitter control logic
   signal TxDataRdy: std_logic;
   signal ok2transmit: std_logic;
   signal prev_TxDataRdy: std_logic;
   signal send2TXfifo: std_logic;
-- For use in receiver control logic
   signal RxDataRdy: std_logic;
   signal RXok2read: std_logic;
   signal prev_RxDataRdy: std_logic;
   signal send2decoder: std_logic;

begin
   TXmap: txmit port map (
      mclkx16 => clock,
      write => write_sig,
      reset => reset,
      data => TXfifo_out,
      tx => transmit,
      txrdy => txrdy_sig);

   RXmap: rxcver port map (
      mclkx16 => clock,
      read => read_sig,
      rx => receive,
      reset => reset,
      rxrdy => rxrdy_sig,
      parityerr => parityerr,
      framingerr => framingerr,
      overrun => overrun,
      data => RXfifo_in);

   TXfifomap: fifo port map (
      data => datain,
      wrreq => TXwrreq,
      rdreq => TXrdreq,
      clock => clock,
      sclr => reset,
	  q => TXfifo_out,
      full => TXfull,
      empty => TXempty,
      usedw => TXfifo_used);

   RXfifomap: fifo port map (
      data => RXfifo_in,
      wrreq => RXwrreq,
      rdreq => RXrdreq,
      clock => clock,
      sclr => reset,
	  q => dataout,
      full => RXfull,
      empty => RXempty,
      usedw => RXfifo_used);

   --Control for Transmission (Through UART and TXfifo)
   TXctrl: process(clock, reset)
   begin
      if clock = '1' and clock'event then
         if reset = '1' then
            TXwrreq <= '0';
            TXrdreq <= '0';
            write_sig <= '1';
            ok2transmit <= '1';
         else
            --Enqueue data when DSP and fifo ready
            if (send2TXfifo = '1') then
               send2TXfifo <= '0';
               TXwrreq <= '1';
            else
               TXwrreq <= '0';
            end if;
            prev_TxDataRdy <= TxDataRdy;
            if (prev_TxDataRdy = '0') and (TxDataRdy = '1') then
               send2TXfifo <= '1';
            end if;

            --Dequeue data when ready to transmit
            --Puts a 1 cycle delay between telling fifo to dequeue one value
            --and telling the UART to read in data for transmission
            if (txrdy_sig = '1') and (ok2transmit = '1') and (TXempty = '0') then
               --Tell TXfifo to Dequeue 1 data value
               TXrdreq <= '1';
               ok2transmit <= '0';
            elsif (TXrdreq = '1') and (ok2transmit = '0') and (write_sig = '1') then
               --Tell UART TX to transmit this data
               write_sig <= '0';
               TXrdreq <= '0';
            else
               --elsif ( = '0') then
               write_sig <= '1';
            end if;
            --Ok to read again once txrdy goes high after going low
            if (txrdy_sig = '0') then
               ok2transmit <= '1';
            end if;
         end if;
      end if;
   end process;

   --Control for Receiving (Through UART and RXfifo)
   RXctrl : process(clock, reset)
   begin
      if clock = '1' and clock'event then
         if reset = '1' then
            RXwrreq <= '0';
            RXrdreq <= '0';
            read_sig <= '1';
            RXok2read <= '1';
            prev_RxDataRdy <= '0';
            send2decoder <= '0';

         else
            --Enqueue data when UART and fifo ready
            if (rxrdy_sig = '1') and (read_sig = '1') and (RXok2read = '1') then
               RXok2read <= '0';
               read_sig <= '0';
            elsif (read_sig = '0') and (RXwrreq = '0') and (RXok2read = '0') then
               RXwrreq <= '1';
            else
               RXwrreq <= '0';
               read_sig <= '1';
            end if;
            --Ok to read again once txrdy goes high after going low
            if (rxrdy_sig = '0') then
               RXok2read <= '1';
            end if;

            --Dequeue data when DSP ready
            --When fifo not empty and decryptor ready
            if (RXempty = '0') and (send2decoder = '1') then
               --Tell RXfifo to Dequeue 1 data value
               send2decoder <= '0';
               RXrdreq <= '1';
            else
               RXrdreq <= '0';
            end if;
            if (RxDataRdy = '1') and (prev_RxDataRdy = '0') then
               send2decoder <= '1';
            end if;
            prev_RxDataRdy <= RxDataRdy;
         end if;
      end if;
   end process;

   TxDataRdy <= write_data;
   RxDataRdy <= read_data;

end architecture;
