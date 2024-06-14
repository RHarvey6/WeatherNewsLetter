from Weather import *

api_key = getApiKey()
getAndWriteJsonForm(api_key)

updateCsv()
deleteUnsubscribers()

users = getCsvData()
print(users)
users_and_content = attachContent(users)

print(users_and_content)
sendEmails(users_and_content)

