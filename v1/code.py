import board
import busio
import digitalio
from digitalio import DigitalInOut
import adafruit_scd30
import time
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
#import adafruit_sdcard
import microcontroller
import storage
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
import math
from analogio import AnalogIn
from adafruit_display_shapes.sparkline import Sparkline

import random
from adafruit_debouncer import Debouncer

# Battery voltage functionality removed


q1 = digitalio.DigitalInOut(board.A2)
q1.direction = digitalio.Direction.OUTPUT
q1.value = True

time.sleep(2)

button_A_pin = digitalio.DigitalInOut(board.A0)
button_A_pin.direction = digitalio.Direction.INPUT
button_A_pin.pull = digitalio.Pull.UP
button_A = Debouncer(button_A_pin)

button_B_pin = digitalio.DigitalInOut(board.A1)
button_B_pin.direction = digitalio.Direction.INPUT
button_B_pin.pull = digitalio.Pull.UP
button_B = Debouncer(button_B_pin)

scd = adafruit_scd30.SCD30(board.I2C())

import displayio
import terminalio
#import neopixel
from adafruit_display_text import label
import adafruit_displayio_ssd1306

displayio.release_displays()

i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)


time.sleep(1)

exception_count = 0
sample_recorded_count = 0

time_init=time.monotonic()

interval_seconds = 2

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 1

SCREEN = 1  # Default to graphic mode

font = terminalio.FONT

line_color = 0xFFFFFF

WHITE = 0x000000

chart_width = display.width - 50  # Reduced by 10 pixels to make room for dot
chart_height = display.height - 10

sparkline1 = Sparkline(width=chart_width, height=chart_height, max_items=40, y_min=400, y_max=1000, x=35, y=5, color=line_color)

text_xoffset = -10
text_label1a = label.Label(
    font=font, text=str(sparkline1.y_top), color=line_color
)  # yTop label
text_label1a.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1a.anchored_position = (
    sparkline1.x + text_xoffset,
    sparkline1.y,
)  # set the text anchored position to the upper right of the graph

text_label1b = label.Label(
    font=font, text=str(sparkline1.y_bottom), color=line_color
)  # yBottom label
text_label1b.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1b.anchored_position = (
    sparkline1.x + text_xoffset,
    sparkline1.y + chart_height,
)  # set the text anchored position to the upper right of the graph

text_label1c = label.Label(
    font=font, text=str((sparkline1.y_top + sparkline1.y_bottom) // 2), color=line_color
)  # yMiddle label
text_label1c.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1c.anchored_position = (
    sparkline1.x + text_xoffset,
    sparkline1.y + chart_height//2,
)  # set the text anchored position to the middle right of the graph

# Current CO2 value label that appears above the latest point on the graph
current_co2_label = label.Label(
    font=font, text="---", color=line_color
)
current_co2_label.anchor_point = (0.5, 1)  # center-bottom anchor
# Position will be updated dynamically based on latest graph point

bounding_rectangle = Rect(
    sparkline1.x, sparkline1.y, chart_width, chart_height, outline=line_color
)

text_label1d = label.Label(
    font=font, text="---", color=line_color
)  # Status label
text_label1d.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1d.anchored_position = (
    #sparkline1.x + chart_width + text_xoffset,
    WIDTH * 4.5 // 5, 
    4 
)  # set the text anchored position


# Create a group to hold the sparkline, text, rectangle and tickmarks
# append them into the group (my_group)
#
# Note: In cases where display elements will overlap, then the order the
# elements are added to the group will set which is on top.  Latter elements
# are displayed on top of former elements.
rad = 2 
# Position circle at right endpoint of graphic line - will be updated dynamically
posx = sparkline1.x + chart_width
posy = sparkline1.y + chart_height // 2

circle = Circle(posx, posy, rad)
circle1 = Circle(posx,HEIGHT-posy,rad)
y_axis = Line(sparkline1.x,sparkline1.y,sparkline1.x,sparkline1.y+chart_height,color=line_color)
x_axis = Line(sparkline1.x,sparkline1.y+chart_height,sparkline1.x+chart_width,sparkline1.y+chart_height,color=line_color)

my_group = displayio.Group()

my_group.append(sparkline1)
my_group.append(text_label1a)
my_group.append(text_label1b)
my_group.append(text_label1c)
my_group.append(current_co2_label)  # Add the current CO2 label
#my_group.append(text_label1d)
#my_group.append(bounding_rectangle)
my_group.append(y_axis)
#my_group.append(x_axis)
my_group.append(circle)

big_text = displayio.Group()
text = "PVOS.ORG\nCO2 Monitor\nREV_W"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=20, y=15)
big_text.append(text_area)
batt_label = label.Label(
    font=font, text="", color=line_color
)  # yTop label
batt_label.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
batt_label.anchored_position = (
    #sparkline1.x + chart_width + text_xoffset,
    WIDTH * 4.5 // 5, 
    4 
)  # set the text anchored position
big_text.append(batt_label)
#big_text.append(circle1)

