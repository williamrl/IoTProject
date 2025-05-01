# IoTProject

Hello! This is our project for the CMPSC 487W course at Penn State Abington. Pitched by Mr. Joseph Oakes, this project is an Smart Home IoT Project focused around managing simulated devices. The main features in this project are the ability to connect to a smart home monitoring system using a publish-subscribe model. Each virtual device will be able to subscribe to the smart home hub the user is accessing, where the hub essentially acts as a message broker, or a manual queue which contains messages describing actions the user wants a smart home device to do. Example actions can include changing the temperature on a thermostat or turning off a light. Each device can also communicate to the smart home hub to display information such as the current temperature in the home, or what smart lights are on. Each user's smart home hub will be different, which will only display the smart home devices throughout your home, ensuring your smart home data is private. To ensure security with user data, sensitive data such as user and device data is encrypted using AES encryption. Users will log into their smart home hubs using their account username and password, which will decrypt all data, giving the user a key which will be used to verify the user is who they claim when accessing or modifying different device information. Data integrity is ensured by using HMAC. HMAC works by hashing the previous key along with the message information. The raw message information is also sent, where the server can rehash the key and message to ensure the signatures match. All important data such as user credentials, settings about different devices, or logs are all stored in a MySQL database. The database is password protected to ensure user data is safe and secure. 

## Installation Guide
1. Download and setup all of the following:
   - https://dev.mysql.com/downloads/mysql/
   - https://www.mysql.com/products/workbench/
   - https://www.rabbitmq.com/tutorials/tutorial-one-python
2. In the MySQL Workbench in a local instance, input the following SQL commands:

```CREATE USER 'SmartHome'@'localhost' IDENTIFIED BY 'SmartHomePassword';```
   
```GRANT ALL PRIVILEGES ON *.* TO 'SmartHome'@'localhost' WITH GRANT OPTION;```
   
4. Install the libraries in the requirements.txt using pip, or some other cmdlet. 
5. Download the project from the GitHub. Ensure that the terminal is in a location where the Command Prompt can access.
## Use Guide
1. Run the Main file.
2. Ctrl Click on the IP Address that is outputted in the log.
3. To run a Simulated Device, you must use a seperate terminal. Go to the Devices folder, choose a device, and run the 'simulated_device.py' file in a seperate terminal. If using Visual Code Studio, this can be done by clicking on the drop arrow next to the Run Program button.
## Known Issues
- Currently, the only way to un-link a Simulated Device from a user is to delete the 'user.session' file from the designated folder.
