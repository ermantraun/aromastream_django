#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>

////////////////////////////

#include <ESP32Servo.h>

#define servoPin_1 4
#define servoPin_2 17
#define fanPin 16
#define ser_neytral 90
#define ser_min 0
#define ser_max 180

String cmd = "";

Servo servo_1;
Servo servo_2;

////////////////////////////

Preferences preferences;

bool wifiSettedUp = false;
bool dnsSettedUp = false;

String ssid = "";
String password = "";

const char* dnsSsid = "ESP32";
const char* dnsPassword = NULL;

WebServer server(80);
DNSServer dnsServer;

//----------------------------------------- Wifi credentials functions ---------------------------------------------------

void saveWifiCredentials(const String& ssid, const String& password) {
  preferences.begin("wifi", false);
  preferences.putString("ssid", ssid);
  preferences.putString("password", password);
  preferences.end();
}

void loadWifiCredentials() {
  preferences.begin("wifi", true);
  ssid = preferences.getString("ssid", "");
  password = preferences.getString("password", "");
  preferences.end();
}

void clearWifiCredentials() {
  preferences.begin("wifi", false);
  preferences.clear();
  preferences.end();
  dnsSettedUp = false;
  setupDnsServer();
}

//------------------------------------------ Setup DNS-Server --------------------------------------------------

void handleRoot() {
  const char* html = R"html(<style>body{width: 100%;margin: 0;display: flex;justify-content: center;align-items:center;background-color: #03102e}form {font-size: 50px;font-family: Arial, Helvetica, sans-serif;color: white;}input {border:1px solid black;font-size:35px;border-radius:30px;width: 100%;height: 100px;margin: 30px;padding:20px;}p{margin: 30px;text-align: center;}</style>
    <form method='post' action='/submit'>
    <p>Enter name (ssid) of your wifi</p>
    <input type='text' name='ssid' placeholder='Enter ssid'><br>
    <p>Enter password of your wifi</p>
    <input type='password' name='password' placeholder='Enter password'><br>
    <input type='submit' value='Send'>
  </form>)html"
  server.send(200, "text/html", html);
}

void handleSubmit() {
  if (server.hasArg("ssid")) {
    ssid = server.arg("ssid");
    dnsSettedUp = true;
  }
  if (server.hasArg("password")) {
    password = server.arg("password");
  }
  server.send(200, "text/plain", "OK");
  saveWifiCredentials(ssid, password);
}

void setupDnsServer() {
  WiFi.softAP(dnsSsid, dnsPassword);
  dnsServer.start(53, "*", WiFi.softAPIP());

  server.on("/", HTTP_GET, handleRoot);
  server.on("/submit", HTTP_POST, handleSubmit);

  server.begin();
}

void setup() {  
  Serial.begin(115200);
  loadWifiCredentials();
  dnsSettedUp = !ssid.isEmpty();
  if (!dnsSettedUp) setupDnsServer();

  ////////////////////////////

  pinMode(fanPin, OUTPUT);
  digitalWrite(fanPin, LOW);
  
  servo_1.attach(servoPin_1);
  servo_2.attach(servoPin_2);
  servo_1.write(ser_neytral);
  servo_2.write(ser_neytral);       
}

//-------------------------------------------------- Pathes handling -----------------------------------------------------

void addCORSHeaders() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range");
}

void handlePathA() {
  Serial.println("Received /A request");
  // Place for your code
  setServo(servo_1, ser_min);
  // ------------------
  addCORSHeaders();
  server.send(200, "text/plain", "Path A");
}

void handlePathB() {
  Serial.println("Received /B request");
  // Place for your code
  setServo(servo_1, ser_max);
  // ------------------
  addCORSHeaders();
  server.send(200, "text/plain", "Path B");
}

void handlePathC() {
  Serial.println("Received /C request");
  // Place for your code
  setServo(servo_2, ser_min);  
  // ------------------
  addCORSHeaders();
  server.send(200, "text/plain", "Path C");
}

void handlePathD() {
  Serial.println("Received /D request");
  // Place for your code
  setServo(servo_2, ser_max);
  // ------------------
  addCORSHeaders();
  server.send(200, "text/plain", "Path D");
}

void setServo (Servo &servo, uint8_t val) {
  digitalWrite(fanPin, HIGH);
  servo.write(val);
  delay(1000);
  servo.write(ser_neytral);
  delay(1000);
  digitalWrite(fanPin, LOW);
}
// --------------------------------------------- Setup Wifi-Server -------------------------------------------------------

void setupWifiServer() {
  WiFi.begin(ssid.c_str(), password.c_str());

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");
  Serial.println("IP address: " + WiFi.localIP().toString());

  if (!MDNS.begin("aromastream")) {
    Serial.println("Ошибка при настройке mDNS");
  } else {
    Serial.println("Успешно настроен mDNS по домену http://aromastream.local");
  }

  server.on("/A", HTTP_GET, handlePathA);
  server.on("/B", HTTP_GET, handlePathB);
  server.on("/C", HTTP_GET, handlePathC);
  server.on("/D", HTTP_GET, handlePathD);

  // Универсальная обработка предварительных CORS запросов
  server.onNotFound([]() {
    if (server.method() == HTTP_OPTIONS) {
      addCORSHeaders();
      server.send(204); // No Content
    } else {
      server.send(404, "text/plain", "Not Found");
    }
  });

  server.begin();
  wifiSettedUp = true;
}

void loop() {
  if (!dnsSettedUp)
    dnsServer.processNextRequest();
  else if (!wifiSettedUp)
    setupWifiServer();
  else
    server.handleClient();
}
