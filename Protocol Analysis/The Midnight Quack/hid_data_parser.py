def main():
    """
    Read 'usbhid_data.txt', decode each 8-byte HID keyboard report,
    and print the resulting text (with common punctuation, symbols, etc.).
    """

    # A usage table for (unshifted) keys on a US keyboard.
    # Key: HID usage ID, Value: resulting character or special action.
    # Reference: USB HID Usage Tables 1.12 (p. 53ff) for Keyboard/Keypad Page (0x07).
    usage_table = {
        # Letters
        0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e',
        0x09: 'f', 0x0A: 'g', 0x0B: 'h', 0x0C: 'i', 0x0D: 'j',
        0x0E: 'k', 0x0F: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o',
        0x13: 'p', 0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
        0x18: 'u', 0x19: 'v', 0x1A: 'w', 0x1B: 'x', 0x1C: 'y',
        0x1D: 'z',

        # Numbers (top row)
        0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4', 0x22: '5',
        0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9', 0x27: '0',

        # Special keys
        0x28: '\n',    # Enter
        0x2A: 'BKSP',  # Backspace (we will handle specially)
        0x2B: '\t',    # Tab
        # 0x29: ESC, 0x39: CapsLock, etc., are typically ignored or special-cased

        # Symbols (unshifted)
        0x2C: ' ',   # space
        0x2D: '-',   # dash
        0x2E: '=', 
        0x2F: '[',  
        0x30: ']',  
        0x31: '\\',
        0x33: ';',
        0x34: "'",
        0x35: '`',
        0x36: ',',
        0x37: '.',
        0x38: '/',
    }

    # Map from an unshifted character to its shifted version.
    # For letters, we’ll handle uppercase in code. For these symbols, we do direct mapping.
    shift_map = {
        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&',
        '8': '*', '9': '(', '0': ')',
        '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', "'": '"',
        '`': '~', ',': '<', '.': '>', '/': '?',
    }

    def apply_shift(char: str) -> str:
        """Return the 'shifted' version of char for a US keyboard."""
        # If it's a-z, make it uppercase:
        if 'a' <= char <= 'z':
            return char.upper()
        # If it's in shift_map, return the mapped symbol
        if char in shift_map:
            return shift_map[char]
        # Otherwise return char unchanged
        return char

    output = []
    last_pressed = set()  # keep track of pressed keycodes from previous report

    with open('usbhid_data.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Each line should have 16 hex characters = 8 bytes
            if len(line) != 16:
                continue

            # Convert line to a list of 8 integers
            bytes_ = [int(line[i:i+2], 16) for i in range(0, 16, 2)]
            modifier = bytes_[0]
            pressed_keys = bytes_[2:]  # up to 6 keycodes

            # Identify the set of keys currently pressed (non-zero)
            current_pressed_set = set(k for k in pressed_keys if k != 0)

            # Detect newly pressed keys
            newly_pressed = current_pressed_set - last_pressed

            # Check if left shift (bit 1) or right shift (bit 5) is active
            #   left shift = 0x02, right shift = 0x20
            shift_active = bool((modifier & 0x02) or (modifier & 0x20))

            for keycode in newly_pressed:
                if keycode in usage_table:
                    char = usage_table[keycode]

                    # Special case: Backspace
                    if char == 'BKSP':
                        if output:
                            output.pop()  # remove last character
                        continue

                    # Normal case: possibly shift it
                    if shift_active:
                        char = apply_shift(char)

                    # Append the resulting character(s) to output
                    output.append(char)
                # else: ignore keycodes not in the table (e.g. Ctrl, Win, F-keys, etc.)

            last_pressed = current_pressed_set

    # Join everything.  Note that \n and \t remain as literal newlines and tabs.
    decoded_string = ''.join(output)
    print(decoded_string)

if __name__ == "__main__":
    main()