import requests
import re
import json
import csv
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

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

def writeFormJson(api_code): #Writes json file to local machine from API
    #form submission api get
    response = requests.get("https://formsubmit.co/api/get-submissions/" + api_code)

    json_dict = json.loads(response.text)

    json_data = json_dict['submissions']
    form_list = []
    form_data_list = []
    
    for form in json_data: #DUPLICATE PROTECTION
        form_data = form['form_data']
        if(form_data not in form_data_list):
            form_data_list.append(form_data)
            form_list.append(form)
    json_dict['submissions'] = form_list

    json_str = json.dumps(json_dict, indent=4) #Convert to string, then write
    with open("./data/form_data.json", "w") as outfile:
        outfile.write(json_str)

def updateCsv(): #Adds any new users from the json not currently in the CSV 
    with open('./data/form_data.json', 'r') as openfile: #open written json file
        # Reading from json file
        json_object = json.load(openfile)
    json_data = json_object['submissions']

    user_info = []

    for form in json_data: #GET ALL POTENTIAL NEW USERS FROM JSON
        form_data = form['form_data']
        if(form_data not in user_info): #Duplicate protection from the form submissions
            user_info.append(form_data)

    reader_data = [] #GET ALL CURRENT USERS IN LOCAL CSV
    with open('./data/form_data.csv', 'r', newline='') as outfile:
        reader = csv.reader(outfile)
        for row in reader:
            reader_data.append(row) #Copy all users in the CSV to the reader_data to use later

    with open('./data/form_data.csv', 'a', newline='') as outfile: #APPEND ALL NEW USERS TO CSV
        writer = csv.writer(outfile)
        dupe = False #DUPLICATE PROTECTION
        for user in user_info: #For each new user in the jsonForm
            for row in reader_data: #For each user already in the form_data CSV
                if(row[0]!=user['emailId'] or row[1]!=user['state'] or row[2]!=user['city']): #If not a dupe
                    continue
                else:
                    dupe = True
            if(dupe==False):
                writer.writerow(user.values())
            dupe=False

def getCsvData(): #Reads local csv form_data, returns all user info
    user_data = []
    with open('./data/form_data.csv', 'r', newline='') as outfile:
        reader = csv.reader(outfile)
        for row in reader:
            current_user = {}
            current_user['emailId'] = row[0]
            current_user['state'] = row[1]
            current_user['city'] = row[2]
            current_user['frequency'] = row[3]
            user_data.append(current_user)

    return user_data

def sendEmails(user_info):
    now = datetime.datetime.now()
    with open('./data/config.properties.txt', 'r') as f:
        lines = f.readlines()

        SERVER = lines[0].strip()
        IMAPSERVER = lines[1].strip()
        PORT = int(lines[2].strip())
        FROM = lines[3].strip()
        TO = lines[4].strip()
        PASS = lines[5].strip()

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

def attachContent(user_forms): #Creates all weather content for each email, attaches it to corresponding user
    print('composing emails...')


    user_info = [] #Will be a list of dicts of each users info, and the content to put into the email
 
    for user in user_forms: #For each form/submission in the json_file
        
        city = user['city']
        state = user['state']

        content = ''

        (lat, long) = get_lat_long(city, state)
        url = 'https://forecast.weather.gov/MapClick.php?textField1=' + lat + '&textField2=' + long
        cnt = extract_weather(url)

        content += cnt
        content += ('<br>------<br>')
        content +=('<br><br>End of Message')

        user['content'] = content #Append content to form_data
        user_info.append(user) #Append form_data to the list of all users data

    return user_info

#Update local JSON file with current form submission form
#with open('./data/config.properties.txt', 'r') as f:
#    lines = f.readlines()
#    api_code = lines[6].strip()
#writeFormJson(api_code)

#updateCsv()
#users = getCsvData()
#users_and_content = attachContent(users)

#sendEmails(users)
