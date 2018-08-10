--! Comunication Controller
--! Vusumuzi Dube

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use STD.textio.all;

entity Controller is
	port(
		CLK		: in 	std_logic;
		GO			: in 	std_logic;
		SEND		: out std_logic;
		RECEIVE	: in 	std_logic;
		STDIN 	: IN	std_logic_vector(7 downto 0);
		STDOUT	: OUT std_logic_vector(7 downto 0)
	);
end entity;

architecture Sync of Controller is
	type 		MESSAGES			is (INIT,CARD_FIFO,INVALID);
	
	constant AT					:  string(1 to 2):=("AT");
	constant AT_BAUD			:  string(1 to 8):=("AT+BAUD8");	-- Will Be 9600 to start with... CONFIGURE to 115200 by other device
	constant AT_NAME			: 	string(1 to 18):=("AT+NAME@CardReader");
	signal	MSG_PTR			: 	MESSAGES:=INIT;
	signal 	FIFO				:	std_logic_vector(7 downto 0):=X"00";
	signal 	count,nextC		:	integer:=0;
	signal	STATE				: 	integer:=1;
	signal 	SB 				:	std_logic:='0';
	signal 	SEND_BIT			:	std_logic:='0';
	signal	MESSAGE			:	string(1 to 28):=("Vusumuzi Dube; U13221796@ASN");
	signal 	TX_EN 			:	std_logic:='1';
	signal	TX_BUSY			:	std_logic:='1';
	
	function write_message(	MSG:	string;
									PTR: 	integer) return integer is
		variable temp: integer;
	begin
		STDOUT <= CONV_STD_LOGIC_VECTOR(character'pos(MSG(PTR)),8);
		if MSG(PTR) = nul and (PTR > 5) then 
			temp := -1;
		else
			temp := PTR+1;
		end if;
		return temp;
	end write_message;
	
	
begin
	
	clk_sync :process(CLK, GO)
	begin
		if rising_edge(CLK) then
			if nextC > -1 then
				count <= count + 1;
				if  count < 10 then
					STATE <= nextC;
				elsif count > 10 and count < 20 then
					SEND_BIT <= '1';
				elsif count > 20 and count < 40 then
					SEND_BIT <= '0';
				elsif count > 50 then
					count <= 0;
				end if;
			end if;
		end if;
	end process clk_sync;

	transmit_message: process(GO, TX_EN)
	
	begin
	if rising_edge(GO) then
		if nextC = -1 then
			nextC <= 1;
		end if;
		--nextC <=	write_message(	string'("System Init Complete!"&cr&lf&nul), STATE);
		case MSG_PTR is
			when 	INIT =>
				nextC <=	write_message(	string'("System Init Complete!"&cr&lf&nul),
												STATE);
			when 	CARD_FIFO =>
				STDOUT <= STDIN;
				nextC  <= -1;
			when others =>
				nextC <=	write_message(	string'("Invalid Message!"&cr&lf&nul), 
												STATE);
		end case;
		if nextC = -1 then TX_BUSY <='0'; else TX_BUSY <= '1'; end if;
	end if;
	end process transmit_message;
	
	receive_message: process(RECEIVE)
		
	begin
		if rising_edge(RECEIVE) then
			FIFO 	<= STDIN;
			MSG_PTR <= CARD_FIFO;
			SB <= '1';
		end if;
	end process receive_message;
	
	--SEND <= RECEIVE;--SEND_BIT or SB;
	SEND <= SEND_BIT or SB;
	--STDOUT <= STDIN;
	--TX_EN <= TX_BUSY;
	
end architecture;