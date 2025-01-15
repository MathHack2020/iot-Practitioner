/***********************************
- Retrieve your IoT certificates from AWS Secrets Manager (using AWS SDK v3),
- Connect to AWS IoT Core with the aws-iot-device-sdk,
- Generate a random payload that matches your desired JSON structure,
- Publish the payload to a topic.
 ***********************************/

const {
    SecretsManagerClient,
    GetSecretValueCommand
  } = require('@aws-sdk/client-secrets-manager');
  const iot = require('aws-iot-device-sdk');
  const { Buffer } = require('buffer');
  
  /*********************************************************
   * ENVIRONMENT VARIABLES
   * Make sure these are set in your environment, or change 
   * them to hardcode your region, endpoint, and secret name.
   *********************************************************/
  const AWS_DEFAULT_REGION = process.env.AWS_DEFAULT_REGION || 'us-east-1';
  const IOT_END_POINT = process.env.IOT_END_POINT || 'xxxxxxxxx-ats.iot.us-east-1.amazonaws.com';
  const SECRET_NAME = process.env.SECRET_NAME || 'iot/certs/prod';
  
  // We'll map device IDs to sensor types so that each device always uses the same sensor type.
  const deviceSensorMap = {};
  
  /*********************************************************
   * HELPER FUNCTIONS
   *********************************************************/
  function generateRandom(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }
  
  // Function to generate the sensor value based on the sensor type
  function generateSensorValue(sensorType) {
    let value;
    if (sensorType === "Temperature") {
        value = Math.random() * 110 - 10;
    } else {
        value = Math.random() * 100 + 1;
    }
    return parseFloat(value.toFixed(2)); // Convert to float after toFixed
}
  
  /*********************************************************
   * MAIN FUNCTION
   * 1. Retrieve certs from Secrets Manager
   * 2. Connect to IoT
   * 3. On 'connect', start sending messages
   *********************************************************/
  async function main() {
    try {
      // 1) Retrieve your certificates from Secrets Manager
      const secretsClient = new SecretsManagerClient({ region: AWS_DEFAULT_REGION });
      const response = await secretsClient.send(
        new GetSecretValueCommand({ SecretId:SECRET_NAME })
      );
  
      let secretString= response.SecretString;
  
      // Expecting a JSON structure like:
      // { "PrivateKey": "<base64>", "Cert": "<base64>", "AmazonRootCA": "<base64>" }
      const secretObj = JSON.parse(secretString);
  
  // Decode from base64 to raw PEM (string) or keep them as buffers
  const privateKeyDecoded = Buffer.from(secretObj.PrivateKey, "base64");
  const certDecoded = Buffer.from(secretObj.Cert, "base64");
  const caDecoded = Buffer.from(secretObj.AmazonRootCA, "base64");
  
  // Create an IoT device using in-memory certificate data
  const device = iot.device({
    privateKey: privateKeyDecoded,  // Pass the raw buffer or string
    clientCert: certDecoded,
    caCert: caDecoded,
    host: IOT_END_POINT,
    clientId: 'iOTestID',
    protocol: 'mqtts'
  });
      
  
      // 3) On 'connect', start publishing random messages
      device.on('connect', () => {
        console.log('Device connected to AWS IoT Core');
  
        // Send data every 4 seconds
        setInterval(() => {
          // Random device ID from 1 to 5
          const deviceId = `device_${generateRandom(1, 5)}`;
  
          // If this device hasn't appeared before, assign a random sensor type
          if (!deviceSensorMap[deviceId]) {
            // 50% chance for Pressure, 50% for Temperature
            deviceSensorMap[deviceId] = (Math.random() < 0.5 ? "Pressure" : "Temperature");
          }
  
          const sensorType = deviceSensorMap[deviceId];
          const value = generateSensorValue(sensorType); // Generate a value based on the sensor type
          const location = `Warehouse_${generateRandom(1, 3)}`; // e.g. Warehouse_1, _2, or _3
  
          // Build the payload
          const payload = {
            device_id: deviceId,
            sensor_type: sensorType,
            location,
            value
          };
  
          // Publish to the topic 'iot/sub'
          device.publish('iot/sub', JSON.stringify(payload));
          console.log('Message sent:', payload);
        }, 4000);
      });
  
      // Handle errors
      device.on('error', (error) => {
        console.error('Device Error:', error);
      });
  
      // If you want to see when the device disconnects
      device.on('close', () => {
        console.log('Connection closed');
      });
  
    } catch (error) {
      console.error('Error:', error);
    }
  }
  
  // Run the script
  main();