#!/usr/bin/env python
"""
Retro Clock - Classic Style LED Matrix         # Flip animation state
        self.manual_flip_triggered = False
        self.flip_animation_frames = 8  # Number of frames in flip animation
        self.flip_duration = 0.4  # Total duration in seconds
        
        # Denver/Mountain Time timezone (UTC-7)
        self.denver_timezone = timezone(timedelta(hours=-7))  # Mountain Standard Time
        
        print("🕰️  Retro Flip Clock initialized - Classic 1970s style")
        print(f"Matrix size: {self.width}x{self.height}")
        print("🏔️  Timezone: Denver/Mountain Time (UTC-7)")A minimalist clock display inspired by vintage Twemco and similar designs:
- Clean, blocky digit display
- Orange background with white frame and black digit windows
- Hour:minute format in large, readable font
- Classic proportions and spacing
- Optional AM/PM indicator
- Simple number changes with no complex animations

Usage:
    sudo python retro-clock.py
"""

import time
import sys
import os
from datetime import datetime, timezone, timedelta

try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    import select  # Unix/Linux
    WINDOWS = False

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from matrix_base import MatrixBase
from font_manager import FontManager
from color_palette import ColorPalette
from config_manager import ConfigManager


class RetroClock(MatrixBase):
    """Classic clock display with vintage 1970s aesthetic."""
    
    def __init__(self):
        # Initialize configuration manager
        self.config = ConfigManager()
        
        # Initialize matrix with configuration from ConfigManager (handled by MatrixBase)
        super().__init__()
        
        # Initialize shared components with clean default theme
        self.font_manager = FontManager()
        self.color_palette = ColorPalette('default')  # Clean white on black
        
        # Load fonts - use the largest available for authentic flip clock look
        self.digit_font = self.font_manager.get_font('xxlarge')  # 9x18B for main digits
        self.ampm_font = self.font_manager.get_font('tiny')      # 4x6 for AM/PM
        
        # Authentic Twemco flip clock colors
        self.background_color = self.color_palette.get_color((200, 80, 0))    # Darker orange background
        self.frame_color = self.color_palette.get_color('white')               # White trim/frame
        self.window_color = self.color_palette.get_color('black')              # Black digit windows
        self.digit_color = self.color_palette.get_color('white')               # White digits
        self.ampm_color = self.color_palette.get_color('white')                # White AM indicator
        
        # Store previous time for flip detection
        self.previous_time = ""
        self.previous_hour = ""
        self.previous_minute = ""
        self.show_ampm = True  # Option to show AM/PM
        
        # Animation configuration
        self.animation_mode = "simple"  # "simple" or "scroll_down"
        self.manual_flip_triggered = False
        self.flip_animation_frames = 8  # Number of frames in flip animation
        self.flip_duration = 0.4  # Total duration in seconds
        
        # Scroll animation parameters
        self.scroll_animation_frames = 20  # Number of frames for scroll animation
        self.scroll_duration = 0.6  # Total duration for scroll animation in seconds
        
        # Timezone configuration - Denver/Mountain Time
        self.denver_timezone = timezone(timedelta(hours=-6))  # Mountain Time
        
        print("🕰️  Retro Flip Clock initialized - Classic 1970s style")
        print(f"Matrix size: {self.width}x{self.height}")
        print("�️  Timezone: Denver/Mountain Time")
    
    def get_current_time(self):
        """Get current time in Denver/Mountain timezone (UTC-6)."""
        # Get UTC time and convert to Mountain Time (UTC-6)
        utc_now = datetime.now(timezone.utc)
        denver_time = utc_now.astimezone(self.denver_timezone)
        return denver_time

    def draw_flip_time(self):
        """Draw time in authentic Twemco flip clock style with separate windows."""
        now = self.get_current_time()
        
        # Format time components separately
        hour = now.strftime("%I")
        if hour.startswith("0"):
            hour = " " + hour[1:]  # Replace leading zero with space for authenticity
        
        minute = now.strftime("%M")  # Always two digits for minutes
        
        # Draw the digit windows and digits
        self.draw_digit_windows(hour, minute)
        
        # Draw AM indicator (like the original - small text on orange background)
        if self.show_ampm:
            ampm = now.strftime("%p").lower()  # Use lowercase "am" like the original
            
            # Position AM/PM in upper left area on orange background
            ampm_x = 4
            ampm_y = 7
            
            current_x = ampm_x
            for char in ampm:
                char_width = self.draw_text(self.ampm_font, current_x, ampm_y,
                                          self.ampm_color, char)
                current_x += char_width
    
    def draw_background_and_frame(self):
        """Draw the orange background and dual frame like a real Twemco clock."""
        # Fill entire background with orange
        for x in range(64):
            for y in range(32):
                self.set_pixel(x, y, self.background_color)
        
        # Draw orange outer frame border (1-pixel thick)
        # Top and bottom borders
        for x in range(64):
            self.set_pixel(x, 0, self.background_color)
            self.set_pixel(x, 31, self.background_color)
        
        # Left and right borders  
        for y in range(32):
            self.set_pixel(0, y, self.background_color)
            self.set_pixel(63, y, self.background_color)
        
        # Draw white inner frame border (1-pixel thick)
        # Top and bottom borders
        for x in range(1, 63):
            self.set_pixel(x, 1, self.frame_color)
            self.set_pixel(x, 30, self.frame_color)
        
        # Left and right borders  
        for y in range(1, 31):
            self.set_pixel(1, y, self.frame_color)
            self.set_pixel(62, y, self.frame_color)
    
    def draw_digit_windows(self, hour_str, minute_str):
        """Draw black rectangular windows for the digits like flip cards."""
        # Define window positions (two separate rectangles for hour and minute)
        # Hour window (left side)
        hour_window = {
            'x': 6, 'y': 8, 'width': 22, 'height': 16
        }
        
        # Minute window (right side)  
        minute_window = {
            'x': 36, 'y': 8, 'width': 22, 'height': 16
        }
        
        # Draw hour window (black rectangle)
        for x in range(hour_window['x'], hour_window['x'] + hour_window['width']):
            for y in range(hour_window['y'], hour_window['y'] + hour_window['height']):
                if 0 <= x < 64 and 0 <= y < 32:
                    self.set_pixel(x, y, self.window_color)
        
        # Draw minute window (black rectangle)
        for x in range(minute_window['x'], minute_window['x'] + minute_window['width']):
            for y in range(minute_window['y'], minute_window['y'] + minute_window['height']):
                if 0 <= x < 64 and 0 <= y < 32:
                    self.set_pixel(x, y, self.window_color)
        
        # Draw white digits centered in their respective windows
        # Hour digits
        hour_width = 0
        for char in hour_str:
            if char != ' ':
                hour_width += self.digit_font.CharacterWidth(ord(char))
        hour_x = hour_window['x'] + (hour_window['width'] - hour_width) // 2
        hour_y = hour_window['y'] + 14  # Adjust for font baseline
        
        current_x = hour_x
        for char in hour_str:
            if char != ' ':
                char_width = self.draw_text(self.digit_font, current_x, hour_y, 
                                          self.digit_color, char)
                current_x += char_width
        
        # Minute digits
        minute_width = 0
        for char in minute_str:
            minute_width += self.digit_font.CharacterWidth(ord(char))
        minute_x = minute_window['x'] + (minute_window['width'] - minute_width) // 2  
        minute_y = minute_window['y'] + 14  # Adjust for font baseline
        
        current_x = minute_x
        for char in minute_str:
            char_width = self.draw_text(self.digit_font, current_x, minute_y,
                                      self.digit_color, char)
            current_x += char_width
    
    def simple_change(self, old_text, new_text, is_hour=True):
        """Simply change from old number to new number - no animation."""
        print(f"🔄 Changing {'hour' if is_hour else 'minute'}: {old_text} → {new_text}")
        # The display will be updated in the main loop, so we don't need to do anything here
        pass
    
    def scroll_down_change(self, old_text, new_text, is_hour=True):
        """Animate old digit scrolling down out of frame while new digit scrolls down from above."""
        print(f"📜 Scroll animation - {'hour' if is_hour else 'minute'}: {old_text} → {new_text}")
        
        # Define window positions based on which digit is changing
        if is_hour:
            window = {'x': 6, 'y': 8, 'width': 22, 'height': 16}
        else:
            window = {'x': 36, 'y': 8, 'width': 22, 'height': 16}
        
        # Calculate text positioning within the window for both old and new text
        old_text_width = 0
        for char in old_text:
            if char != ' ':
                old_text_width += self.digit_font.CharacterWidth(ord(char))
        
        new_text_width = 0
        for char in new_text:
            if char != ' ':
                new_text_width += self.digit_font.CharacterWidth(ord(char))
        
        old_text_x = window['x'] + (window['width'] - old_text_width) // 2
        new_text_x = window['x'] + (window['width'] - new_text_width) // 2
        baseline_y = window['y'] + 14  # Normal baseline position
        
        # Animate scrolling down
        frame_duration = self.scroll_duration / self.scroll_animation_frames
        
        for frame in range(self.scroll_animation_frames + 1):
            # Calculate vertical offset for this frame
            progress = frame / self.scroll_animation_frames
            scroll_distance = window['height'] + 8  # Total distance to scroll
            scroll_offset = int(progress * scroll_distance)
            
            # Clear and redraw the entire display
            self.clear()
            self.draw_background_and_frame()
            
            # Calculate positions for old and new text
            old_text_y = baseline_y + scroll_offset  # Old text scrolls down from normal position
            new_text_y = baseline_y - scroll_distance + scroll_offset  # New text starts above, scrolls down
            
            # Draw the black window background first
            for x in range(window['x'], window['x'] + window['width']):
                for y in range(window['y'], window['y'] + window['height']):
                    if 0 <= x < 64 and 0 <= y < 32:
                        self.set_pixel(x, y, self.window_color)
            
            # Draw the scrolling digits with proper clipping to window boundaries
            self.draw_clipped_text(old_text, old_text_x, old_text_y, window)
            self.draw_clipped_text(new_text, new_text_x, new_text_y, window)
            # Draw the non-changing digit in its normal position
            now = self.get_current_time()
            current_hour = now.strftime("%I").replace("0", " ", 1) if now.strftime("%I").startswith("0") else now.strftime("%I")
            current_minute = now.strftime("%M")
            
            if is_hour:
                # Draw minute normally (not changing)
                self.draw_static_digit(current_minute, is_hour=False)
            else:
                # Draw hour normally (not changing)  
                self.draw_static_digit(current_hour, is_hour=True)
            
            # Draw AM/PM indicator
            if self.show_ampm:
                ampm = now.strftime("%p").lower()
                ampm_x = 4
                ampm_y = 7
                current_x = ampm_x
                for char in ampm:
                    char_width = self.draw_text(self.ampm_font, current_x, ampm_y,
                                              self.ampm_color, char)
                    current_x += char_width
            
            self.swap()
            time.sleep(frame_duration)
        
        # After animation, draw the final state normally
        self.clear()
        self.draw_background_and_frame() 
        self.draw_flip_time()
        self.swap()
    
    def draw_clipped_text(self, text, text_x, text_y, window):
        """Draw text with pixel-perfect clipping to window boundaries."""
        # Only draw if the text might be visible in the window area
        if (text_y > window['y'] - 25 and text_y < window['y'] + window['height'] + 10):
            # Draw the text normally first
            current_x = text_x
            for char in text:
                if char != ' ':
                    char_width = self.draw_text(self.digit_font, current_x, text_y,
                                              self.digit_color, char)
                    current_x += char_width
            
            # Now "clip" by redrawing background/frame over areas outside the window
            # Clear area above the window
            for x in range(max(0, window['x'] - 10), min(64, window['x'] + window['width'] + 10)):
                for y in range(max(0, window['y'] - 25), window['y']):
                    if 0 <= x < 64 and 0 <= y < 32:
                        # Determine what color this pixel should be (background or frame)
                        if x <= 1 or x >= 62 or y <= 1 or y >= 30:
                            self.set_pixel(x, y, self.background_color)
                        elif x <= 2 or x >= 61 or y <= 2 or y >= 29:
                            self.set_pixel(x, y, self.frame_color)
                        else:
                            self.set_pixel(x, y, self.background_color)
            
            # Clear area below the window
            for x in range(max(0, window['x'] - 10), min(64, window['x'] + window['width'] + 10)):
                for y in range(window['y'] + window['height'], min(32, window['y'] + window['height'] + 25)):
                    if 0 <= x < 64 and 0 <= y < 32:
                        # Determine what color this pixel should be (background or frame)
                        if x <= 1 or x >= 62 or y <= 1 or y >= 30:
                            self.set_pixel(x, y, self.background_color)
                        elif x <= 2 or x >= 61 or y <= 2 or y >= 29:
                            self.set_pixel(x, y, self.frame_color)
                        else:
                            self.set_pixel(x, y, self.background_color)
            
            # Clear area to the left of the window
            for x in range(max(0, window['x'] - 10), window['x']):
                for y in range(max(0, window['y'] - 5), min(32, window['y'] + window['height'] + 5)):
                    if 0 <= x < 64 and 0 <= y < 32:
                        # Determine what color this pixel should be (background or frame)
                        if x <= 1 or x >= 62 or y <= 1 or y >= 30:
                            self.set_pixel(x, y, self.background_color)
                        elif x <= 2 or x >= 61 or y <= 2 or y >= 29:
                            self.set_pixel(x, y, self.frame_color)
                        else:
                            self.set_pixel(x, y, self.background_color)
            
            # Clear area to the right of the window
            for x in range(window['x'] + window['width'], min(64, window['x'] + window['width'] + 10)):
                for y in range(max(0, window['y'] - 5), min(32, window['y'] + window['height'] + 5)):
                    if 0 <= x < 64 and 0 <= y < 32:
                        # Determine what color this pixel should be (background or frame)
                        if x <= 1 or x >= 62 or y <= 1 or y >= 30:
                            self.set_pixel(x, y, self.background_color)
                        elif x <= 2 or x >= 61 or y <= 2 or y >= 29:
                            self.set_pixel(x, y, self.frame_color)
                        else:
                            self.set_pixel(x, y, self.background_color)

    def draw_static_digit(self, text, is_hour=True):
        """Draw a single digit group (hour or minute) in its normal position."""
        if is_hour:
            window = {'x': 6, 'y': 8, 'width': 22, 'height': 16}
        else:
            window = {'x': 36, 'y': 8, 'width': 22, 'height': 16}
        
        # Draw window background
        for x in range(window['x'], window['x'] + window['width']):
            for y in range(window['y'], window['y'] + window['height']):
                if 0 <= x < 64 and 0 <= y < 32:
                    self.set_pixel(x, y, self.window_color)
        
        # Draw digits
        text_width = 0
        for char in text:
            if char != ' ':
                text_width += self.digit_font.CharacterWidth(ord(char))
        
        text_x = window['x'] + (window['width'] - text_width) // 2
        text_y = window['y'] + 14
        
        current_x = text_x
        for char in text:
            if char != ' ':
                char_width = self.draw_text(self.digit_font, current_x, text_y,
                                          self.digit_color, char)
                current_x += char_width
    
    def check_for_input(self):
        """Check for keyboard input in a non-blocking way (cross-platform)."""
        try:
            if WINDOWS:
                # Windows implementation
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b' ' or key == b'\r':  # Space or Enter key
                        self.manual_flip_triggered = True
                        return True
                    elif key == b'+' or key == b'=':  # Plus key to increase brightness
                        self.increase_brightness()
                        return True
                    elif key == b'-' or key == b'_':  # Minus key to decrease brightness
                        self.decrease_brightness()
                        return True
                    elif key == b'a' or key == b'A':  # 'A' key to toggle animation mode
                        self.toggle_animation_mode()
                        return True
            else:
                # Unix/Linux implementation
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.readline().strip()
                    if line == ' ' or line == '':  # Space or Enter key
                        self.manual_flip_triggered = True
                        return True
                    elif line == '+' or line == '=':  # Plus key to increase brightness
                        self.increase_brightness()
                        return True
                    elif line == '-' or line == '_':  # Minus key to decrease brightness
                        self.decrease_brightness()
                        return True
                    elif line == 'a' or line == 'A':  # 'A' key to toggle animation mode
                        self.toggle_animation_mode()
                        return True
        except:
            # Fallback - no input detection
            pass
        return False
    
    def increase_brightness(self):
        """Increase brightness by 10%."""
        current = self.matrix.brightness
        new_brightness = min(100, current + 10)
        self.set_brightness(new_brightness)
        print(f"🔆 Brightness: {new_brightness}%")
    
    def decrease_brightness(self):
        """Decrease brightness by 10%."""
        current = self.matrix.brightness
        new_brightness = max(1, current - 10)
        self.set_brightness(new_brightness)
        print(f"🔅 Brightness: {new_brightness}%")
    
    def toggle_animation_mode(self):
        """Toggle between simple and scroll-down animation modes."""
        if self.animation_mode == "simple":
            self.animation_mode = "scroll_down"
            print("📜 Animation mode: Scroll Down")
        else:
            self.animation_mode = "simple"
            print("🔄 Animation mode: Simple")
        print(f"Animation mode changed to: {self.animation_mode}")
    
    def run(self):
        """Main display loop with flip animations."""
        print("🕰️  Starting Authentic Twemco-Style Clock - Press CTRL-C to stop")
        print("🧡 Orange background with white frame and black digit windows")
        print("⌨️  Controls:")
        print("   SPACE = Manual refresh")
        print("   + = Increase brightness")
        print("   - = Decrease brightness")
        print("   A = Toggle animation mode (simple/scroll-down)")
        print(f"🎬 Current animation mode: {self.animation_mode}")
        
        # Initialize previous time values
        now = self.get_current_time()
        self.previous_hour = now.strftime("%I").replace("0", " ", 1) if now.strftime("%I").startswith("0") else now.strftime("%I")
        self.previous_minute = now.strftime("%M")
        
        try:
            while True:
                # Get current time
                now = self.get_current_time()
                current_hour = now.strftime("%I").replace("0", " ", 1) if now.strftime("%I").startswith("0") else now.strftime("%I")
                current_minute = now.strftime("%M")
                
                # Check for keyboard input
                self.check_for_input()
                
                # Check if time changed or manual flip triggered
                hour_changed = current_hour != self.previous_hour
                minute_changed = current_minute != self.previous_minute
                
                # Handle time changes with selected animation mode
                animation_occurred = False
                
                if hour_changed:
                    if self.animation_mode == "simple":
                        self.simple_change(self.previous_hour, current_hour, is_hour=True)
                    else:  # scroll_down
                        self.scroll_down_change(self.previous_hour, current_hour, is_hour=True)
                        animation_occurred = True
                    
                if minute_changed:
                    if self.animation_mode == "simple":
                        self.simple_change(self.previous_minute, current_minute, is_hour=False)
                    else:  # scroll_down
                        self.scroll_down_change(self.previous_minute, current_minute, is_hour=False)
                        animation_occurred = True
                    
                # Handle manual flip trigger
                if self.manual_flip_triggered:
                    print("🔄 Manual animation triggered - forcing scroll animation for debugging")
                    # Force animation even if time hasn't changed (for debugging)
                    if self.animation_mode == "scroll_down":
                        # Animate both hour and minute for visual effect
                        self.scroll_down_change(current_hour, current_hour, is_hour=True)
                        self.scroll_down_change(current_minute, current_minute, is_hour=False)
                        animation_occurred = True
                    else:
                        print("🔄 Manual refresh (simple mode)")
                    self.manual_flip_triggered = False
                
                # Update previous values
                self.previous_hour = current_hour
                self.previous_minute = current_minute
                
                # Draw normal time display (skip if animation just occurred)
                if not animation_occurred:
                    self.clear()
                    self.draw_background_and_frame()
                    self.draw_flip_time()
                    self.swap()
                
                # Update every 0.1 seconds for responsive input
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏰️  Clock stopped - Time stands still!")
        finally:
            self.clear()


if __name__ == "__main__":
    clock = RetroClock()
    clock.run()