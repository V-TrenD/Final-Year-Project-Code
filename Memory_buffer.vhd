
library ieee;
use ieee.std_logic_1164.all;

entity Memory_buffer is
	port(
		
		DATAIN:	in 	std_logic_vector(7 downto 0);
		PUSH:		in 	std_logic;
		PULL:		in		std_logic;
		CLK:		in		std_logic;
		DATAOUT:	out	std_logic_vector(7 downto 0);
		FULL:		out 	std_logic
	);
end entity;

architecture FIFO of Memory_buffer is
	type DATA is array(64 downto 1) of std_logic_vector(7 downto 0); 
	signal items: DATA;
	signal ptr_in:		integer:=0;
	signal ptr_out:	integer:=0;
begin

	process(PUSH)
	begin
	
		if rising_edge(PUSH) and ptr_in < 64 then 
			items(ptr_in) <= DATAIN;
			ptr_in <= ptr_in+1;
		end if;
	
	end process;
	
	process(PULL)
	begin
	
		if rising_edge(PULL) and  ptr_out < 64 then 
			DATAOUT <= items(ptr_out);
			ptr_out <= ptr_out+1;
		end if;
	
	end process;
	
	FULL <= 	'1' when ptr_in > 62 else
				'0';

end FIFO;