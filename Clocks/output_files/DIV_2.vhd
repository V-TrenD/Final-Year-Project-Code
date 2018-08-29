-- 1MHz Clock
--! Use standard library
library ieee;
--! Use logic elements
    use ieee.std_logic_1164.all;
	 USE ieee.std_logic_arith.ALL;

entity DIV_2 is
	port(
		CLK_IN  : in std_logic:='0';
		CLK_OUT : out std_logic:='0'
	);
end entity;

architecture DIV of DIV_2 is
	signal CLK: std_logic:='0';
	signal count: integer:=0;
begin
	process(CLK_IN)
	begin
		if rising_edge(CLK_IN) then
			CLK <= not CLK;
		end if;
	end process;
	
	CLK_OUT <= CLK;
end architecture;