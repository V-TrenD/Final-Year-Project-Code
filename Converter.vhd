--
--
--

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;


entity Converter is
	port(
		DATA	:	in		std_logic_vector(7 downto 0);
		D0		:	out	std_logic;
		D1		:	out	std_logic;
		D2		:	out	std_logic;
		D3		:	out	std_logic;
		D4		:	out	std_logic;
		D5		:	out	std_logic;
		D6		:	out	std_logic;
		D7		:	out	std_logic
	);
end Converter;

architecture output of Converter is
begin

	D0 <= DATA(0);
	D1 <= DATA(1);
	D2 <= DATA(2);
	D3 <= DATA(3);
	D4 <= DATA(4);
	D5 <= DATA(5);
	D6 <= DATA(6);
	D7 <= DATA(7);

end output;