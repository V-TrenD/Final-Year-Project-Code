-- 1MHz Clock
--! Use standard library
library ieee;
--! Use logic elements
    use ieee.std_logic_1164.all;
	 USE ieee.std_logic_arith.ALL;

entity DIV_N is
	generic(
		N :	integer:=10
	);
	port(
		CLK_IN  : in std_logic:='0';
		CLK_OUT : out std_logic:='0'
	);
end entity;

architecture DIV of DIV_N is
	signal CLK: std_logic:='0';
	signal count: integer:=0;
begin
	process(CLK_IN)
	begin
		if rising_edge(CLK_IN) then
			count <= count + 1;
			if count=N then
				CLK <= not CLK;
				count <= 0;
			end if;
		end if;
		
	end process;
	
	CLK_OUT <= CLK;
end architecture;