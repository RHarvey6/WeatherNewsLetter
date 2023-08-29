import requests
import re
import json
import csv
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def getLatLong(city, state):
    with open('./data/uscities.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if(row[0] == city):
                if(row[1] == state):
                    return (row[2],row[3])

def extractWeather(url):
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

def getAndWriteJsonForm(api_key): #Writes json file to local machine from API
    #form submission api get
    response = requests.get("https://formsubmit.co/api/get-submissions/" + api_key)

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

def deleteUnsubscribers():

    with open('./data/form_data.json', 'r') as openfile: #open written json file
        # Reading from json file
        json_object = json.load(openfile)
        json_data = json_object['submissions']

    reader_data = [] #GET ALL CURRENT USERS IN LOCAL CSV
    with open('./data/form_data.csv', 'r', newline='') as infile:
        reader = csv.reader(infile)
        for row in reader:
            reader_data.append(row) #Copy all users in the CSV to the reader_data to use later

    unsubs = []
    #GETUNSUBS
    for form in json_data: #GET ALL POTENTIAL NEW USERS FROM JSON
        form_data = form['form_data']
        form_date = form['submitted_at']
        if(form_data not in unsubs): #Duplicate protection from the form submissions
            try:
                type = form_data['type']
            except:
                type=''
                pass
            if(type =='unsubscribe'): #From the JSON, each unsubscription form.
                date = form_date['date'] #Date in Json unsubscribe submission
                isDupe = False
                for row in reader_data: #Read from current csv, looking for any new unsubs not yet in the CSV
                    if(row[0]=='unsubscribe'): #Only look at the already unsubscribed rows
                        if(row[1]==form_data['emailId'] and row[2]==form_date['date']):
                            isDupe = True
                if(isDupe == False):
                    form_data['date'] = date
                    unsubs.append(form_data)
    print(unsubs)

    with open('./data/form_data.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        write_rows = []
        for row in reader_data:
            isUnsub = False
            if(row[0]=='subscribe'):
                for unsub in unsubs:
                    if(row[1]==unsub['emailId'] and row[0]=='subscribe'): #If equal to the unsub email
                        isUnsub=True
                if(isUnsub==False): #If a normal subscriber
                    write_rows.append(row)
                else: #If unsubbed
                    row[0] = 'deleted'
                    write_rows.append(row)
            else:
                write_rows.append(row)
        for unsub in unsubs:
            writer.writerow(unsub.values())
        writer.writerows(write_rows)

def updateCsv(): #Adds any new users from the json not currently in the CSV 
    with open('./data/form_data.json', 'r') as openfile: #open written json file
        # Reading from json file
        json_object = json.load(openfile)
    json_data = json_object['submissions']

    user_info = []

    for form in json_data: #GET ALL POTENTIAL NEW USERS FROM JSON
        form_data = form['form_data']
        form_date = form['submitted_at']
        if(form_data not in user_info): #Duplicate protection from the form submissions
            try:
                type = form_data['type']
            except:
                type=''
                pass
            if(type =='subscribe'):
                form_data['date'] = form_date['date']
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
            for row in reader_data: #For each user already in the form_data CSV\
                if(row[0] == 'subscribe'):
                    csv_email = row[1]
                    try: 
                        email = user['emailId'] #Incase error
                    except:
                        email = ''
                        csv_email= ''
                        pass
                    if(csv_email==email and row[2]==user['state'] and row[3]==user['city']): #If a dupe
                        dupe = True
            if(dupe==False):
                writer.writerow(user.values())
            dupe=False

def getCsvData(): #Reads local csv form_data, returns all user subsriber info
    user_data = []
    with open('./data/form_data.csv', 'r', newline='') as outfile:
        reader = csv.reader(outfile)
        for row in reader:
            try:type = row[0]
            except:type = ''
            if(type == 'subscribe'):
                current_user = {} #Create a dict for each user, append to list of dicts user_data
                current_user['emailId'] = row[1]
                current_user['state'] = row[2]
                current_user['city'] = row[3]
                current_user['frequency'] = row[4]
                user_data.append(current_user)
    return user_data

def getApiKey():
    with open('./data/config.properties.txt', 'r') as f:
        lines = f.readlines()
        api_key = lines[5].strip()
    return api_key

def createUnsubscribeButton(email, city, state):
    0

def sendEmails(user_info):
    now = datetime.datetime.now()
    with open('./data/config.properties.txt', 'r') as f:
        lines = f.readlines()

        SERVER = lines[0].strip()
        IMAPSERVER = lines[1].strip()
        PORT = int(lines[2].strip())
        FROM = lines[3].strip()
        PASS = lines[4].strip()

    print("Initiating Server")

    server = smtplib.SMTP(SERVER, PORT)

    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(FROM, PASS)

    for user in user_info: #Loops through each user, creating and sending an email to each one
  

        city = user['city']
        state = user['state']
        TO = user['emailId']
        content = user['content']

        msg = MIMEMultipart()
        msg['From'] = FROM
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
        
        email = user['emailId']
        city = user['city']
        state = user['state']

        content = ''

        (lat, long) = getLatLong(city, state)
        url = 'https://forecast.weather.gov/MapClick.php?textField1=' + lat + '&textField2=' + long
        content  += extractWeather(url)

        #content+= createUnsubscribeButton(email, city, state)
        content += ('<br>------<br>')
        content +=('<br><br>End of Message')

        user['content'] = content #Append content to form_data
        user_info.append(user) #Append form_data to the list of all users data

    return user_info
