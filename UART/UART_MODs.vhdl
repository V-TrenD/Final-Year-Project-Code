-- UART LIBRARY
-- Vusumuzi Dube

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;
USE ieee.numeric_std.all;

package UART_MODs is
	COMPONENT UART_TX IS
		PORT (CLK		: IN std_logic;
				GO			: IN std_logic;
				EN  		: IN std_logic;
				RESET  	: IN std_logic;
				DATA   	: IN std_logic_vector(7 downto 0);
				TX     	: OUT std_logic;
				RDY  		: OUT std_logic);
	END COMPONENT;
		
	COMPONENT UART_RX IS
		PORT (CLK		: IN std_logic;
				RDY  		: IN std_logic;
				EN  		: IN std_logic;
				RESET  	: IN std_logic;
				DATA   	: OUT std_logic_vector(7 downto 0);
				RX     	: IN std_logic;
				DONE		: OUT std_logic);
	END COMPONENT;
	
	COMPONENT BAUDRATE IS
		PORT (CLK_IN		: IN std_logic;
				COUNT			: IN unsigned(7 downto 0);
				CLK			: OUT std_logic
				);
	END COMPONENT;
end package;