# -*- coding: utf-8 -*-
import os

from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage, ConfirmTemplate, MessageAction,
    CarouselTemplate,
    CarouselColumn,
    URIAction,
    PostbackAction
)

app = Flask(__name__)

configuration = Configuration(access_token=userdata.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(userdata.get('LINE_CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        action = event.message.text
        if action == 'confirm':
            reply = TemplateMessage(
                alt_text='confirm template',
                template = ConfirmTemplate(
                    text='Are you sure?',
                    actions=[
                        MessageAction(label='Yes',text='Yes'),
                        MessageAction(label='No',text='No')
                    ]
                )
            )
        elif action == 'carousel':
            carousei_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://www.printwand.com/blog/media/2012/01/ultimate-guide-to-your-product-launch.jpg',
                        title='商品 A',
                        text='這是商品 A 的描述，價格 $100。',
                        actions=[
                            URIAction(label='查看詳情', uri='https://www.printwand.com/blog/the-ultimate-guide-to-your-new-product-launch'),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i0.wp.com/www.gktoday.in/wp-content/uploads/2016/04/Product-in-Marketing.png?ssl=1',
                        title='商品 B',
                        text='這是商品 B 的描述，價格 $200。',
                        actions=[
                            URIAction(label='查看詳情', uri='http://gktoday.in/product-in-marketing-meaning-and-types/'),
                        ]
                    )

                ]
            )
            reply = TemplateMessage(
                alt_text='this is a carousel template',
                template=carousei_template
            )
        else:
            reply = TextMessage(text='Please type"confirm"')

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply]
            )
        )

if __name__ == "__main__":
    app.run()
