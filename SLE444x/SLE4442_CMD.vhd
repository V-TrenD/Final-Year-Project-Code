library ieee;
-- Commonly imported packages:
	-- STD_LOGIC and STD_LOGIC_VECTOR types, and relevant functions
	use ieee.std_logic_1164.all;

	-- SIGNED and UNSIGNED types, and relevant functions
	use ieee.numeric_std.all;

	-- Basic sequential functions and concurrent procedures
	use ieee.VITAL_Primitives.all;
	
	entity SLE4442_CMD is
--	generic
--	(
--		<name>	: <type>  :=	<default_value>;
--		...
--		<name>	: <type>  :=	<default_value>
--	);
	port
	(
		-- Input ports
		CLK_IN	: in  std_logic;
		EN			: in 	std_logic;
		GO			: in	std_logic;
--		BUAD		: in 	std_logic_vector:="000";
		
		-- Inout ports
		CARD_IO	: inout 	std_logic:='Z';
		DATA		: in 		std_logic_vector(7 downto 0):="ZZZZZZZZ";
		
		-- Output ports
		CARD_CLK	: out std_logic:='Z';
		DONE		: out std_logic:='Z'
	);
end SLE4442_CMD;
