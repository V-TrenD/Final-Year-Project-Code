-- UART TRANSMIT
-- BASED ON PIC18F45K20 EUSART MODULE
-- by VUSUMUZI DUBE 	

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;
USE ieee.numeric_std.all;

ENTITY BAUDRATE IS
	generic(
		COUNT_START :	unsigned:= "0000000001110101" -- 117;
	);
PORT (CLK_IN		: IN std_logic:='0';
		COUNT			: IN unsigned(15 downto 0):=COUNT_START;--"01110101"; -- 117
		CLK			: OUT std_logic:='0'
		);
END BAUDRATE;
-- buad rate = clk_in/(2*count)
-- default 27M/(2*117)
architecture BAUD of BAUDRATE is
	signal counter : integer:=0;
	signal CLK_OUT : std_logic:='0';
begin

	process	(CLK_IN, COUNT)
	begin
		if rising_edge(CLK_IN) then
			counter <= counter +1;
			if counter = to_integer(COUNT) then
				counter <= 0;
				CLK_OUT <= not CLK_OUT;
			end if;
		end if;
	end process;
	
	CLK <= CLK_OUT;
end BAUD;