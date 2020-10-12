from flask import Flask, request, abort
import requests
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction

app = Flask(__name__)

line_bot_api = LineBotApi('your line access token')
handler = WebhookHandler('your secret number')

def monoNum(n):
    content = requests.get("https://invoice.etax.nat.gov.tw/invoice.xml")
    tree = ET.fromstring(content.text)
    items = tree[0].findall('item')
    title = items[n][0].text
    ptext = items[n][2].text
    ptext = ptext.replace('<p>','').replace('</p>','\n')
    return title + '月\n' + ptext[:-1]

def uniform_invoice(user_invoice):
    content = requests.get("https://invoice.etax.nat.gov.tw/invoice.xml")
    tree = ET.fromstring(content.text)
    items = tree[0].findall('item')
    ptext = items[0][2].text
    ptext = ptext.replace('<p>','').replace('</p>','')
    temlist = ptext.split('：')
    print(temlist)
    prizelist = []
    prizelist.append(temlist[1][5:8])
    prizelist.append(temlist[2][5:8])
    for i in range(3):
        prizelist.append(temlist[3][9*i+5:9*i+8])
    sixlist = temlist[4].split('、')
    for i in range(len(sixlist)):
        prizelist.append(sixlist[i])    
    if user_invoice in prizelist:
        return '符合某獎項後三碼，請自行核對發票前五碼!\n\n'+monoNum(0)
    else:
        return '很可惜，未中獎。請輸入下一張發票最後三碼。'
    

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):   
    mtext = event.message.text
    if mtext == "@快速選單":
        try:
            message = TextSendMessage(
                text = '請選擇你最喜歡的課程',
                quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(
                            action = MessageAction(label = "雲端運算與服務",text="雲端運算與服務")
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = "計算機圖學概論",text="計算機圖學概論")
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = "資訊講座",text="資訊講座")
                        ),
                        QuickReplyButton(
                            action = MessageAction(label = "電腦與網路安全概論",text="電腦與網路安全概論")
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif mtext == "@本期中獎號碼":
        try:
            message = TextSendMessage(text=monoNum(0))
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif mtext == "@前期中獎號碼":
        try:
            message = TextSendMessage(text=monoNum(0)+'\n\n'+monoNum(1))
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif mtext == "@輸入發票最後三碼":
        try:
            message = TextSendMessage(text="請輸入發票最後三碼進行對獎！")
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif len(mtext)==3 and mtext.isdigit():
        try:
            message = TextSendMessage(text=uniform_invoice(mtext))
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=mtext))
        
if __name__ == '__main__':
    app.run()