// libraries
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <EEPROM.h> 

// settings
// wi-fi settings
const char* ssid = "";
const char* password = "";

// mqtt_settings
const char* mqtt_server = "";
const int mqtt_port = ;
const char* mqtt_user = "";
const char* mqtt_password = "";
const char* mqtt_topic = "rgb/lamp";

// connections
#define led_strip 15
#define pixels_count 5

// EEPROM settings
#define EEPROM_SIZE 512     
#define EEPROM_ADDR 0       

struct StripState {
  bool stripOn;
  int currentR;
  int currentG;
  int currentB;
  int currentBrightness;
  bool rainbowMode;
};

// classes objects
WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_NeoPixel NeoPixel(pixels_count, led_strip, NEO_GRB + NEO_KHZ800);

// Global variables for strip state
StripState state = {
  true,   // stripOn
  255,    // currentR
  255,    // currentG
  255,    // currentB
  100,    // currentBrightness
  false   // rainbowMode
};

// functions
void saveStateToEEPROM() {
  EEPROM.put(EEPROM_ADDR, state);
  EEPROM.commit();  
  Serial.println("State saved to EEPROM");
}

void loadStateFromEEPROM() {
  EEPROM.get(EEPROM_ADDR, state);
  if (state.currentR < 0 || state.currentR > 255) {
    state.stripOn = true;
    state.currentR = 255;
    state.currentG = 255;
    state.currentB = 255;
    state.currentBrightness = 100;
    state.rainbowMode = false;
    saveStateToEEPROM(); 
  }
  Serial.println("State loaded from EEPROM");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("WIFI connecting...");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void sendResponse(String data) {
  String responseMessage = "a:" + data;
  Serial.print("Sending response: ");
  Serial.println(responseMessage);
  client.publish(mqtt_topic, responseMessage.c_str());
}

String getCurrentStatus() {
  String statusData = String(state.stripOn ? "1" : "0") + ":";
  statusData += String(state.currentR) + ":";
  statusData += String(state.currentG) + ":";
  statusData += String(state.currentB) + ":";
  statusData += String(state.rainbowMode ? "1" : "0") + ":";
  statusData += String(state.currentBrightness);
  return statusData;
}

void applyStripSettings() {
  if (!state.stripOn) {
    NeoPixel.fill(NeoPixel.Color(0, 0, 0));
  } else if (state.rainbowMode) {
    NeoPixel.rainbow();
  } else {
    NeoPixel.fill(NeoPixel.Color(state.currentR, state.currentG, state.currentB));
  }
  NeoPixel.setBrightness(state.currentBrightness);
  NeoPixel.show();
}

void processSetCommand(String parameters) {
  String parts[6];
  int partCount = 0;
  
  while (parameters.length() > 0 && partCount < 6) {
    int separatorIndex = parameters.indexOf(':');
    if (separatorIndex == -1) {
      parts[partCount++] = parameters;
      break;
    } else {
      parts[partCount++] = parameters.substring(0, separatorIndex);
      parameters = parameters.substring(separatorIndex + 1);
    }
  }
  
  if (partCount >= 6) {
    String newStripOn = parts[0];
    String newR = parts[1];
    String newG = parts[2];
    String newB = parts[3];
    String newRainbow = parts[4];
    String newBrightness = parts[5];
    
    bool stateChanged = false;
    
    if (newStripOn != "-1") {
      bool newState;
      if (newStripOn == "True") {
        newState = !state.stripOn;
      } else {
        newState = (newStripOn == "1" || newStripOn == "true");
      }
      if (newState != state.stripOn) {
        state.stripOn = newState;
        stateChanged = true;
      }
    }
    if (newR != "-1") {
      int val = newR.toInt();
      if (val != state.currentR) {
        state.currentR = val;
        stateChanged = true;
      }
    }
    if (newG != "-1") {
      int val = newG.toInt();
      if (val != state.currentG) {
        state.currentG = val;
        stateChanged = true;
      }
    }
    if (newB != "-1") {
      int val = newB.toInt();
      if (val != state.currentB) {
        state.currentB = val;
        stateChanged = true;
      }
    }
    if (newRainbow != "-1") {
      bool newMode;
      if (newRainbow == "True") {
        newMode = !state.rainbowMode;
      } else {
        newMode = (newRainbow == "1" || newRainbow == "true");
      }
      if (newMode != state.rainbowMode) {
        state.rainbowMode = newMode;
        stateChanged = true;
      }
    }
    if (newBrightness != "-1") {
      int brightnessValue = newBrightness.toInt();
      if (brightnessValue >= 0 && brightnessValue <= 255 && brightnessValue != state.currentBrightness) {
        state.currentBrightness = brightnessValue;
        stateChanged = true;
      }
    }
    
    Serial.println("Parsed set parameters:");
    Serial.print("On: "); Serial.println(state.stripOn);
    Serial.print("RGB: "); Serial.print(state.currentR); Serial.print(", "); Serial.print(state.currentG); Serial.print(", "); Serial.println(state.currentB);
    Serial.print("Rainbow: "); Serial.println(state.rainbowMode);
    Serial.print("Brightness: "); Serial.println(state.currentBrightness);
    
    applyStripSettings();
    
    if (stateChanged) {
      saveStateToEEPROM();
    }
    
    Serial.println("Set command processed (no response sent)");
  }
}

void processGetCommand() {
  Serial.println("Get status request received");
  sendResponse(getCurrentStatus());
}

void callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';
  String message = String((char*)payload);
  Serial.print("Received message: ");
  Serial.println(message);
  
  if (message.length() == 0 || message.charAt(0) != '$') {
    Serial.println("Ignoring message (not a command)");
    return;
  }
  
  String command = message.substring(1);
  
  if (command.startsWith("s:")) {
    String parameters = command.substring(2);
    processSetCommand(parameters);
  }
  else if (command == "g") {
    processGetCommand();
  }
  else {
    Serial.println("Unknown command: " + command);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(mqtt_topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("Connecting error, code: ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

// main funcs
void setup() {
  Serial.begin(115200);
  
  EEPROM.begin(EEPROM_SIZE);
  loadStateFromEEPROM();
  
  NeoPixel.begin();
  NeoPixel.setBrightness(state.currentBrightness);
  applyStripSettings();
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  if (state.stripOn && state.rainbowMode) {
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 20) {
      NeoPixel.rainbow();
      NeoPixel.show();
      lastUpdate = millis();
    }
  }
}