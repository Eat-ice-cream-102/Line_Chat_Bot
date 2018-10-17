
# Build My Environment
## Ubuntu 16.04 update and timeset
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt-get update
$ sudo apt install curl
$ sudo timedatectl set-timezone "Asia/Taipei"
```
## Install Docker
```
$ curl -fsSL get.docker.com | sh
$ sudo usermod -aG docker your-user
$ sudo systemctl enable docker
```
### Re-login to use docker commend directly 
```
$ docker build -t="eaticecream/linechatbot" .
$ docker run --name line-chat-bot-jupyter --link some-mysql -p 8888:8888 -p 5000:5000 -v $(pwd):/home/jovyan/work -d eaticecream/linechatbot start-notebook.sh --NotebookApp.token=''
$ docker run --name line-ngrok -d -p 4040 --link line-chat-bot-jupyter wernight/ngrok ngrok http line-chat-bot-jupyter:5000
$ curl $(docker port line-ngrok 4040)/api/tunnels > tunnels.json
```
## Install git
> sudo apt install git

# Flask structor
```
+-------------------------------------------
---README.md
+--manage.py
+--config.py
+--app.py
+--(requirements)+--line_key
|                +--mysql_key
|                +--lineTest_sample.sql
+--(static)+--(image)+--rich_menu.png
|          +--(richmenu)+--rich_menu
+-------------------------------------------
```
# RichMenu Setting
## load LineChatBot key
```
line_key=json.load(open("./requirements/line_key", 'r'))
CHANNEL_ACCESS_TOKEN = line_key.get("Channel_access_token")
CHANNEL_SECRET = line_key.get("Channel_secret")
MY_USER_ID = line_key.get("My_user_ID")
RICH_MENU_ID = line_key.get("Rich_menu_ID")
```
## 1. Prepare a rich menu image

## 2. Create a rich menu
### 2-1. Create a rich menu objec: 把做好的myJsonRichMenu另外存放成檔案
```
menuJson = json.load(open("./static/richmenu/rich_menu", 'r'))
```
### 2-2. Send an HTTP POST request to the '/v2/bot/richmenu' endpoint
```
createMenuEndpoint = 'https://api.line.me/v2/bot/richmenu' # 設定 request address
createMenuRequestHeader={'Content-Type':'application/json','Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
lineCreateMenuResponse = requests.post(createMenuEndpoint,headers=createMenuRequestHeader,data=json.dumps(menuJson)) # get RichMenuId from response
uploadRichMenuId=json.loads(lineCreateMenuResponse.text).get("richMenuId")
```
## 3. Upload the rich image
```
uploadMenuEndpoint='https://api.line.me/v2/bot/richmenu/%s/content' % RICH_MENU_ID # 設定 request address
uploadMenuRequestHeader={'Content-Type':'image/png','Content-Length': '348', 'Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
uploadImageFile=open("./static/image/rich_menu.png",'rb') # 設定上傳圖片
lineUploadMenuResponse=requests.post(uploadMenuEndpoint,headers=uploadMenuRequestHeader,data=uploadImageFile) # response an array of rich menu response objects
```
## 4. Link the rich image to individual user
```
linkMenuEndpoint='https://api.line.me/v2/bot/user/%s/richmenu/%s' % (MY_USER_ID, uploadRichMenuId) # 設定 request address
linkMenuRequestHeader={'Content-Type':'image/png','Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
lineLinkMenuResponse=requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader) # Link Response empty JSON
```
## get RichMenu Image
```
getRichMenuImageEndpoint = 'https://api.line.me/v2/bot/richmenu/%s/content' % RICH_MENU_ID
getRichMenuImageHeader = {'Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN}
getRichMenuImageResponse=requests.get(getRichMenuImageEndpoint,headers=getRichMenuImageHeader)
```

## To Be Conttinued ########
1. Actually I left running python code and ngrok on the docker aside, no have enough time to try if it is workable, only learned the method from my teacher, LBH, first. if you are interested in knowing how to make it, maybe you can refer our forked reposity.
2. the muti-process method seems not work very well when line-chat-bot pushes messages to followers, it would cause duplicate-sending issue. Have not tried yet, but setting a trigger/listener on the DB/ORM may be the solution to it.
3. The flask structure and python code still has much to be refined to be more readable and formal.