total_ticks = 2 

for i in range(total_ticks + 1):
    x_start = sparkline1.x - 5
    x_end = sparkline1.x
    y_both = int(round(sparkline1.y + (i * (chart_height) / (total_ticks))))
    if y_both > sparkline1.y + chart_height - 1:
        y_both = sparkline1.y + chart_height - 1
    my_group.append(Line(x_start, y_both, x_end, y_both, color=line_color))

# Set the display to show my_group that contains the sparkline and other graphics (default to graphic mode)
display.root_group = my_group

#SCREEN = 1 # 0: big_text; 1: my_group (graphic mode)
time.sleep(1)
text_area.text=""
text_area.x=30
text_area.y=45
text_area.font=bitmap_font.load_font("/lib/Junction-regular-24.bdf")
#text_area.font=bitmap_font.load_font("/lib/LeagueSpartan-Bold-16.bdf")

DISPLAY_ON = 1

while True:

    button_A.update()
    button_B.update()
    if button_B.fell:
        DISPLAY_ON= not DISPLAY_ON
        if(DISPLAY_ON):
            display.wake()
        else:
            display.sleep()

    if button_A.fell:
        DISPLAY_ON = 1
        display.wake()
        SCREEN = not SCREEN 
        if(SCREEN==0):
            display.root_group = big_text
        else:
            display.root_group = my_group

    #w.feed()
    current_time = time.monotonic()-time_init 


    if (scd.data_available and ((current_time > interval_seconds) or sample_recorded_count < 1)):

        try:
            temp_str = "{:.0f}C".format(scd.temperature)
            humid_str = "{:.0f}RH".format(scd.relative_humidity)

            if (scd.CO2>1):
                print(round(scd.CO2))

                if(SCREEN==0):
                    #circle1.fill=line_color
                    #time.sleep(.05)
                    #circle1.fill=WHITE
                    display.auto_refresh = False
                    text_area.text=str(round(scd.CO2))
                    batt_label.text="  " + temp_str+"  " + humid_str
                    sparkline1.add_value(round(scd.CO2))
                    display.auto_refresh = True

                else:
                    display.auto_refresh = False
                    
                    # Update circle position to right endpoint of the graph at the latest CO2 value level
                    co2_range = sparkline1.y_top - sparkline1.y_bottom
                    if co2_range > 0:
                        normalized_value = (round(scd.CO2) - sparkline1.y_bottom) / co2_range
                        circle_y = sparkline1.y + chart_height - (normalized_value * chart_height)
                    else:
                        circle_y = sparkline1.y + chart_height // 2
                    
                    circle_x = sparkline1.x + chart_width + 3  # Position dot just outside the sparkline endpoint
                    circle.x = int(circle_x)
                    circle.y = int(circle_y)
                    
                    # Alternate between filled and empty circle instead of blinking on/off
                    if circle.fill is None:
                        circle.fill = line_color  # Fill the circle
                        circle.outline = line_color
                    else:
                        circle.fill = None  # Empty circle (just outline)
                        circle.outline = line_color
    
                    # Get current CO2 value and calculate scaling BEFORE adding to sparkline
                    current_co2 = round(scd.CO2)
                    
                    # Get existing values and include the new one for scaling calculation
                    existing_values = list(sparkline1.values())
                    all_values = existing_values + [current_co2]
                    
                    # Calculate new range if needed
                    needs_rescale = False
                    if all_values:
                        max_co2 = max(all_values)
                        min_co2 = min(all_values)
                        
                        # Check if current value exceeds the sparkline's current range
                        if current_co2 > sparkline1.y_top or current_co2 < sparkline1.y_bottom:
                            needs_rescale = True
                        
                        if needs_rescale:
                            # Calculate dynamic range that shows all data points
                            # Add some padding (10%) to top and bottom
                            range_padding = max(50, (max_co2 - min_co2) * 0.1)
                            
                            new_y_min = max(0, min_co2 - range_padding)
                            new_y_max = max_co2 + range_padding
                            
                            # Round to nice numbers - y_max to multiples of 500, y_min to multiples of 50
                            new_y_min = math.floor(new_y_min / 50) * 50
                            new_y_max = math.ceil(new_y_max / 500) * 500
                            
                            # Ensure minimum range of 200 for readability
                            if new_y_max - new_y_min < 200:
                                center = (new_y_max + new_y_min) / 2
                                new_y_min = center - 100
                                new_y_max = center + 100
                                new_y_min = max(0, new_y_min)
                                # Re-round to nice numbers after adjustment
                                new_y_min = math.floor(new_y_min / 50) * 50
                                new_y_max = math.ceil(new_y_max / 500) * 500
                            
                            # Convert to integers to avoid float conversion errors
                            new_y_min = int(new_y_min)
                            new_y_max = int(new_y_max)
                            
                            print(f"CO2: {current_co2}, Rescaling to range: {new_y_min}-{new_y_max}")
                            
                            # Remove old sparkline from group
                            my_group.remove(sparkline1)
                            
                            # Create new sparkline with updated range
                            sparkline1 = Sparkline(width=chart_width, height=chart_height, max_items=40, 
                                                 y_min=new_y_min, y_max=new_y_max, 
                                                 x=35, y=5, color=line_color)
                            
                            # Re-add all existing values to new sparkline
                            for value in existing_values:
                                sparkline1.add_value(value)
                            
                            # Insert new sparkline at the beginning of the group (behind other elements)
                            my_group.insert(0, sparkline1)
                    
                    # Now add the current value
                    sparkline1.add_value(current_co2)
                    
                    print(f"After update - sparkline range: {sparkline1.y_bottom}-{sparkline1.y_top}")
                    print(sparkline1.values())
                    text_label1a.text=str(sparkline1.y_top)
                    text_label1b.text=str(sparkline1.y_bottom)
                    text_label1c.text=str((sparkline1.y_top + sparkline1.y_bottom) // 2)
                    
                    # Update current CO2 value label and position it relative to the latest point
                    current_co2_label.text = str(round(scd.CO2))
                    
                    # Calculate position: center above the dot at the end of the sparkline
                    latest_x = sparkline1.x + chart_width + 3  # Position above the dot
                    
                    # Map the latest CO2 value to y position on the graph
                    co2_range = sparkline1.y_top - sparkline1.y_bottom
                    y_midpoint = (sparkline1.y_top + sparkline1.y_bottom) / 2
                    
                    if co2_range > 0:
                        normalized_value = (round(scd.CO2) - sparkline1.y_bottom) / co2_range
                        graph_y = sparkline1.y + chart_height - (normalized_value * chart_height)
                        
                        # If CO2 value is above midpoint, display text below the line
                        # If CO2 value is below midpoint, display text above the line
                        if round(scd.CO2) > y_midpoint:
                            current_co2_label.anchor_point = (0.5, 0)  # center-top anchor
                            latest_y = graph_y + 8  # Below the line
                        else:
                            current_co2_label.anchor_point = (0.5, 1)  # center-bottom anchor
                            latest_y = graph_y - 8  # Above the line
                    else:
                        current_co2_label.anchor_point = (0.5, 1)  # center-bottom anchor
                        latest_y = sparkline1.y + chart_height // 2 - 8
                    
                    current_co2_label.anchored_position = (int(latest_x), int(latest_y))

                    #sparkline1.add_value(random.uniform(0, 1000))
                    # sparkline1.add_value already called above - removed duplicate
                    #co2_reading.text = str(round(scd.CO2))

                    display.auto_refresh = True

                    time.sleep(0.01)

                sample_recorded_count = sample_recorded_count + 1
                print(sample_recorded_count)
                time_init=time.monotonic()

        except Exception as e:
            print("*** Exception: " + str(e))
            exception_count += 1
            # break