-------------------------------------------------------
--! @file ISO7816_RX.vhd
--! @brief Card Interface Connection
-------------------------------------------------------

--! Use standard library
library ieee;
--! Use logic elements
		 use ieee.std_logic_1164.all;
	 USE ieee.std_logic_arith.ALL;
	 --use ieee.std_textio

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


--! ISO7816_RX entitys
entity ISO7816_RX is
    port ( --! Is controlled by the card cloc driver unit. Outputs the clock frequency requested by the card in the set up phase
        CLK_IN   	: in  std_logic:='0'; --! Is the input clock. coorinates operations inside this unit
		  EN			: in	std_logic:='0'; --!
		  BUSY		: out	std_logic:='0';
		  INFO		: out std_logic_vector(7 downto 0):="00000000"; --!
		  B			: out std_logic:='1';
		  I_O			: in 	std_logic:='U' --!
    );
end entity;

--! @brief Architecture definition of the ISO7816_RX
--! @details More details about this mux element.
architecture behavior of ISO7816_RX is
	type PHASES is (START,START2,B0,PARITY,STOP,ERROR,IDAL); --! state maching definition of transmission phase
	signal CS: 		PHASES:=IDAL; 		--! current state of transmission
	signal NS: 		PHASES:=START; 	--! nect state of transmission
	signal CLK:		std_logic:='0';	--!
	SIGNAL count: 	integer:=0;			--!
	signal temp: 	integer:=0;			--!
	signal P: 		std_logic:='U'; 	--! Parity Bit coputation variable
	signal DATA:	std_logic_vector(7 downto 0):="00000000";	--!
	signal force:	std_logic:='0';
	signal DCOUNT:	integer:= 0;
begin

	clock:	process(CLK_IN,I_O,CS)
	begin 
	if 	rising_edge(CLK_IN) then 
		CLK <= not CLK;
		
	elsif falling_edge(CLK_IN) then
		
	end if;
	if I_O = 'L' and CS=START then
		force <= '1';
	elsif CS=B0 then
		force <= '0';
	end if;
	
	end process clock;
	
	sync_proc: process(CLK,EN, NS, force)
	
	begin
		--count <= count + 1;
		if EN = '0' then
			CS <= IDAL;
		else
			if force='1' then
				CS <= B0;
			elsif rising_edge(CLK) then
				CS <= NS;
				if CS = B0 then
					DCOUNT <= DCOUNT + 1;
				else
					DCOUNT <= 0;
				end if;
			elsif falling_edge(CLK) then
				
			end if;
		end if;
		
--		if CS = PARITY and NS = STOP and NOT P = I_O then
--			CS <= ERROR;
--		end if;
	end process sync_proc;
--	
--	start_bit: process(I_O)
--	
--	begin
--
--	end process start_bit;

	transmit: process(CS, DCOUNT)
		variable TEMP: integer:=-1;
	begin
		case CS is
			when IDAL 	=>
				BUSY 	<= '1';
				NS 	<= START;
				B 		<= '1';
			when START 	=>
				-- send start bit for 2 clock events
				BUSY 	<= '0';
				B 		<= '1';
--				if I_O='0' then
--					--BUSY 	<= '1';
--					NS 	<= B0;	
--					B 			<= '0';
--					--DATA 	<= "ZZZZZZZZ";
--				else
--					NS 	<= START;	
--					B 			<= '1';
--				end if;
			when B0 		=>
				BUSY 	<= '1';
				if DCOUNT > 7 then
					NS <= STOP;
					TEMP:=-1;
				else
					if not (TEMP=DCOUNT) then
						DATA(DCOUNT)	<= I_O;
						B 		<= DATA(DCOUNT);
						NS 	<= B0;
						TEMP:=DCOUNT;
					end if;
				end if;
			when PARITY	=>
				P 			<= I_O;	-- place I_O in high impedance state to prepare for reading
				NS 		<= STOP;
			when STOP	=>
				INFO 		<= DATA;
				if I_O='1' then
					NS 		<= START;--IDAL;
					B 			<= '1';--DATA(7);
					BUSY 		<= '0';
				end if;
				report "There was input";
			when ERROR  =>
				NS 		<= START;--IDAL;--ERROR;
			when others =>
				NS 		<= START;--IDAL;
		end case;
	end process transmit;

	
end architecture;
