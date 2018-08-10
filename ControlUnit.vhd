-------------------------------------------------------
--! @file ControlUnit.vhd
--! @brief Control unit for the card reader system
-------------------------------------------------------

--! Use standard library
library ieee;
--! Use logic elements
		use ieee.std_logic_1164.all;
	
--! Control Unit for card communication entity
entity ControlUnit is
    port (
        CLK   		: 		in  	std_logic:='0'; 										--! Is the input clock. coorinates operations inside this unit Expects 40MHz Norminal
		  -- To card interface
		  CARD_IN: 			in		std_logic:='0'; 										--! Informs the unit of the presecns of a card to enable the communication
		  CARD_RESET: 		out	std_logic:='0'; 										--! Reset line to reset cards
		  CARD_CLK_in: 	in		std_logic:='0'; 										--! input clock for the card, for clock freezing purposes passed th
		  CARD_CLK_out:	buffer	std_logic:='0'; 										--! output clock for the card, for clock freezing purposes
		  CARD_INFO	: 		inout	std_logic_vector(7 downto 0):="00000000"; 	--! the info read or written from the card
		  CARD_VCC_SEL	: 	OUT	std_logic_vector(2 downto 0):="000"; 			--! the power class that the card logic to should be set to 
		  CARD_BUSY:		IN		std_logic:='0';										--! set high when the card control is transmitting or reciving data
		  CARD_READ:		OUT	std_logic:='0'											--! puts the I/O buffer in read mode
		
    );
end entity;

architecture behavior of ControlUnit is
	type 		CARD_CLASSES 		is (CLASS_A, CLASS_B, CLASS_C);		--! THE VALID CARD CLASSES FOR ICC's
	type 		STATES 				is (IDAL, INSERTED);
	SIGNAL	CLOCK_EN:			STD_logic:='0';
	SIGNAL 	CLOCK_COUNTER: 	integer:=0;
	SIGNAL 	MAIN_STATE: 		STATES:=IDAL;
	
	-------------------------------------------
	--! sequence of events to read one byte form a card
	function read_byte(
			data: std_logic
		) return std_logic_vector is
	begin
		
	end read_byte;
	function write_byte(
			data: std_logic_vector(7 downto 0)
		) return std_logic is
	begin
		
	end write_byte;
	-------------------------------------------
	--! sequence of events to read an ATR
	procedure get_ATR(
			CARD_STATE: std_logic
		) is
	begin
		
	end get_ATR;
	-------------------------------------------
	--! sequence of events to cold reset a card
	--! 	1. Pull the RST line to low state.
	--!	2. Pull the VCC line to high state.
	--!	3. The UART module in the interfacing device should be in the Reception mode in the software.
	--!	4. Provide the clock signal at CLK line of the smart card.
	--!	5. The RST line has to be in the low state for at least 400 clock cycles after the clock signal is
	--!		applied at CLK pin. Therefore, give a delay for at least 400 clock cycles after providing the clock
	--!		at CLK pin of the smart card.
	--!	6. Pull the RST line to high state.
	procedure cold_reset(
			CARD_CLASS: CARD_CLASSES
		) is
		
	begin
	
		CARD_RESET 		<= '0'; 				-- SET RESET TO LOW
		
		CARD_VCC_SEL 	<= "001" WHEN CARD_CLASS=CLASS_A ELSE
								"010" WHEN CARD_CLASS=CLASS_B ELSE
								"100"	WHEN CARD_CLASS=CLASS_C ELSE
								"000";		-- SET THE LOGICAL VOLTAGE TO ONE OF THE 3 CLASSES
		CARD_READ		<= '1';				-- PREPARE TO READ DATA
		CLOCK_COUNTER 	<=  0;
		CLOCK_EN			<= '1';				-- START THE CLOCK
		loop
			if CLOCK_COUNTER > 400 then	-- wait for at least 400 clock cycles
				exit;
			end if;
		end loop;	
	end cold_reset;
	-------------------------------------------
begin


	main:	process(CARD_IN)
	begin
	if CARD_IN = '1' then
	
		CASE MAIN_STATE IS
			WHEN IDAL 		=>
			
			WHEN INSERTED	=>
				for class in CARD_CLASSES loop
					cold_reset(class);
					get_ATR(CARD_IN);
				end loop;
			WHEN OTHERS		=>
			
		END CASE;
	
	end if;
	
	end process main;
	
	CARD_CLK_out 		<= CARD_IN WHEN CLOCK_EN = '1' ELSE
								CARD_CLK_out;
							
end architecture behavior;