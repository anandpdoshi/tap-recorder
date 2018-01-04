/*
 * Project tap-recorder
 * Description:
 * Author:
 * Date:
 */

int recordButtonPin = D2;
int playButtonPin = D3;
int metronomeButtonPin = D4;
int leftButtonPin = D1;
int rightButtonPin = D5;

int buttons[] = { recordButtonPin, playButtonPin, metronomeButtonPin, leftButtonPin, rightButtonPin };
char* events[] = { "record", "play", "metronome", "left", "right" };
int outputs[] = { 0, 0, 0, 0, 0 }; // the current state of the output pins
int buttonStates[] = { LOW, LOW, LOW, LOW, LOW }; // the current reading from the input pins
int lastButtonStates[] = { LOW, LOW, LOW, LOW, LOW }; // the previous reading from the input pins

unsigned long lastDebounceTimes[] = { 0, 0, 0, 0, 0 }; // the last time the output pin was toggled
unsigned long debounceDelay = 50; // the debounce time; increase if the output flickers

// Define a pin we'll place an LED on
int ledPin = D0;
int ledState = LOW;         // the current state of the output pin

void setup() {
  // Set up the LED for output
  for (int i=0; i < 5; i++) {
    pinMode(buttons[i], INPUT);
  }
  pinMode(ledPin, OUTPUT);
  // pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);

  // set initial LED state
  digitalWrite(ledPin, 0);
 }

void loop() {
  int t = millis();
  // Serial.println(sizeof(buttons));
  for (int i=0; i < 5; i++) {
    int reading = digitalRead(buttons[i]);
    // if (i==0) {
    //   Serial.print(i);
    //   Serial.print(" = ");
    //   Serial.println(reading);
    // }


    if (reading != lastButtonStates[i]) {
      // reset the debouncing timer
      lastDebounceTimes[i] = t;
    }

    if ((t - lastDebounceTimes[i]) > debounceDelay) {
      // whatever the reading is at, it's been there for longer than the debounce
      // delay, so take it as the actual current state:

      // if the button state has changed:
      if (reading != buttonStates[i]) {
        buttonStates[i] = reading;

        // only toggle the LED if the new button state is HIGH
        if (buttonStates[i] == HIGH) {
          outputs[i] = !outputs[i];

          // using reverse logic because of a glitch that I don't understand
          ledState = outputs[i];
          // ledState = !ledState;

          Serial.print(events[i]);
          Serial.print(" = ");
          Serial.println(String(outputs[i]));
          // Particle.publish(events[i], String(outputs[i]), PRIVATE);
        }


      }
    }

    // save the reading. Next time through the loop, it'll be the lastButtonState:
    lastButtonStates[i] = reading;

    // Serial.println(events[i] + " = " + String(reading));
  }

  // set the LED
  digitalWrite(ledPin, ledState);


}

// void setup() {
//   // pinMode(D1, INPUT);
//   pinMode(D1, INPUT);
//   pinMode(D2, INPUT);
//   Serial.begin(9600);
// }
//
// void loop() {
//   Serial.print(digitalRead(D1));
//   Serial.print(" ");
//   Serial.println(digitalRead(D2));
// }
