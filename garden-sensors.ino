#include <JsonParserGeneratorRK.h>
#include <Adafruit_DHT_Particle.h>
#include <MQTT.h>
#include <BH1750.h>

BH1750 sensor(0x23, Wire);
void callback(char* topic, byte* payload, unsigned int length);
MQTT client("broker.emqx.io", 1883, callback, true);
#define DHTPIN D4     // what pin we're connected to
#define DHTTYPE DHT11        // DHT 11 
DHT dht(DHTPIN, DHTTYPE);

void setup() {
    //start serial com
    Serial.begin(9600); // initialize serial communication at 9600 bits per second
    dht.begin();
    RGB.control(true);
    //setup light sensor
    sensor.begin();
    sensor.set_sensor_mode(BH1750::forced_mode_high_res2);
    // connect to the server
    client.connect("Tom");
    // publish/subscribe
    if (client.isConnected()) {
        client.publish("SIT210/wave","connected");
        Serial.print("connected");
        client.subscribe("SIT210/wave/#");
    }
}

// recieve message
void callback(char* topic, byte* payload, unsigned int length) {
    Serial.println(topic);
    char p[length + 1];
    memcpy(p, payload, length);
    p[length] = NULL;
}

float lightSensorLoop()
{
    sensor.make_forced_measurement();
    return sensor.get_light_level();
}
float moistureSensorLoop()
{
    return analogRead(A4);
}
float tempSensorLoop()
{
// Reading temperature or humidity takes about 250 milliseconds!
    float t = dht.getTempCelcius();

    delay(5000);
    // Check if any reads failed and exit early (to try again).
    if (isnan(t)) {
        tempSensorLoop(); //if it fails to read, try again
        // Serial.println("Failed to read temperature from DHT sensor!");
        // t = -1;
    }
    return(t);
}
float humiSensorLoop()
{
    // Sensor readings may also be up to 2 seconds 
    float h = dht.getHumidity();
    delay(5000);
    // Check if any reads failed and exit early (to try again).
    if (isnan(h)) {
        humiSensorLoop();
        // Serial.println("Failed to read humidity from DHT sensor!");
        // h = -1;
    }
    return(h);
}

void printer(float l, float m, float h, float t)//purely for debugging
{
    Serial.println("_________________________________________________________________________");
    Serial.println(Time.timeStr());
    Serial.println("_________________________________________________________________________");
    Serial.println();
    
    Serial.print("Light Level: "); 
    Serial.print(l);
    Serial.println("Lux"); 
    
    Serial.print("Moisture Level: "); 
    Serial.print(m);
    Serial.println();
    
    Serial.print("Humidity: "); 
    Serial.print(h);
    Serial.println("%");
    
    Serial.print("Temperature: "); 
    Serial.print(t);
    Serial.println("*C");
    Serial.println("_________________________________________________________________________");
}
//create a JSON payload to send the temp and humidity data together
void createEventPayload(float l, float m, float t, float h){
    JsonWriterStatic<256> jw;
    {
        JsonWriterAutoObject obj(&jw);
        jw.insertKeyValue("light: ", l);
        jw.insertKeyValue("moisture: ", m);
        jw.insertKeyValue("temp: ", t);
        jw.insertKeyValue("humi: ", h);
    }
    // Publish data to the Particle cloud. 
    client.publish("SIT210/wave", jw.getBuffer());
}


void loop() {
    float lightLevel = lightSensorLoop();
    float moistureLevel = moistureSensorLoop();
    float humidityLevel = humiSensorLoop();
    float tempLevel = tempSensorLoop();
    client.connect("Tom");
    
    if (client.isConnected() == false)
    {
        Serial.println("Disconnected");
    }
    else
    {
        client.loop();
        createEventPayload(lightLevel, moistureLevel, humidityLevel, tempLevel);
        client.disconnect();
        //printer(lightLevel, moistureLevel, humidityLevel, tempLevel);
        delay(10000);
    }
}
