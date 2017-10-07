"Because I didn't write good getting-started documentation for [https://github.com/vigevenoj/esp-dht-mqtt] (esp-dht-mqtt)"

## Getting started
Clone the repository  
Create a virtualenv and activate it  
pip install -r requirements.txt  
Upload secrets.py to hardware with adafruit-ampy  
Upload sensor\_reader.py to hardware as main.py with adafruit-ampy  


## Flashing hardware
To erase the firmware,  
`esptool.py --port $(PORT) erase_flash`  
To write micropython firmware,  
`esptool.py --port $(PORT) --baud 46080 write_flash --flash_size=detect 0 $(FIRMWARE)`  
