-------------------------------------------------------
--! @file CardDriver.vhd
--! @brief Card Interface Connection
-------------------------------------------------------

--! Use standard library
library ieee;
--! Use logic elements
    use ieee.std_logic_1164.all;
	 USE ieee.std_logic_arith.ALL;

--! @brief THIS COMPONENT READS AND WRITES INFORMATION FROM THE CARD ON A LOWER LEVEL
--! <h1>Pins</h1>
--! 	IT IS CONNECTED TO THE CARD DIRECTLY AND CONTROLLED BY THE CARD LOGIC
--! 	CONSISTS OF THE 8 PINS REQUIRED TO COMMUNICATE WITH THE CARD	
--!
--!	<h2>[VCC](@ref VCC_SEL)</h2>
--!	Is connected to the Logic DC-DC conveter that is used to power and communicate with the cards. Allows for selection
--! 	of card classes based on the value the value of VCC_SEL @link 
--!
--!	<h2>[CLK_OUT](@ref CLK_OUT)</h2>
--!	Is controlled by the CardClockUnit. Outputs the clock frequency requested by the card in the set up phase.
--!	The minimum clock frequency is 1MHz, during the set up phase. After this phase the actual clock frequency is doenoted
--! 	<i>f</i>, which will be a programmable value between <i>f \in \[1MHz,5MHz\]</i>.
--!	
--!	Duty cycle of this clock pins output will be between \i 40% and \i 60%. This clock will only change
--!	its frequency:	\n 
--! 		- after completion of an answer to reset. \n
--!		- after completion of a successful PPS exchange. \n


--! CardDriver entitys
entity CardDriver is
    port (
        CLK_OUT   : out std_logic:='0'; --! Is controlled by the card cloc driver unit. Outputs the clock frequency requested by the card in the set up phase
        CLK_IN   	: in  std_logic:='0'; --! Is the input clock. coorinates operations inside this unit
		  RST_OUT	: out	std_logic:='0'; --!
		  RST_IN		: in  std_logic:='0'; --!
		  CLASS_SEL	: in	std_logic_vector(2 downto 0):="000"; --! 
		  VCC_SEL	: out std_logic_vector(1 downto 0):="00"; --!
		  INFO		: inout std_logic_vector(7 downto 0):="11001010"; --!
		  I_O			: inout std_logic --!
    );
end entity;

--! @brief Architecture definition of the CardDriver
--! @details More details about this mux element.
architecture behavior of CardDriver is
	type PHASES is (START,B0,B1,B2,B3,B4,B5,B6,B7,PARITY,STOP,ERROR,IDAL); --! state maching definition of transmission phase
	signal CS: PHASES:=IDAL; 	--! current state of transmission
	signal NS: PHASES:=START; --! nect state of transmission
	SIGNAL count: integer:=0;
	signal temp: integer:=0;
	signal P: std_logic:='U'; --! Parity Bit coputation variable 
begin

	sync_proc: process(CLK_IN, NS, count, P)
	
	begin
		-- take care of the asynchronous input
		--if RST_IN = '1' then
			
		--els
		if rising_edge(CLK_IN) then
			CS <= NS;
			count <= temp;
			--with CS select
			IF CS = B0 OR CS = B1 OR CS = B2 OR CS = B3 OR CS = B4 OR CS = B5 OR CS = B6 OR CS = B7 THEN
				P <= (I_O xor P);
			--			'0' when others;
			ELSIF	CS = START THEN
				P <= '0';
			END IF;
			if (NS = START and not (CS = START)) or (NS = STOP and not (CS = STOP)) then
				count <= 0; 
				end if;
		end if;
		
		if CS = PARITY and NS = STOP and NOT P = I_O then
			CS <= ERROR;
		end if;
	end process sync_proc;

	transmit: process(CS, I_O, INFO, count)
	begin
		temp <= count + 1;
		case CS is 
			when IDAL 	=>
				temp <= 0;
				NS <= START;
			when START 	=>
				-- send start bit for 2 clock events
				I_O <= '0';	
				--if count = 1 then
					NS <= B0;
				--end if;
			when B0 		=>
				I_O <= INFO(0);
				NS <= B1;
			when B1 		=>
				I_O <= INFO(1);
				NS <= B2;
			when B2 		=>
				I_O <= INFO(2);
				NS <= B3;
			when B3 		=>
				I_O <= INFO(3);
				NS <= B4;
			when B4 		=>
				I_O <= INFO(4);
				NS <= B5;
			when B5 		=>
				I_O <= INFO(5);
				NS <= B6;
			when B6 		=>
				I_O <= INFO(6);
				NS <= B7;
			when B7 		=>
				I_O <= INFO(7);
				NS <= STOP;--PARITY;
			when PARITY	=>
				I_O <= 'Z';	-- place I_O in high impedance state to prepare for reading
				NS <= STOP;
			when STOP	=>
				I_O <= '1';
				NS <= START;--IDAL;
			when ERROR  =>
				NS <= START;--ERROR;
			when others =>
				NS <= IDAL;
		end case;
	end process transmit;
	
	RST_OUT<=RST_IN;
	CLK_OUT<=CLK_IN;

end architecture;
