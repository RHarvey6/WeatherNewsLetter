import requests
import re

from bs4 import BeautifulSoup

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datetime

import csv

def get_lat_long(city, state):
    with open("./uscities.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if(row[0] == city):
                if(row[1] == state):
                    return (row[2],row[3])

def extract_weather(url):
    print('Extracting Weather')
    cnt = ''
    cnt +=('<b>Your weather for the week, at a glance.</b>\n'  + '<br>'
        + 'Retrieved from: '  + '<a href="' + url + '">' + 'forecast.weather.gov' + '</a>'
        +'<br>'+'-'*50+'<br>')
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content,'html.parser')
    
    for i,tag in enumerate(soup.find_all('li',attrs={'class':'forecast-tombstone'})): #For each tombstone
        has_hazard = False
        if('current-hazard' not in tag.attrs.get("class")): #NOT a hazard tombstone (Hazard is the first tombstone that appears when there is a hazard)
            period_name = tag.find('p',attrs={'class':'period-name'}).get_text(separator=" ")
            short_desc = tag.find('p',attrs={'class':'short-desc'}).get_text(separator=" ")
            high_low_temp = tag.find('p',attrs={'class':re.compile('temp')}).get_text(separator=" ")

            img = tag.find('img')
            imgsrc = img.get('src')
        
        
            cnt +=  ('<p class="forecast-summary">' + 
                    '<br>' + '<b>' + period_name+ '</b>' + "\n" + '<br>' +
                    '<img src = "https://forecast.weather.gov/' + imgsrc +  '">' + '<br>' +
                    short_desc + "\n"+ '<br>' +
                    high_low_temp + "\n" + '<br>' +
                    '</p>')
        else: #HAZARD
            hazard_name = tag.find('p',attrs={'class':'short-desc'}).get_text(separator=" ")
            hazard_text = tag.find('div',attrs={'class':'top-bar'}).find('div',attrs={'id':'headline-detail-now'}).get_text(separator=" ")
            if(has_hazard == False): #Ensures we only put one "Current Hazards"
                cnt += ('<div>' + 
                    '<p style="color:red; font-size:20px">' +
                    '<br>' + '<b>' + 'CURRENT HAZARDS:' + '</b>' + '<br>')
                has_hazard = True
            cnt += (hazard_name + '<br>' + 
                hazard_text + '<br>' + '</p>'
                '</div>')
    return(cnt)

def sendEmail(content):
    print('composing email...')
    #Email details
    with open('config.properties.txt', 'r') as f:
        SERVER = f.readline().strip()
        PORT = int(f.readline().strip())
        FROM = f.readline().strip()
        TO = f.readline().strip()
        PASS = f.readline().strip()

    msg = MIMEMultipart()

    msg['Subject'] = 'Weather for the Week [Automated Email]' + ' ' + city + ', ' + state + ', ' + str(now.month) + '-' + str(now.day) + '-' + str(now.year)
    msg['From'] = FROM
    msg['TO'] = TO
    #msg['To'] = ",".join(TO)

    msg.attach(MIMEText(content,'html'))

    print("Initiating Server")

    server = smtplib.SMTP(SERVER, PORT)

    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(FROM, PASS)
    server.sendmail(FROM, TO, msg.as_string())

    print('Email Sent...')

    server.quit()



    content = ''

now = datetime.datetime.now()

content = ''

city = 'Anchorage'
state = 'Alaska'

(lat, long) = get_lat_long(city, state)

url = 'https://forecast.weather.gov/MapClick.php?textField1=' + lat + '&textField2=' + long

cnt = extract_weather(url)



content += cnt
content += ('<br>------<br>')
content +=('<br><br>End of Message')

sendEmail(content)




