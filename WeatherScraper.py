import requests
import re

from bs4 import BeautifulSoup

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datetime

now = datetime.datetime.now()

content = ''

#url = "https://forecast.weather.gov/MapClick.php?CityName=White+Bear+Lake&state=MN&site=MPX&textField1=45.0677&textField2=-93.0127&e=0"
url = "https://forecast.weather.gov/MapClick.php?CityName=Owatonna&state=MN&site=MPX&textField1=44.0852&textField2=-93.2243&e=0"

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
    f = open('config.properties.txt', 'r')
    SERVER = f.readline().strip()
    PORT = int(f.readline().strip())
    FROM = f.readline().strip()
    TO = f.readline().strip()
    PASS = f.readline().strip()
    f.close()

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



cnt = extract_weather(url)

city = re.search('CityName=[^&]+', url)
city = city.string[city.start()+9:city.end()].replace('+', ' ') #If the city name is multiple words, the url will have +, so this replaces that
state = re.search('state=[^&]+', url)
state = state.string[state.start()+6:state.end()]


content += cnt
content += ('<br>------<br>')
content +=('<br><br>End of Message')

sendEmail(content)




