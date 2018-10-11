

library ieee;
-- Commonly imported packages:
	-- STD_LOGIC and STD_LOGIC_VECTOR types, and relevant functions
	use ieee.std_logic_1164.all;

	-- SIGNED and UNSIGNED types, and relevant functions
	use ieee.numeric_std.all;

	-- Basic sequential functions and concurrent procedures
	use ieee.VITAL_Primitives.all;
	
	entity SLE4442_ATR is
--	generic
--	(
--		<name>	: <type>  :=	<default_value>;
--		...
--		<name>	: <type>  :=	<default_value>
--	);
	port
	(
		-- Input ports
		CLK		: in  std_logic;
		EN			: in 	std_logic;
		GO			: in	std_logic;
--		BUAD		: in 	std_logic_vector:="000";
		
		-- Inout ports
		CARD_IO	: inout std_logic:='Z';
		DATA		: inout std_logic_vector:="ZZZZZZZZ";
		
		-- Output ports
		CARD_RST	: out std_logic:='Z';
		CARD_CLK	: out std_logic:='Z';
		CARD_VDD : out std_logic:='Z'
	);
end SLE4442_ATR;


architecture Controller of SLE4442_ATR is

	-- Declarations (optional)
	type PHASES is (POWER, RESET, BYTE1, BYTE2, BYTE3, BYTE4,IDAL);
	signal CS: PHASES				:=IDAL; 	--! current state of transmission
	signal NS: PHASES				:=IDAL; --! nect state of transmission
	signal CLK_BUF					: std_logic:='0';
	signal COUNT_DOWN				: integer:=0;
	signal RESET_COUNT			: std_logic:='0';
	signal B1						: std_logic_vector(7 downto 0);
begin
	
	CLOCK_SYNCS : process(CLK, CS, NS) is
		variable HALF_BUF: integer:=0;
	begin
		if EN='1' then
			if rising_edge(CLK) then
				HALF_BUF := HALF_BUF + 1;
				if HALF_BUF > 5000 then
					CLK_BUF <= not CLK_BUF;
					HALF_BUF := 0;
					if RESET_COUNT='1' then 
						COUNT_DOWN 	<= 0;
					else
						COUNT_DOWN	<= COUNT_DOWN + 1;
					end if;
				end if;
			end if;
		else
			
		end if;
	end process;
	
	process(CS, NS) is
	begin
		case CS is
			when IDAL 	=>
			-- No Operation
				CARD_CLK <= 'Z';
				CARD_RST <= 'Z';
				CARD_IO 	<= 'Z';
				CARD_VDD <= 'Z';
				if GO = '1' then
					NS <= POWER;
					RESET_COUNT 	<= '1';	-- Counter Init
				end if;
			when POWER =>
				if COUNT_DOWN < 10 then
				-- POWER UP THE CARD FOR 10 Pulses
					RESET_COUNT 	<= '0';
					CARD_VDD 		<= '1';
				else
					NS 				<= RESET;
					RESET_COUNT 	<= '1';	-- Counter Init
				end if;
			when RESET	=>
				if COUNT_DOWN < 2 then
				-- POWER UP THE CARD FOR 10 Pulses
					RESET_COUNT 	<= '0';
					CARD_CLK 		<= '0';
				elsif COUNT_DOWN < 4 then
					CARD_RST			<= '1';
				elsif COUNT_DOWN < 5 then
					CARD_CLK			<= '1';
				elsif COUNT_DOWN < 7 then
					CARD_CLK			<= '0';
				elsif COUNT_DOWN < 9 then
					CARD_RST			<= '0';
				else
					NS 				<= RESET;
					RESET_COUNT 	<= '1';	-- Counter Init
				end if;
			when BYTE1	=>
				B1(COUNT_DOWN) <= CARD_IO;
				
		end case;
	end process;
	
	
	

end Controller;
