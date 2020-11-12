#include "LowPower.h"

int WIFI_SIG = 3;
int Pi_on = 5;
int IO = 6;
int LED = 7;
int STROBE = 9;

int RECOVER = 0;

void setup(void)
{
  pinMode(WIFI_SIG, INPUT_PULLUP);
  pinMode(Pi_on, OUTPUT);
  pinMode(IO, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
  pinMode(STROBE, OUTPUT);

  digitalWrite(Pi_on, LOW);
  digitalWrite(LED, LOW);
  digitalWrite(STROBE, LOW);

  for (int i = 0; i < 3; i++) {
    digitalWrite(LED, HIGH);
    delay(400);
    digitalWrite(LED, LOW);
    delay(100);
  }
}

void Pi_Samp() {
  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++) {
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  int WIFI_Status = digitalRead(WIFI_SIG);
  int Press_Status = digitalRead(IO);

  do {
    digitalWrite(LED, HIGH);
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
    Press_Status = digitalRead(IO);
    if (Press_Status == LOW) {
      RECOVER = 1;
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(LED, LOW);

  for (int i = 1; i <= 5; i++) {
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  digitalWrite(Pi_on, LOW);
}

void Pi_Samp_RECOVER() {

  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++) {
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
    if (Press_Status == LOW) {
      RECOVER = 1;
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(LED, LOW);

  for (int i = 1; i <= 5; i++) {
    strobe();
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

  digitalWrite(Pi_on, LOW);
}


void strobe() {
  digitalWrite(STROBE, HIGH);
  delay(100);
  digitalWrite(STROBE, LOW);
  delay(100);
  digitalWrite(STROBE, HIGH);
  delay(50);
  digitalWrite(STROBE, LOW);
  LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);

}

void loop(void)
{

  Pi_Samp();

  if (RECOVER == 1) {
    while (1) {
      Pi_Samp_RECOVER();
      //This is the sleep cycle! Set for 150 cycles of 4 seconds for 10 minutes
      for (int i = 1; i <= 300; i++) {
        strobe();
      }
    }
  }
  //This is the sleep cycle! Set for 150 cycles of 4 seconds for 10 minutes
  for (int i = 1; i <= 225; i++) {
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

}
