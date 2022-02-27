#include "I2Cdev.h"
#include "MPU6050.h"

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;
int imu_delay = 1; //delay in ms
int imu_sample_size = 5; //freq = 1000/(imu_delay*imu_sample_size) Hz

#define OUTPUT_READABLE_ACCELGYRO


void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    // initialize serial communication
    // (38400 chosen because it works as well at 8MHz as it does at 16MHz, but
    // it's really up to you depending on your project)
    Serial.begin(38400);

    // initialize device
    Serial.println("Initializing I2C devices...");
    accelgyro.initialize();

    // verify connection
    Serial.println("Testing device connections...");
    Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

    // use the code below to change accel/gyro offset values
    /*
    Serial.println("Updating internal sensor offsets...");
    // -76  -2359 1688  0 0 0
    Serial.print(accelgyro.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro.getZAccelOffset()); Serial.print("\t"); // 1688
    Serial.print(accelgyro.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getZGyroOffset()); Serial.print("\t"); // 0
    Serial.print("\n");
    accelgyro.setXGyroOffset(220);
    accelgyro.setYGyroOffset(76);
    accelgyro.setZGyroOffset(-85);
    Serial.print(accelgyro.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro.getZAccelOffset()); Serial.print("\t"); // 1688
    Serial.print(accelgyro.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getZGyroOffset()); Serial.print("\t"); // 0
    Serial.print("\n");
    */

}

void loop() {
    // read raw accel/gyro measurements from device
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    int total_ax = 0; int avg_ax;
    int total_ay = 0; int avg_ay;
    int total_az = 0; int avg_az;
    int total_gx = 0; int avg_gx;
    int total_gy = 0; int avg_gy;
    int total_gz = 0; int avg_gz;
    int i;
    
    for (i = 0; i < imu_sample_size; i++) {
      accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
      total_ax += ax; 
      total_ay += ay; 
      total_az += az;
      total_gx += gx; 
      total_gy += gy; 
      total_gz += gz;
      delay(imu_delay);
      }

    avg_ax = total_ax/imu_sample_size;
    avg_ay = total_ay/imu_sample_size;
    avg_az = total_az/imu_sample_size;
    avg_gx = total_gx/imu_sample_size;
    avg_gy = total_gy/imu_sample_size;
    avg_gz = total_gz/imu_sample_size;
    Serial.print("a/g:\t");
    Serial.print("avg_ax:"); Serial.print(avg_ax); Serial.print("\t\t");
    Serial.print("avg_ay:");Serial.print(avg_ay); Serial.print("\t\t");
    Serial.print("avg_az:");Serial.print(avg_az); Serial.print("\t\t");
    Serial.print("avg_gx:");Serial.print(avg_gx); Serial.print("\t\t");
    Serial.print("avg_gy:");Serial.print(avg_gy); Serial.print("\t\t");
    Serial.print("avg_gz:");Serial.println(avg_gz);

}
