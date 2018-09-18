# load LineChatBot key
line_key=json.load(open("./requirements/line_key", 'r'))
CHANNEL_ACCESS_TOKEN = line_key.get("Channel_access_token")
CHANNEL_SECRET = line_key.get("Channel_secret")
MY_USER_ID = line_key.get("My_user_ID")
RICH_MENU_ID = line_key.get("Rich_menu_ID")

# 1. Prepare a rich menu image

# 2. Create a rich menu
# 2-1. Create a rich menu objec: 把做好的myJsonRichMenu另外存放成檔案
menuJson = json.load(open("./requirements/rich_menu", 'r'))
# 2-2. Send an HTTP POST request to the '/v2/bot/richmenu' endpoint
createMenuEndpoint = 'https://api.line.me/v2/bot/richmenu' # 設定 request address
createMenuRequestHeader={'Content-Type':'application/json','Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
lineCreateMenuResponse = requests.post(createMenuEndpoint,headers=createMenuRequestHeader,data=json.dumps(menuJson)) # get RichMenuId from response
uploadRichMenuId=json.loads(lineCreateMenuResponse.text).get("richMenuId")

# 3. Upload the rich image
uploadMenuEndpoint='https://api.line.me/v2/bot/richmenu/%s/content' % RICH_MENU_ID # 設定 request address
uploadMenuRequestHeader={'Content-Type':'image/png','Content-Length': '348', 'Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
uploadImageFile=open("./static/rich_menu.png",'rb') # 設定上傳圖片
lineUploadMenuResponse=requests.post(uploadMenuEndpoint,headers=uploadMenuRequestHeader,data=uploadImageFile) # response an array of rich menu response objects

# 4. Link the rich image to individual user
linkMenuEndpoint='https://api.line.me/v2/bot/user/%s/richmenu/%s' % (MY_USER_ID, uploadRichMenuId) # 設定 request address
linkMenuRequestHeader={'Content-Type':'image/png','Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
lineLinkMenuResponse=requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader) # Link Response empty JSON

# get RichMenu Image
getRichMenuImageEndpoint = 'https://api.line.me/v2/bot/richmenu/%s/content' % '179f7e16d4d627de7fd1c50bf92cffaa'
getRichMenuImageHeader = {'Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN}
getRichMenuImageResponse=requests.get(getRichMenuImageEndpoint,headers=getRichMenuImageHeader)
