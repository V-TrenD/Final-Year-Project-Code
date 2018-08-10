-- UART RECEIVE
-- BASED ON PIC18F45K20 EUSART MODULE
-- by VUSUMUZI DUBE 	

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

ENTITY UART_RX IS
PORT (CLK		: IN std_logic:='0';
		RDY  		: IN std_logic:='0';
      EN  		: IN std_logic:='0';
      RESET  	: IN std_logic:='0';
      DATA   	: OUT std_logic_vector(7 downto 0):="00000000";
      RX     	: IN std_logic:='1';
		DONE		: OUT std_logic:='0');
END UART_RX;

ARCHITECTURE UART_RECEIVE OF UART_RX IS
	type PHASES is (START,B0,B1,B2,B3,B4,B5,B6,B7,PARITY,STOP,ERROR,IDAL);
	signal CS: PHASES:=IDAL; 	--! current state of transmission
	signal NS: PHASES:=IDAL; --! nect state of transmission
	signal DATA_HOLD: std_logic_vector(7 downto 0);
	signal RCIF: std_logic:='0';
BEGIN
	clock_sync:	process(CS,CLK,RESET)
	begin
		RCIF <= not RX;
		if RESET = '1' then
			CS <= IDAL;
		elsif rising_edge(CLK) then
			CS <= NS;
		elsif falling_edge(CLK) then
--			if RX='0' then
--				RCIF<='1';
--			end if;
		end if;
	end process clock_sync;
	
	RECEIVE: process(CS)
	begin
		case CS is 
			when IDAL 	=>
				DONE <= '0';
				if EN = '0' then
					NS <= IDAL;
				else
					if RDY = '0' then
						NS <= IDAL;
					else
						NS <= START;
					end if;
				end if;
			when START 	=> -- CHECK START BIT
				if EN = '0' or RDY = '0' then
					NS <= IDAL;
				elsif RCIF='1' then
					NS <= B0;
					DONE <='0';
				else 
					NS <= START;
				end if;
			when B0 		=>
				DATA_HOLD(0) <= RX;
				NS <= B1;
			when B1 		=>
				DATA_HOLD(1) <= RX;
				NS <= B2;
			when B2 		=>
				DATA_HOLD(2) <= RX;
				NS <= B3;
			when B3 		=>
				DATA_HOLD(3) <= RX;
				NS <= B4;
			when B4 		=>
				DATA_HOLD(4) <= RX;
				NS <= B5;
			when B5 		=>
				DATA_HOLD(5) <= RX;
				NS <= B6;
			when B6 		=>
				DATA_HOLD(6) <= RX;
				NS <= B7;
			when B7 		=>
				DATA_HOLD(7) <= RX;
				NS <= STOP;
			when PARITY	=>
--				TX <=  	DATA_HOLD(7) xor DATA_HOLD(6) xor DATA_HOLD(5) xor DATA_HOLD(4) xor
--							DATA_HOLD(3) xor DATA_HOLD(2) xor DATA_HOLD(1) xor DATA_HOLD(0);	-- place TX in high impedance state to prepare for reading
				NS <= STOP;
			when STOP	=>
--				TX <= '1';
				DATA <= DATA_HOLD;
				DONE <= '1';
				--if RX = '0' then
				--	NS <= ERROR;
				if EN = '0' or RDY = '0' then
					NS <= IDAL;
				else
					NS <= START;
				end if;
			when ERROR  =>
				NS <= ERROR;
				DATA <= "10000000";
				NS <= START;
			when others =>
				NS <= IDAL;
		end case;
	end process RECEIVE;
	
END UART_RECEIVE;