-------------------------------------------------------
--! @file CardClockUnit.vhd
--! @brief Colock Unit for card communication
-------------------------------------------------------

--! Use standard library
library ieee;
--! Use logic elements
    use ieee.std_logic_1164.all;

--! \b TA_1 encodes the indicated value of the clock rate conversion integer (Fi), the indicated value of the baud rate
--! adjustment integer (Di) and the maximum value of the frequency supported by the card (f_max). The default
--! values are <i> Fi = 372, Di = 1 </i> and <i>f_max = 5 MHz</i>
--! <table>
--! <caption> encode Fi and f (max.).</caption>
--! <tr><th>	Bits  		<th> 0000 <th> 0001 <th> 0010 <th> 0011 <th> 0100 <th> 0101 <th> 0110 <th> 0111<th> 1000 <th> 1001 <th> 1010 <th> 1011 <th> 1100 <th> 1101 <th> 1110 <th> 1111
--! <tr><td>	Fi 			<td> 372	 <td> 372  <td> 558  <td> 744  <td> 1116 <td> 1488 <td> 1860 <td> RFU <td>	RFU  <td> 512  <td> 768  <td> 1024 <td> 1536 <td> 2048 <td> RFU  <td> RFU
--! <tr><td>	Di 			<td> RFU  <td>	1 	  <td> 2 	<td> 4    <td>		8 <td> 	16 <td>	32  <td>	64  <td> 12   <td> 20   <td> RFU	 <td> RFU  <td> RFU  <td> RFU  <td> RFU  <td> RFU 
--! <tr><td>	f (max.) MHz<td>	4 	 <td>	5	  <td> 	6  <td> 	8	 <td> 12	  <td>   16 <td> 20   <td>  -  <td> -    <td>  5   <td>  7,5 <td> 10   <td> 15   <td> 20   <td>   -  <td>  -
--! </table>

-- <table>
-- <caption> encode Fi and f (max.).</caption>
-- <tr><th>	Bits  		<th> 0000 <th> 0001 <th> 0010 <th> 0011 <th> 0100 <th> 0101 <th> 0110 <th> 0111
-- <tr><td>	Fi 				<td> 372	 <td> 372  <td> 558  <td> 744  <td> 1116 <td> 1488 <td> 1860 <td> RFU
-- <tr><td>	Di 				<td> RFU  <td>	1 	  <td> 2 	<td> 4    <td>		8 <td> 	16 <td>	32  <td>	64 
-- <tr><td>	f (max.) MHz 	<td>	4 	 <td>	5	  <td> 	6 <td> 	8	<td> 12	 <td>   16 <td> 20   <td>  -
-- <tr><th>	Bits  			<th> 1000 <th> 1001 <th> 1010 <th> 1011 <th> 1100 <th> 1101 <th> 1110 <th> 1111
-- <tr><td>	Fi 				<td>	RFU <td> 512  <td> 768  <td> 1024 <td> 1536 <td> 2048 <td> RFU  <td> RFU
-- <tr><td>	Di 				<td> 12   <td>	20   <td> RFU	<td> RFU  <td>	RFU  <td> RFU  <td> RFU  <td>	RFU 
-- <tr><td>	f (max.) MHz 	<td> -    <td>  5   <td>  7,5 <td> 10   <td> 15   <td> 20   <td>   -  <td>  -
-- </table>

--! CardClockUnit entity
entity CardClockUnit is
    port (
        CLK_OUT   : out  	std_logic:='0'; --! Is controlled by the card cloc driver unit. Outputs the clock frequency requested by the card in the set up phase
        CLK_IN   	: in  	std_logic:='0'; --! Is the input clock. coorinates operations inside this unit Expects 40MHz Norminal
		  EN			: in 		std_logic:='1'; --! allows the clock signal to be output according to the programed count
		  Fi_Di		: in 		std_logic_vector(7 downto 0)--! uesd to program the frequency
    );
end entity;

--! @brief Architecture definition of the CardClockUnit
--! @details More details about this mux element.
architecture behavior of CardClockUnit is
	signal	Fi		: integer	:= 372; 	--! Clock Rate Conversion Integer
	signal	Di		: integer 	:= 1; 	--! Baud Rate Adjustment Integer
	signal 	CLK	: std_logic := '0'; 	--! Clock Hold Variable
	signal 	f 		: integer	:= 5;		--! clock frequency role over for 5Mhz
begin

	change_frequency: process (EN, Fi_Di) -- 
			variable temp: std_logic_vector(3 downto 0);
		begin
		if EN = '0' then
			-- Set up the clock rate conversion integer Fi
			temp := Fi_Di(7 downto 4);
			case temp is										-- CLK IN is expected to be a 40MHz ossilator
				when "0000" => Fi <= 372; 	f <= 25;	--20;		-- 4MHz
				when "0001" =>	Fi <= 372; 	f <= 5;	--16;		-- 5MHz
				when "0010" =>	Fi <= 558;	f <= 4;	--13 ;	-- 6MHz
				when "0011" =>	Fi <= 744;	f <= 3;	--10;		-- 8MHz
				when "0100" =>	Fi <= 1116;	f <= 2;	--7;		-- 12MHz
				when "0101" =>	Fi <= 1488;	f <= 5;		-- 16MHz
				when "0110" =>	Fi <= 1860;	f <= 4;		-- 20MHz
				when "1001" =>	Fi <= 512;	f <= 10;		-- 5MHz
				when "1010" =>	Fi <= 768;	f <= 14;		-- 7.5MHz
				when "1011" =>	Fi <= 1024;	f <= 8;		-- 10MHz
				when "1100" =>	Fi <= 1536;	f <= 6;		-- 15MHz
				when "1101" =>	Fi <= 2048;	f <= 4;		-- 20MHz
				when others =>	Fi <= Fi;	f <= f;
			end case;
			-- Set up the baud rate adjustment integer
			temp := Fi_Di(3 downto 0);
			case temp is
				when "0001" =>	Di <= 1;
				when "0010" =>	Di <= 2;
				when "0011" =>	Di <= 4;
				when "0100" =>	Di <= 8;
				when "0101" =>	Di <= 16;
				when "0110" =>	Di <= 32;
				when "0111" =>	Di <= 64;
				when "1000" =>	Di <= 12;
				when "1001" =>	Di <= 20;
				when others =>	Di <= Di;
			end case;
		end if;
	end process change_frequency;
	
	run: process(EN,CLK_IN)
		variable CLK_DIV	: integer :=0;	--! Clock Division Integer
	begin
		if EN = '1' then
			if rising_edge(CLK_IN) then 
				CLK_DIV := CLK_DIV + 1;
				if	CLK_DIV = f then
					CLK_DIV := 0;
					CLK <= not CLK;
				end if;
			end if;
			
		elsif	EN= '0' then
			CLK_DIV := 0;
			CLK <=	'0';
		end if; 
	end process run;
	

	
	CLK_OUT <= CLK;
	
end architecture;