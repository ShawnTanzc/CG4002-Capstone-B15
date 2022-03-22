#include <IRremote.h> // >v3.0.0
#include <TM1637.h>
          
#define PIN_RECV 3
#define CLK 4
#define PIN_LED 5
#define BUZZER_PIN 2

TM1637 tm(CLK,PIN_LED);
int HEALTH_COUNT = 100; //initialises health count

void setup()  
{  
  Serial.begin(9600); //initialize serial connection to print on the Serial Monitor of the Arduino IDE
  IrReceiver.begin(PIN_RECV); // Initializes the IR receiver object
  pinMode( BUZZER_PIN, OUTPUT );
  tm.init();//initialises Grove 4-Digit Display
  tm.set(2); //set brightness; 0-7
}  
                               
void loop()  
{  
  digitalWrite(BUZZER_PIN,LOW);
  
  tm.display(3, HEALTH_COUNT % 10);    //displays health count
  tm.display(2, HEALTH_COUNT / 10 % 10);   
  tm.display(1, HEALTH_COUNT / 100 % 10);   
  tm.display(0, "");   
  
  if (IrReceiver.decode()) {
    //Serial.println("Received something...");    
    //IrReceiver.printIRResultShort(&Serial); // Prints a summary of the received data
    //Serial.println();
    //IrReceiver.resume(); 

    if (IrReceiver.decodedIRData.protocol != UNKNOWN && IrReceiver.decodedIRData.command == 0x33) {
      IrReceiver.printIRResultShort(&Serial); // If data received is in proper packet format
      Serial.println();

      // Inform server that player has taken damage

      digitalWrite(BUZZER_PIN,HIGH);
      delay(20);
      digitalWrite(BUZZER_PIN,LOW);
      //tone(BUZZER_PIN,440,50) ; // La
    
      HEALTH_COUNT -= 10;
    
      } 
      
    if (HEALTH_COUNT <= 0) {
    //wait for game end action
    HEALTH_COUNT = 100; //auto_revive dummy code
    }
  
    delay(10); // wait
    IrReceiver.resume(); // Enables to receive the next IR signal

  }  
}  
