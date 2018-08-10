-- UART Controller
-- Vusumuzi Dube
-- BASED on PIC18F45K20 EUART module 
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

library work;
use work.UART_MODs.all;
ENTITY UART IS
PORT (CLK		: IN 	std_logic:='0';	 								--! CLOCK Pin normally connected to 27MHz Clock
		BAUD		: IN 	std_logic_vector(7 downto 0):="01110101";	--! Buad rate scaler, BAUDRATE = CLK/BAUD, BAUD $\in\[1,255\]$
		PUT  		: IN 	std_logic:='0';									--! Transmit TXREG Data on TX line
		GET		: IN 	std_logic:='0';									--! Read Received Data in RXREG line, Free for next Receive
      EN  		: IN 	std_logic:='0';									--! Turn On this module
		TXEN		: IN  std_logic:='0';									--! Enable Transmissions
		RXEN		: IN  std_logic:='0';									--! Enable Reception
      RESET  	: IN 	std_logic:='0';									--! Reset the module
      RXREG   	: OUT std_logic_vector(7 downto 0):="00000000"; --! Receive Register, stores receive Data 
		TXREG   	: IN  std_logic_vector(7 downto 0):="00000000"; --! Transsmit Register, stores Data to be transmited
      RX     	: IN 	std_logic:='1';									--! RX Line to external Bus
		TX			: OUT std_logic:='1';									--! TX Line to external Bus
		RXIF		: OUT std_logic:='0';									--! Receive Interupt Flag
		TXIF		: OUT std_logic:='0' 									--! Transmissions Interupt Flag
		);
END UART;

architecture EUSART of UART is
	signal TX_EN :		std_logic:='0';
	signal RX_EN :		std_logic:='0';
	signal RATE	:		std_logic:='0';
begin
	-- FROM => TO
	Tx_MOD : UART_TX port map(
		CLK 		=> 		RATE,
		GO			=>			PUT,
      EN  		=>			TX_EN,
      RESET  	=>			RESET,
      DATA   	=>			TXREG,
      TX     	=>			TX,
      RDY  		=>			TXIF
	);
	
	Rx_MOD : UART_RX port map(
		CLK 		=> 		RATE,
		RDY		=>			GET,
      EN  		=>			RX_EN,
      RESET  	=>			RESET,
      DATA   	=>			RXREG,
      RX     	=>			RX,
      DONE  	=>			RXIF
	);
	
	TX_EN <= TXEN and EN;
	RX_EN <= RXEN and EN;
	
end EUSART;