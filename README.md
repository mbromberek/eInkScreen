<div id="top"></div>


<h3 align="center">eInk Smart Display</h3>

  <p align="center">
    Shows the current date, current weather, the next few events in your calendar, and running statistics.
    The original code and most of this README is from <a href="https://github.com/13Bytes/eInkCalendar">eInkCalendar</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#components">Components</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#frame">Frame</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
The finished project on my counter:

<img src="https://github.com/mbromberek/eInkScreen/blob/main/pictures/SmartScreen.jpeg" height=500>
<!--<img src="https://user-images.githubusercontent.com/12069002/150647924-80f5f8fa-098a-4592-b257-7ac27326abfb.jpg" height=500>-->

<p align="right">(<a href="#top">back to top</a>)</p>



### Components
This repo includes the software (100% python) and the STLs of the frame.

I used the following hardware:

* [Waveshare 800×480, 7.5inch E-Ink display (13505)](https://www.waveshare.com/product/displays/7.5inch-e-paper-hat-b.htm)
* [Raspberry Pi 3b](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/)
* Case was 3D printed, details are <a href="#frame">below</a>
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
The prerequisites are based on [this](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)) waveshare instruction to get your rapi ready for the display:

* Enable the SPI interface on your raspi
  ```sh
  sudo raspi-config
  # Choose Interfacing Options -> SPI -> Yes  to enable SPI interface
  ```
* Install BCM2835 libraries
  ```sh
  wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
  tar zxvf bcm2835-1.60.tar.gz 
  cd bcm2835-1.60/
  sudo ./configure
  sudo make
  sudo make check
  sudo make install
  ```
* Install wiringPi libraries
  ```sh
  sudo apt-get install wiringpi
  
  #For Pi 4, you need to update it：
  cd /tmp
  wget https://project-downloads.drogon.net/wiringpi-latest.deb
  sudo dpkg -i wiringpi-latest.deb
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/mbromberek/eInkScreen
   cd eInkScreen
   ```
2. Install requirements
   ```sh
   sudo apt-get update
   # requirements by waveshare
   sudo apt-get install python3-pip python3-pil python3-numpy RPi.GPIO python-spidev
   # requirements by this repo
   sudo python3 -m pip install -r requirements.txt
   ```
3. Create config-file
   ```sh
   cp settings.py.sample settings.py
   ```
   Now edit `settings.py` and set all your settings:

   `LOCALE: "en_US"` (or e.g. `en-GB.UTF-8`) Select your desired format and language. It needs to be installed on your device (which 95% of time is already the case - as it's you system-language. If not, take a look at the [Debian Wiki](https://wiki.debian.org/Locale))
   
   `WEBDAV_CALENDAR_URL = "webcal://p32-caldav.icloud.com/published/2/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"` The address of your shared wabdav calendar. (It needs to be publicly accessible by this URL)
   
   `WEBDAV_IS_APPLE = True` Is the calendar hosted on icloud?
   
   `WEATHER_BASE_URL = 'https://weatherkit.apple.com/api/v1/weather'` The address for getting weather from Apple WeatherKit.

   `WEATHER_KEY = 'XXXXXXXXXXXX'` Bearer token for WeatherKit.

   `LATITUDE = '40.60189'` Latitude Coordinate for getting current weather.
   
   `LONGITUDE = '-74.06026'` Longitude Coordinate for getting current weather.
   
   `LANGUAGE = 'en_US'` Language for results to be returned.
   
   `ROTATE_IMAGE = True` This will rotate the image 180° before printing it to the calendar. `True` is required if you use my STL, as the dipay is mounted upside-down.


4. Add the start-script to your boot-process:\
   (You might need to adapt the path `/home/pi/eInkScreen/run_screen.sh` acordingly)

   Make `run_screen.sh` executable
   ```sh
   chmod +x /home/pi/eInkScreen/run_screen.sh
   ``` 
   and add it to crontab, as follows:
   ```sh
   crontab -e
   ```
   and add following line:\
   ```@reboot sleep 60 && /home/pi/eInkScreen/run_screen.sh```\

<p align="right">(<a href="#top">back to top</a>)</p>



## Frame

The STLs of the frame can be found in [hardware](https://github.com/mbromberek/eInkScreen/tree/main/hardware).

Details about 3D printed Frame can be found on the original [project's site](https://github.com/13Bytes/eInkCalendar)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact
* Mike Bromberek
* Email [mikebromberek@gmail.com](mikebromberek@gmail.com)
* Mastodon [@mikebromberek@twit.social](https://twit.social/@mikebromberek)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
* I got the idea from Jason Snell <a href="https://sixcolors.com/post/2022/09/a-smart-e-ink-calendar-comes-to-my-kitchen/">A smart E Ink calendar comes to my kitchen</a>
* The start of the code and the details for 3D printing the frame are from Louis - [@Louis_D_](https://twitter.com/Louis_D_) - coding@13bytes.de. Original code is <a href="https://github.com/13Bytes/eInkCalendar">eInkCalendar</a>

<p align="right">(<a href="#top">back to top</a>)</p>
