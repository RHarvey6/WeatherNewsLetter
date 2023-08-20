import requests
import re
import json

from bs4 import BeautifulSoup

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datetime

import csv

def get_lat_long(city, state):
    with open('./data/uscities.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if(row[0] == city):
                if(row[1] == state):
                    return (row[2],row[3])

def extract_weather(url):
    print('Extracting Weather')
    cnt = ''
    
    cnt+= ('<head> <style>' +
           'p {color: blue;}'
           '</style></head>')
    
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

def writeFormJson(api_code): #Writes json file to local machine
    #form submission api get
    response = requests.get("https://formsubmit.co/api/get-submissions/" + api_code)

    json_dict = json.loads(response.text)
    json_str = json.dumps(json_dict, indent=4)

    def writeJson(file): #write the file
        with open("./data/form_data.json", "w") as outfile:
            outfile.write(file)
    writeJson(json_str)

def getFormData(): #Reads local json file, returns 
    with open('./data/form_data.json', 'r') as openfile: #open written json file
        # Reading from json file
        json_object = json.load(openfile)
    json_data = json_object['submissions']
    return json_data

def sendEmails(user_info):
    now = datetime.datetime.now()
    with open('./data/config.properties.txt', 'r') as f:

        SERVER = f.readline().strip()
        IMAPSERVER = f.readline().strip()
        PORT = int(f.readline().strip())
        FROM = f.readline().strip()
        TO = f.readline().strip()
        PASS = f.readline().strip()

    msg = MIMEMultipart()
    msg['From'] = FROM


    print("Initiating Server")

    server = smtplib.SMTP(SERVER, PORT)

    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(FROM, PASS)

    for user in user_info: #Loops through each user, sending an email to each one
        city = user['city']
        state = user['state']
        TO = user['emailId']
        content = user['content']

        msg['Subject'] = 'Weather for the Week [Automated Email]' + ' ' + city + ', ' + state + ', ' + str(now.month) + '-' + str(now.day) + '-' + str(now.year)
        msg['TO'] = TO
        msg.attach(MIMEText(content,'html'))
        server.sendmail(FROM, TO, msg.as_string()) #SEND THE EMAIL
        print('Email Sent...')

    server.quit()

def initEmail(): #Creates all content for each email, as well as the user info to send emails out to corresponding user
    print('composing emails...')

    #Email details

    #TODO Call writeFormJson w/ api_code in config.properties

    user_forms = getFormData()
    user_info = [] #Will be a list of dicts of each users info, and the content to put into the email
 
    for form in user_forms: #For each form/submission in the json_file
        form_data = form['form_data']
        
        city = form_data['city']
        state = form_data['state']
        '''
        try: TO = form_data['emailId']
        except KeyError:
            pass
        try: frequency = form_data['frequency']
        except KeyError:
            pass
        '''
    
        content = ''

        (lat, long) = get_lat_long(city, state)
        url = 'https://forecast.weather.gov/MapClick.php?textField1=' + lat + '&textField2=' + long
        cnt = extract_weather(url)

        content += cnt
        content += ('<br>------<br>')
        content +=('<br><br>End of Message')

        form_data['content'] = content #Append content to form_data
        user_info.append(form_data) #Append form_data to the list of all users data

    return user_info


users = initEmail()
#sendEmails(users)

