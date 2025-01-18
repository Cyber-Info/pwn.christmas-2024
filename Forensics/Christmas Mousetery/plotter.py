import struct
import matplotlib.pyplot as plt

x = y = 0
x_positions = [x]
y_positions = [y]

left_click_x = []
left_click_y = []

with open("usbhid_data.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        data = bytes.fromhex(line)
        
        button_byte = data[1]
        
        left_pressed = (button_byte & 0x01) != 0
        
        dx = struct.unpack('<h', data[3:5])[0]
        dy = struct.unpack('<h', data[5:7])[0]
        
        x += dx
        y += dy
        x_positions.append(x)
        y_positions.append(y)
        
        if left_pressed:
            left_click_x.append(x)
            left_click_y.append(y)

plt.figure(figsize=(8, 6))
plt.plot(x_positions, y_positions, marker='o', label='Mouse Path', color='black')
if left_click_x:
    plt.scatter(left_click_x, left_click_y, marker='x', s=100, color='red', label='Left Click')
plt.title("USB HID Mouse Movement (Left Clicks Highlighted)")
plt.xlabel("X position")
plt.ylabel("Y position")
plt.grid(True)
plt.legend()

plt.gca().invert_yaxis()

plt.show()