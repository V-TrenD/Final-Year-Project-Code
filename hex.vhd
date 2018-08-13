-- 
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity hex is
	port 
	(
		data	: in unsigned (7 downto 0);
		SSD_H : out std_logic_vector(6 downto 0);
		SSD_L : out std_logic_vector(6 downto 0)
	);
end entity;

architecture rtl of hex is
	signal upper : unsigned(3 downto 0);
	signal lower : unsigned(3 downto 0);
begin
	upper <= data(7 downto 4);
	lower <= data(3 downto 0);
	
	SSD_H <= "1000000" when upper = 0 else
				"1111001" when upper = 1 else
				"0100100" when upper = 2 else
				"0110000" when upper = 3 else
				"0011001" when upper = 4 else
				"0010010" when upper = 5 else
				"0000010" when upper = 6 else
				"1111000" when upper = 7 else
				"0000000" when upper = 8 else
				"0010000" when upper = 9 else
				"0001000" when upper = 10 else -- A
				"0000011" when upper = 11 else -- b
				"1000110" when upper = 12 else -- C
				"0100001" when upper = 13 else -- d
				"0000110" when upper = 14 else -- E
				"0001110" when upper = 15 else -- F
				"1111111";
	
	SSD_L <= "1000000" when lower = 0 else
				"1111001" when lower = 1 else
				"0100100" when lower = 2 else
				"0110000" when lower = 3 else
				"0011001" when lower = 4 else
				"0010010" when lower = 5 else
				"0000010" when lower = 6 else
				"1111000" when lower = 7 else
				"0000000" when lower = 8 else
				"0010000" when lower = 9 else
				"0001000" when lower = 10 else -- A
				"0000011" when lower = 11 else -- b
				"1000110" when lower = 12 else -- C
				"0100001" when lower = 13 else -- d
				"0000110" when lower = 14 else -- E
				"0001110" when lower = 15 else -- F
				"1111111";

end rtl;
