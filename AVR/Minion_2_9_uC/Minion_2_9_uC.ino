#include "LowPower.h"

int WIFI_SIG = 3;
int Pi_on = 5;
int IO = 6;
int LED = 7;
int STROBE = 9;
int BURN = 10;

int RECOVER = 0;
int SAMPLES = 0;
int Sample_Num = 300;


void setup(void)
{
  pinMode(WIFI_SIG, INPUT_PULLUP);
  pinMode(Pi_on, OUTPUT); 
  pinMode(IO, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
  pinMode(STROBE, OUTPUT);
  pinMode(BURN, OUTPUT);

  digitalWrite(Pi_on, LOW);
  digitalWrite(LED, LOW);
  digitalWrite(STROBE, LOW);
  digitalWrite(BURN, LOW);

  for(int i = 0; i < 3; i++){
    digitalWrite(LED, HIGH);
    delay(400);
    digitalWrite(LED, LOW);
    delay(100);
  }
}

void Pi_Samp() {
  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  int WIFI_Status = digitalRead(WIFI_SIG);
  int Press_Status = digitalRead(IO);

  do {
    digitalWrite(LED, HIGH);
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
    Press_Status = digitalRead(IO);
    if (Press_Status == LOW){
      RECOVER = 1;
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(LED, LOW);

  for (int i = 1; i <= 5; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  digitalWrite(Pi_on, LOW);
}

void Pi_Samp_RECOVER() {

  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    strobe();
  }

  int WIFI_Status = digitalRead(WIFI_SIG);
  int Press_Status = digitalRead(IO);

  do {
    digitalWrite(LED, HIGH);
    strobe();
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
    Press_Status = digitalRead(IO);
    if (Press_Status == LOW){
      RECOVER = 1;
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(LED, LOW);

  for (int i = 1; i <= 5; i++){
    strobe();
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  digitalWrite(Pi_on, LOW);
}


void strobe() {
  for (int j = 1; j <= 3; j++) { 
    digitalWrite(STROBE, HIGH);
    delay(random(50, 300));
    digitalWrite(STROBE, LOW);
    delay(random(10, 100));
  }
}

void loop(void) 
{

  Pi_Samp();
  
  SAMPLES = SAMPLES + 1;

  if (RECOVER == 1 || SAMPLES > Sample_Num) {
    digitalWrite(BURN, HIGH);

    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    RECOVER = 0;

    while(1) {
      Pi_Samp_RECOVER();
    }
  }
  //This is the sleep cycle! Set for 150 cycles of 4 seconds for 10 minutes
  for (int i = 1; i <= 225; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

}




