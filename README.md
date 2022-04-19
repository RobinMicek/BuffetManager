# **Buffet Manager**
* **Easy-to-use Open-Source POS / Buffet Manager system**
* Based on **Python 3** & **Flask** & **FastAPI** & **MySQL**



## Fuctions
* Support for multiple accounts / kiosk   
* Statistics and Charts 
* Dashboard login via Google Authenticator


## Parts
* **Core** - Handles all the logic
  * Default port - 8181
* **Dashboard** - Admin panel for setting up and managing your kiosks
  * Default port - 8000
* **Client** - POS / Kiosk
  * Default port - 8010


# **How to run**

### **Requirements** 
  * MySQL
  * Python 3

## **Setup**
* Create enviroment variables: \
  **API_URL** - *Core* url (default is [`https://local-server-ip:8181`]())
  \
  **DB_HOST** - MySQL Host url
  \
  **DB_USER** - MySQL Username
  \
  **DB_PASSWORD**  - MySQL Password
* Create *'buffetdb'* database on the MySQL server

## **Run**
Requirements.txt install needs to be done for each part separately (*core*, *dashboard*, *client*)
* Go into part's folder
* Install required Python libraries
  ```sh
  pip3 install -r requirements.txt
  ```





* Start the **CORE** server 
  ```sh
  uvicorn app:app --host 0.0.0.0. --port 8181 
  ```

* Start the **DASHBOARD** server 
  ```sh
  gunicorn --bind 0.0.0.0.:8000 app:app
  ```

* Start the **CLIENT** server 
  ```sh
  gunicorn --bind 0.0.0.0.:8010 app:app
  ```

If you are setting this up on a linux Linux server using ssh you may wanna use something like a *Screen* 

**Gunicorn only works on UNIX systems (Linux/Mac)** \
If you are trying to run this app on Windows, look for a different solution on \
how to run WSGI app (e.g. mod_wsgi) 




## **After your Buffet Manager is running**
*Dashboard* can be accessed on [`https://local-server-ip:8000`]() \
You will be prompted to do **default setup**
\
\
POS / Kiosk  can be accessed on [`https://local-server-ip:8010`]()

\
\
**For developers** - *Core* API documentation can be accesed [`https://local-server-ip:8181/docs`]() for **Swagger UI** or [`https://local-server-ip:8181/redoc`]() for **ReDoc** 


## **ToDo**
* Dockerization - Ability to run all three parts in Docker (easier for user setup)



made with ♥ by Robin Míček 
