# reflow-controller
pi pico project to control reflow oven

This project is currently under very heavy development, so expect some bugs as of now while i do more testing

## how to use
 - download release zip
 - upload all files in the to the micropython device
 - check the wokwi diagram below for wiring diagram, and add a toaster oven on the relay that will be the actual oven

## wifi connection
 - currently wifi is disabled due to wokwi issues, these will be fixed soon(tm)
 - add your wifi network in the file `networks.json` in this format, and it will automatically connect to the 1st network:
```json
{
	"ssid":  "your-wifi-name",
	"pass":  "your-wifi-password"
}
```

## wokwi simulation
 - this project can be simulated in wokwi here is the link https://wokwi.com/projects/405794574081822721
 - wokwi is not 100% accurate so wifi features have been disabled, also there is no toaster oven in wokwi

## temperature sensing device
 - it is recomended to use a thermocouple because it is easy to find high temperature thermocouples, code coming soon for this
 - a ntc thermistor can also be used but can have issues at higher temperatures

## solder pastes
the currently supported solder pastes can be found in `profiles.json`

all lead-free solder pastes have the "LF" marking at the end of the name for easy differentiation, if you open a PR please include this if the paste you are adding is lead-free

if you would like to use a solder paste not currently included in the project please do __one__ of these things
1. open a github issue - please provide the name of the solder paste and preferably a link to a datasheet (preferred)
2. make your own profile like the example profiles found in `profiles.json` and open a pull request with the name of the paste and a datasheet
3. message me with the contact info found on my website https://whatware.net/about
