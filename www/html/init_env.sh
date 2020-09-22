sudo apt-get update
sudo apt-get install -y python3
sudo apt-get install -y apache2
sudo apt-get install -y sqlite3
sudo apt-get install -y sqlite
sudo apt-get install -y sqlitebrowser
sudo apt-get install -y php libapache2-mod-php
sudo apt-get install -y php7.0-sqlite

sudo cp -R www/ /var
cd /var/www
sudo chmod -R 777 db/
cd html/
sudo mkdir trace
sudo chmod -R 777 trace/

sudo a2enmod cgi
sudo service apache2 restart
