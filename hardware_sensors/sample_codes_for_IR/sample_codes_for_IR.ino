#include <IRremote.h> // >v3.0.0
#include <TM1637.h>
                                 
#define PIN_SEND 3
#define DIN_PIN 2
#define CLK 4
#define PIN_LED 5
#define BUZZER_PIN A0

TM1637 tm(CLK,PIN_LED);
int AMMO_COUNT = 6;

void setup()  
{  
  pinMode( DIN_PIN, INPUT );
  //pinMode( BUZZER_PIN, OUTPUT );
  IrSender.begin(PIN_SEND); // Initializes IR sender
  tm.init(); //initialises Grove 4-Digit Display
  tm.set(2); //set brightness; 0-7
  Serial.begin( 9600 );
}  
                               
void loop()  
{  
  int switch_value;
  switch_value = digitalRead( DIN_PIN ); //switch value is 1 by default
  
  tm.display(3,AMMO_COUNT);
  

  Serial.println(switch_value);
    

  
  if (switch_value == 0) {
    IrSender.sendNEC(0x0102, 0x33, true, 0); // the address 0x0102 with the command 0x33 is sent 
    AMMO_COUNT -= 1;

    
    tm.display(3,AMMO_COUNT);


    tone(BUZZER_PIN,262,50) ; // Do
    
    while (switch_value == 0) {
      switch_value = digitalRead( DIN_PIN ); // debounces trigger
      delay(10);
      }
  }
  if (AMMO_COUNT < 0) {
  //wait for reload action
  AMMO_COUNT = 6; //auto_reload dummy code
  }
  delay(10); // wait
}  
