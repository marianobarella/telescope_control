/*

24 nov 2020
Buenos Aires, Argentina

Telescope right-ascension and declination axis control using Arduino and Python.

An Arduino MEGA board coupled with a L293D motor shield controls two DC motors: one motor 
for right-ascension axis and the other for declination.

Two MR-04A DC motors were purchased to IGNIS Motor http://www.ignismotor.com/

This code is based on Robin2 code for controlling a servo and LEDs.
Available at https://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764

It uses the MotorDriver library of CuriosityGym. 
Available at https://github.com/CuriosityGym/motordriver and the library manager also

Author: Mariano Barella, marianobarella@gmail.com

*/

#include <MotorDriver.h>

// -------------------- definitions
// -------------------- definitions
// -------------------- definitions

MotorDriver RA;
MotorDriver DE;

int newVel = 0;

int velRA = 0;
int absVelRA = 0;

int velDEC = 0;
int absVelDEC = 0;

int RAMotorNumber = 1;
int DECMotorNumber = 3;

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newInstructionFromPC = false;

char axis[buffSize] = {0};

unsigned long curMillis;

// -------------------- config
// -------------------- config
// -------------------- config

void setup() {
  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
}

// -------------------- main
// -------------------- main
// -------------------- main

void loop() {
  
  // get time  
  curMillis = millis();

  // Read the instructions and reply
  getInstructionFromPC();
  replyToPC();
  
  // move motor if needed
  moveMotor();
}

// -------------------- auxiliary functions
// -------------------- auxiliary functions
// -------------------- auxiliary functions

void getInstructionFromPC() {

  // receive instructions from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();

    // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newInstructionFromPC = true;
      // reset buffer
      inputBuffer[bytesRecvd] = 0;
      // read instruction
      parseInstruction();
    }
    
    if(readInProgress) {
      // collect input
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

//=============
 
void parseInstruction() {

  // split the intruction into its parts
    
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,",");      // get the first part - the axis
  strcpy(axis, strtokIndx); // copy it to axis
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  newVel = atoi(strtokIndx);     // convert this part to an integer
  
}

//=============

void moveRA() {

  // move right-ascension axis
  
  if (newVel != velRA) {
    
    absVelRA = abs(newVel);
    
    if (newVel > 0) {
      
      Serial.println("Moving RA forward");
      RA.motor(RAMotorNumber, FORWARD, absVelRA);
    }
    
    else if (newVel < 0) {
      
      Serial.println("Moving RA backward");
      RA.motor(RAMotorNumber, BACKWARD, absVelRA);
    }
    
    else {
      
      Serial.println("Stop RA");
      RA.motor(RAMotorNumber, RELEASE, 0);
    }
  }

  velRA = newVel;
}

//=============

void moveDEC() {

  // move declination axis
  
  if (newVel != velDEC) {

    absVelDEC = abs(newVel);
    
    if (newVel > 0) {
      Serial.println("Moving DEC forward");
      DE.motor(DECMotorNumber, FORWARD, absVelDEC);
    }
    
    else if (newVel < 0) {
      Serial.println("Moving DEC backward");
      DE.motor(DECMotorNumber, BACKWARD, absVelDEC);
    }
    
    else {
      Serial.println("Stop DEC");
      DE.motor(DECMotorNumber, RELEASE, 0);
    }

    velDEC = newVel;
  }
}

//=============

void moveMotor() {

  // set the speed of the selected axis
  
  if (strcmp(axis, "RA") == 0) {
     moveRA();
  }

  if (strcmp(axis, "DEC") == 0) {
     moveDEC();
  }

}

//=============

void replyToPC() {

  if (newInstructionFromPC) {
    newInstructionFromPC = false;
    Serial.print("< Axis ");
    Serial.print(axis);
    Serial.print(" newVel ");
    Serial.print(newVel);
    Serial.print(" Time ");
    Serial.print(curMillis >> 10); // divide by 512 is approx = half-seconds
    Serial.println(" s >");
  }
}

// -------------------- end of auxiliary functions
// -------------------- end of auxiliary functions
// -------------------- end of auxiliary functions
