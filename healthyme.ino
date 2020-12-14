// Lisa V Huang
// 13867781
//used referring to perviously created lab4 
//uses the skeleton code given and referencing the rht03 public example
//
/*Lisa V Huang
 * 13867781
 * refers:
 * skeleton code for lab3  lab4 and rht03 public example
 * 

 */


#include "SparkFunLSM6DS3.h"
#include "WiFiEsp.h"
// Emulate Serial1 on pins 6/7 if not present
#include <SparkFun_RHT03.h>
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1(10, 11); // RX, TX
SoftwareSerial Serial2(4,5); // RX, TX
#endif
const int RHT03_DATA_PIN = 4; // RHT03 data pin
char ssid[] = ""; // your network SSID (name)
char pass[] = ""; // your network password
int status = WL_IDLE_STATUS; // the Wifi radio's status
RHT03 rht;
char server[] = "";
char content[200];
char get_request[200];
char post_request[200];
char post_data[200];
char str_temp[4] ="0";
char str_humidity[4] = "0";
// Initialize the Ethernet client object
WiFiEspClient client;

LSM6DS3 myIMU( I2C_MODE, 0x6B );
float cum_rms;
float count;
int steps_taken;
bool callibrate = false;

#define DATA_SEND_MILLIS 120000;//2 min 
#define CAL_MILLIS 700;//2 sec
unsigned long send_timer;
unsigned long callibration_timer;

void setup()
{
  // initialize serial for debugging
  Serial.begin(115200);
  while (!Serial) { ; 
  }
  // initialize serial for ESP module
  Serial1.begin(115200);
  // initialize ESP module
  WiFi.init(&Serial1);
  // initialize RTH03
  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }
  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network
    status = WiFi.begin(ssid, pass);
  }
  Serial.println("You're connected to the network");
  printWifiStatus();
  rht.begin(RHT03_DATA_PIN);
  myIMU.begin();
  cum_rms = 0;
  count = 0;
  steps_taken = 0;
  callibration_timer = millis() + CAL_MILLIS;
  send_timer = millis() + DATA_SEND_MILLIS;
  update_temp_hum();
  send_data();
}

void loop()
{
  //sensor info
  float delta_x = myIMU.readFloatAccelX();
  float delta_y = myIMU.readFloatAccelY();
  float delta_x1 = myIMU.readFloatGyroX();
  float delta_y1 = myIMU.readFloatGyroY();
  float delta_z = myIMU.readFloatAccelZ();
  float delta_z1 = myIMU.readFloatGyroZ();
  
  float rms = sqrt((delta_x * delta_x + delta_y * delta_y+delta_x1 * delta_x1 + delta_y1 * delta_y1 +delta_z1 * delta_z1)/6); // step threshold = 10
  if (millis() > callibration_timer and callibrate == false )
  {
    Serial.println("Callibrating");
    cum_rms+= rms;
    count +=1;
    callibrate =true;
    
  }else
  {
    rms= rms -cum_rms/count;
    if (rms > 20)
    {
      steps_taken +=1;
      Serial.println("stepsTaken: ");
      Serial.println(steps_taken);
    }
  }
  if (millis() > send_timer)
  {
      update_temp_hum();
      send_timer = millis()+ DATA_SEND_MILLIS;
      send_data();
  }
  delay(350);
}

void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  // print the received signal strengthx
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void update_temp_hum()
{
  // stores sensor info into the global variables
  int updateRet = rht.update();
  if (updateRet == 1)
  {
    // The humidity(), tempC(), and tempF() functions can be called -- after 
    // a successful update() -- to get the last humidity and temperature
    // value 
    float latestHumidity = rht.humidity();
    float latestTempF = rht.tempF();
    
    // Now print the values:
    Serial.println("Humidity: " + String(latestHumidity, 1) + " %");
    Serial.println("Temp (F): " + String(latestTempF, 1) + " deg F");
    dtostrf(latestTempF,2,0,str_temp);
    dtostrf(latestHumidity,2,0,str_humidity);
    Serial.println();
    
  }

}

void send_data()
{
  sprintf(get_request,"GET /update_data?temp=%s&hum=%s&steps=%d HTTP/1.1\r\nHost: 3.139.62.53\r\nConnection: close\r\n\r\n", str_temp, str_humidity,steps_taken);
  if (!client.connected()){
    Serial.println("Starting connection to server...");
    client.connect(server, 5000);
  }
  Serial.println("Connected to server");
  // Make a HTTP request
  client.print(get_request);

  delay(500);
  while(client.connected())
  {
    while (client.available()) {
      char c = client.read();
      Serial.write(c);
      delay(100);
    }
  }
  Serial.println(get_request);
  delay(1000);
}
