from Weather import *

api_key = getApiKey()
#getAndWriteJsonForm(api_key)

updateCsv()
users = getCsvData()
users_and_content = attachContent(users)

#sendEmails(users_and_content)
