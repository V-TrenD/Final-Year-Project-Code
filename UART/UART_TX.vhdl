-- UART TRANSMIT
-- BASED ON PIC18F45K20 EUSART MODULE
-- by VUSUMUZI DUBE 	

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

ENTITY UART_TX IS
PORT (CLK		: IN std_logic;
		GO			: IN std_logic;
      EN  		: IN std_logic;
      RESET  	: IN std_logic;
      DATA   	: IN std_logic_vector(7 downto 0);
      TX     	: OUT std_logic;
      RDY  		: OUT std_logic);
END UART_TX;

ARCHITECTURE UART_TRANSMIT OF UART_TX IS
	type PHASES is (START,B0,B1,B2,B3,B4,B5,B6,B7,PARITY,STOP,ERROR,IDAL, PAUSE);
	signal CS: PHASES:=IDAL; 	--! current state of transmission
	signal NS: PHASES:=IDAL; --! nect state of transmission
	signal DATA_HOLD: std_logic_vector(7 downto 0);
BEGIN
	clock_sync:	process(CS,CLK,RESET)
	begin
		if RESET = '1' then
			CS <= IDAL;
		elsif rising_edge(CLK) then
			CS <= NS;
		end if;
	end process clock_sync;
	
	transmit: process(CS, GO)
	begin
		case CS is 
			when IDAL 	=>
				
				if EN = '0' then
					NS <= IDAL;
					RDY <= '0';
					TX <= '1';
				else
					if GO = '0' then
						NS <= IDAL;
						RDY <= '1';
						TX <= '1';
					else
						DATA_HOLD <= DATA;
						NS <= START;
						RDY <= '1';
					end if;
				end if;
			when START 	=> -- SEND START BIT
				RDY <= '0';
				TX <= '0';
				NS <= B0;
			when B0 		=>
				TX <=DATA_HOLD(0);
				NS <= B1;
				RDY <= '0';
			when B1 		=>
				TX <=DATA_HOLD(1);
				NS <= B2;
				RDY <= '0';
			when B2 		=>
				TX <=DATA_HOLD(2);
				NS <= B3;
				RDY <= '0';
			when B3 		=>
				TX <=DATA_HOLD(3);
				NS <= B4;
				RDY <= '0';
			when B4 		=>
				TX <=DATA_HOLD(4);
				NS <= B5;
				RDY <= '0';
			when B5 		=>
				TX <=DATA_HOLD(5);
				NS <= B6;
				RDY <= '0';
			when B6 		=>
				TX <=DATA_HOLD(6);
				NS <= B7;
				RDY <= '0';
			when B7 		=>
				TX <=DATA_HOLD(7);
				NS <= STOP;
				RDY <= '0';
			when PARITY	=>
				TX <=  	DATA_HOLD(7) xor DATA_HOLD(6) xor DATA_HOLD(5) xor DATA_HOLD(4) xor
							DATA_HOLD(3) xor DATA_HOLD(2) xor DATA_HOLD(1) xor DATA_HOLD(0);	-- place TX in high impedance state to prepare for reading
				NS <= STOP;
				RDY <= '0';
			when STOP	=>
				--if CLK = '0' then
				--RDY <= '1';
				TX <= '1';
				--end if;
				NS <= IDAL;
				RDY <= '0';
			when PAUSE =>
				RDY <= '1';
				NS <= IDAL;
			when ERROR  =>
				NS <= ERROR;
			when others =>
				NS <= IDAL;
		end case;
	end process transmit;
	
END UART_TRANSMIT;