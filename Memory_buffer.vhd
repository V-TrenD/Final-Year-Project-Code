
library ieee;
use ieee.std_logic_1164.all;
use IEEE.numeric_std.all;

entity Memory_buffer is
	port(
		
		DATAIN:	in 	std_logic_vector(7 downto 0);
		PUSH:		in 	std_logic;
		PULL:		in		std_logic;
		CLK:		in		std_logic;
		DATAOUT:	out	std_logic_vector(7 downto 0);
		DOUT:		out	std_logic_vector(7 downto 0);
		ADDIN:	in		unsigned(7 downto 0);
		COUNT	:	out	unsigned(7 downto 0);
		RESET: 	in		std_logic;
		FULL:		out 	std_logic
	);
end entity;

architecture FIFO of Memory_buffer is
	type DATA is array(63	 downto 0) of std_logic_vector(7 downto 0); 
	signal items: 		DATA;
	signal ptr_in:		integer:=0;
	signal ptr_out:	integer:=0;
	signal holder:		integer:=0;
begin

	process(PUSH, RESET)
	begin
	
		if RESET = '0' then 
			for I in 0 to 63 loop
				items(I) <= X"00";
			end loop;
			ptr_in <= 0;
		else
			if falling_edge(PUSH) and ptr_in < 64 then 
				items(ptr_in) <= DATAIN;
				ptr_in <= ptr_in+1;
			end if;
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
	COUNT <= to_unsigned(ptr_in, 8);
	holder <= to_integer(ADDIN);
	DOUT <= 	ITEMS(holder) when holder < 64 else
				"XXXXXXXX";
end FIFO;