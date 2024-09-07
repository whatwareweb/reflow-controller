from machine import Pin
from time import sleep_us, sleep_ms

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

class LiquidCrystal:
    def __init__(self, *args):
        """A LCD can be initialized with 6, 7, 10 or 11 arguments.
        Syntax:
            6 arguments: LiquidCrystal(rs, enable, d4, d5, d6, d7)
            7 arguments: LiquidCrystal(rs, rw, enable, d4, d5, d6, d7)
            10 arguments: LiquidCrystal(rs, enable, d0, d1, d2, d3, d4, d5, d6, d7)
            11 arguments: LiquidCrystal(rs, rw, enable, d0, d1, d2, d3, d4, d5, d6, d7)
        Depending on the number of arguments we can determine if
        we want Read/Write or only Write and if we are in four bit mode or eight bit mode.
        """
        self.fourbitmode = len(args) in (6, 7)
        self.rs, self.enable = args[:2]
        if len(args) == 6:
            self.rw = 255
            self.d0, self.d1, self.d2, self.d3 = args[2:]
            self.d4, self.d5, self.d6, self.d7 = 0, 0, 0, 0
        elif len(args) == 7:
            self.rw = args[2]
            self.d0, self.d1, self.d2, self.d3 = args[3:]
            self.d4, self.d5, self.d6, self.d7 = 0, 0, 0, 0
        elif len(args) == 10:
            self.rw = 255
            self.d0, self.d1, self.d2, self.d3,
            self.d4, self.d5, self.d6, self.d7 = args[2:]
        elif len(args) == 11:
            self.rw = args[2]
            self.d0, self.d1, self.d2, self.d3,
            self.d4, self.d5, self.d6, self.d7 = args[3:]
        
        self._rs_pin = Pin(self.rs, Pin.OUT)
        # spare one pin by not setting rw
        if (self.rw != 255):
            self._rw_pin = Pin(self.rw, Pin.OUT)
        else: self._rw_pin = self.rw
        self._enable_pin = Pin(self.enable, Pin.OUT)
        # set all pins to output here, so we don't have to do it every time a character is drawn
        self._data_pins = []
        self._data_pins.append(Pin(self.d0, Pin.OUT))
        self._data_pins.append(Pin(self.d1, Pin.OUT))
        self._data_pins.append(Pin(self.d2, Pin.OUT))
        self._data_pins.append(Pin(self.d3, Pin.OUT))
        self._data_pins.append(Pin(self.d4, Pin.OUT))
        self._data_pins.append(Pin(self.d5, Pin.OUT))
        self._data_pins.append(Pin(self.d6, Pin.OUT))
        self._data_pins.append(Pin(self.d7, Pin.OUT))
        
        if self.fourbitmode:
            self._displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        else:
            self._displayfunction = LCD_8BITMODE | LCD_1LINE | LCD_5x8DOTS
        
        self.begin(16, 1)
        
    def begin(self, cols:int, lines:int, dotsize=LCD_5x8DOTS):
        if lines > 1:
            self._displayfunction |= LCD_2LINE
        self._numlines = lines
        
        self.setRowOffsets(0x00, 0x40, 0x00 + cols, 0x40 + cols)
        
        # for some 1 line displays you can select a 10 pixel high font
        if ((dotsize != LCD_5x8DOTS) & (lines == 1)):
            self._displayfunction |= LCD_5x10DOTS
          
        # SEE PAGE 45/46 FOR INITIALIZATION SPECIFICATION!
        # according to datasheet, we need at least 40 ms after power rises above 2.7 V
        # before sending commands. RPi can turn on way before 4.5 V so we'll wait 50
        sleep_ms(50)
        # Now we pull both RS and R/W low to begin commands
        self._rs_pin.value(0)
        self._enable_pin.value(0)
        if (self._rw_pin != 255): 
            self._rw_pin.value(0)
        
        # Put the LCD into 4 bit or 8 bit mode
        if not self._displayfunction & LCD_8BITMODE:
            # this is according to the Hitachi HD44780 datasheet
            # figure 24, page 46
            
            # start in 8bit mode, try to set 4 bit mode
            self.write4bits(0x03)
            sleep_us(4500)   # wait min 4.1ms
            
            # second try
            self.write4bits(0x03)
            sleep_us(4500)   # wait min 4.1ms
            
            # third go
            self.write4bits(0x03)
            sleep_us(150)
            
            # finally, set to 4-bit interface
            self.write4bits(0x02)
        else:
            # this is according to the Hitachi HD44780 datasheet
            # page 45 figure 23

            # Send function set command sequence
            self.command(LCD_FUNCTIONSET | self._displayfunction)
            sleep_us(4500)   # wait more than 4.1 ms

            # second try
            self.command(LCD_FUNCTIONSET | self._displayfunction)
            sleep_us(150)

            # third go
            self.command(LCD_FUNCTIONSET | self._displayfunction)
            
        # finally, set nr of lines, font size, etc.
        self.command(LCD_FUNCTIONSET | self._displayfunction)
        
        # turn the display on with no cursor or blinnking as default
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()

        # clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        # set the entry mode
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def setRowOffsets(self, row0:int, row1:int, row2:int, row3:int):
        self._row_offsets = [row0, row1, row2, row3]

    # ------ high level commands, for the user! ------
    
    def clear(self):
        """Clear the display"""
        self.command(LCD_CLEARDISPLAY)
        sleep_us(2000)   # this command takes a long time

    def home(self):
        """Return cursor home"""
        self.command(LCD_RETURNHOME)
        sleep_us(2000)   # this command takes a long time

    def set_cursor(self, col:int, row:int):
        """Set cursor to dedicated position"""
        max_lines = len(self._row_offsets)
        if row >= max_lines:
            row = max_lines - 1   # we count rows starting w/ 0
        if row >= self._numlines:
            row = self._numlines - 1   # we count rows starting w/ 0
        self.command(LCD_SETDDRAMADDR | (col + self._row_offsets[row]))

    def no_display(self):
        """Turn off display (quick method)"""
        self._displaycontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def display(self):
        """Turn on display (quick method)"""
        self._displaycontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def no_cursor(self):
        """Turn off cursor"""
        self._displaycontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def cursor(self):
        """Turn on cursor"""
        self._displaycontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def no_blink(self):
        """Turn off blinking cursor"""
        self._displaycontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def blink(self):
        """Turn on blinking cursor"""
        self._displaycontrol |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def scroll_display_left(self):
        """This command scrolls the display without changing the RAM"""
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scroll_display_right(self):
        """This command scrolls the display without changing the RAM"""
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def left_to_right(self):
        """This is for text that flows Left to Right"""
        self._displaymode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def right_to_left(self):
        """ This is for text that flows Right to Left"""
        self._displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def autoscroll(self):
        """This will 'right justify' text from the cursor"""
        self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)
    
    def no_autoscroll(self):
        """This will 'left justify' text from the cursor"""
        self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)
    
    def create_char(self, location:int, charmap:list):
        """Allows us to fill the first 8 CGRAM locations
        with custom characters
        """
        location &= 0x7   # we only have 8 locations 0-7
        self.command(LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self.write(charmap[i])
    
    def print(self, s:str):
        """ This function will print ASCII chars using
        the write function. It does not exist in the
        equivalent C++ library, since they import the
        Print.h library.
        """
        for c in s:
            self.write(ord(c))
    
    # ------ mid level commands, for sending data and commands ------
    
    def command(self, value:int):
        self.send(value, 0)
        
    def write(self, value:int):
        self.send(value, 1)
        return 1   # assume success
    
    # ------ low level data pushing commands ------
    
    def send(self, value:int, mode:int):
        """Write either command or data, with automatic 4/8bit selection"""
        self._rs_pin.value(mode)
        if (self._rw_pin != 255):
            self._rw_pin.value(0)
        if (self._displayfunction & LCD_8BITMODE):
            self.write8bits(value)
        else:
            self.write4bits(value>>4)
            self.write4bits(value)
        
    def pulse_enable(self):
        self._enable_pin.value(0)
        sleep_us(1)
        self._enable_pin.value(1)
        sleep_us(1)   # wait >450 ns
        self._enable_pin.value(0)
        sleep_us(100)   # commands need >37 us to settle

    def write4bits(self, value:int):
        for i in range(4):
            self._data_pins[i].value((value >> i) & 0x01)
        self.pulse_enable()
        
    def write8bits(self, value:int):
        for i in range(8):
            self._data_pins[i].value((value >> i) & 0x01)
        self.pulse_enable()