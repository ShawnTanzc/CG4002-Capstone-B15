#include <TM1637.h>

int CLK = A5;
int DIO = 2;

TM1637 tm(CLK,DIO);

void setup() {
  // put your setup code here, to run once:
  tm.init();

  // set brightness; 0-7
  tm.set(2);
}

void loop() {
  // put your main code here, to run repeatedly:

  // example: "12:ab"
  // tm.display(position, character);
  tm.display(0,1);
  tm.display(1,2);
  tm.point(1);
  tm.display(2,10);
  tm.display(3,11);
}
