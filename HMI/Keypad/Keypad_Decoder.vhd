library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity Keypad_Decoder is
	port 
	(
		CLK_IN: in 	std_logic; 							--!
		EN		: in	std_logic; 							--!
		PRESS	: out	std_logic; 							--!
		Data	: out std_logic_vector(3 downto 0); --!
		ROW 	: in 	std_logic_vector(3 downto 0); --!
		COL 	: out std_logic_vector(3 downto 0)	--!
	);
end entity;