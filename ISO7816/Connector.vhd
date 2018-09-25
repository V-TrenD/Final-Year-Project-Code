--
--
--

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;

entity Connector is
	port(
		CARDIN	: out 	std_logic;
		VDD		: in		std_logic;
		CLK 		: in		std_logic;
		RESET 	: in		std_logic;
		IO_RX		: in		std_logic;
		IO_TX		: out 	std_logic;
		R_W		: in		std_logic;
		EN			: in		std_logic:='0';
		
		C1			: out 	std_logic;  -- VDD Pin
		C2			: out 	std_logic;  -- Reset line
		C3			: out 	std_logic; 	-- CLK line
		IO			: inout 	std_logic;  -- IO line
		CARD		: in		std_logic   -- Card test
	);
end Connector;

architecture behave of Connector is
	begin
	
	process (R_W, IO_RX, IO)
	begin
	if R_W = '1'then
		IO_TX 	<= IO;
	elsif R_W = '0' then
		IO			<= IO_RX;
	end if;
	end process;
	
	CARDIN 	<= CARD;
	C1 		<= VDD when EN = '1' else 
					'Z';
	C2			<= RESET when EN = '1' else
					'Z';
	C3			<= CLK when EN = '1' else
					'Z';
	
end behave;