#include "RTClib.h"

RTC_DS1307 rtc;

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, Raspberry Pi Pico W!");

  if (!rtc.begin()) {
    Serial.println("no rtc found");
    //exit(1);
  }
}


void loop() {

}