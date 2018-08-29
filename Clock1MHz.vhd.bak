-- 1MHz Clock
--! Use standard library
library ieee;
--! Use logic elements
    use ieee.std_logic_1164.all;
	 USE ieee.std_logic_arith.ALL;

entity Clock1MHz is
	port(
		CLK_IN  : in std_logic:='0';
		CLK_OUT : out std_logic:='0'
	);
end entity;

architecture F_1MHz of Clock1MHz is
	signal CLK: std_logic:='0';
	signal count: integer:=0;
begin
	process(CLK_IN)
	begin
		if rising_edge(CLK_IN) then
			count<= count + 1;
			if count >= 6 then -- clock works with 6 which is 3.57MHz
				CLK <= not CLK;
				count <= 0;
			end if;
		end if;
	end process;
	
	CLK_OUT <= CLK;
end architecture;