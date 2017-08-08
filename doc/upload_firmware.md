### Download Firmware

#### Use Arduino IDE

Download and read the documents from git repos under https://github.com/uArm-Developer


#### Use command line tool: avrdude

1. First install avrdude

2. Download the hex file from the release page of the github

3. Use command line likes (i.e. for uArm Metal)
<pre>
avrdude -patmega328p -carduino -P/dev/ttyUSB0 -b115200 -D -Uflash:w:/tmp/firmware.hex:i
</pre>


#### Use GUI tools from UF

Something like ```uArmStudio```, refer to: https://forum.ufactory.cc/t/official-faq-for-uarm-swift-pro-updating


