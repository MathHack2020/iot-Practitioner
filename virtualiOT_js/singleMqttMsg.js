const awsIot = require('aws-iot-device-sdk');
const AWS_DEFAULT_REGION =  'us-east-1';
const IOT_END_POINT =  'a3l9efh9x9pqsn-ats.iot.us-east-1.amazonaws.com' || process.env.IOT_END_POINT ;
const device = awsIot.device({
    keyPath: '../.certs/iotThingDemo.cert.pem',        // Path to your private key
    certPath:  '../.certs/iotThingDemo.private.key',             // Path to your certificate
    caPath: '../.certs/root-CA.crt',      // Path to AWS Root CA
    clientId: 'iOTestID',            // Device client ID
    host: `${IOT_END_POINT}`  // .iot.${region}.amazonaws.com`   AWS IoT endpoint
});

device.on('connect', function() {
    console.log('Connected to AWS IoT Core');
    // Publish random sensor data every 2 seconds

        const payload = JSON.stringify({
            
            temperature: (Math.random() * 10 + 20).toFixed(2), // Random temperature
            pressure: (Math.random() * 200 + 900).toFixed(2) ,  // Random pressure
            device_id: `device_${Math.floor(Math.random() * 5) + 1}`
        });
        device.publish('iot/sub', payload);  // Publish to the topic 'iot/sub'
        console.log('Message sent:', payload);

});

device.on('error', function(error) {
    console.error('Error:', error);
});