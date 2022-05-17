import base64
import json
import re

import numpy as np
import cv2
import requests
from django.contrib.auth.models import User
from django.core.mail import send_mail

from app.models import Push
from djangoProject import settings


def check(rep, str):
    res = re.search(rep, str)
    if res:
        return True
    else:
        return False


def base64ToImage(base64Code):
    img_data = base64.b64decode(base64Code)
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img


def send_qywx(send_msg, push, url):
    try:
        qywx_corpid = push.corp_id
        qywx_agentid = push.agent_id
        qywx_corpsecret = push.corp_secret
        qywx_touser = '@all'
        res = requests.get(
            f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={qywx_corpid}&corpsecret={qywx_corpsecret}"
        )
        token = res.json().get("access_token", False)
        data = {
            "touser": qywx_touser,
            "agentid": int(qywx_agentid),
            "msgtype": "textcard",
            "textcard": {
                "title": "绿色守护",
                "description": send_msg,
                "url": url,
            },
        }
        requests.post(url=f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
                      data=json.dumps(data))
        return True
    except:
        return False


def send_email(img_url=None, content=None, email=None):
    try:
        if img_url == None:
            html_content = test_html()
        else:
            html_content = push_html(img_url, content)
        print(html_content)
        send_mail(subject='绿色守护', message=None, from_email=settings.EMAIL_HOST_USER, html_message=html_content,
                  recipient_list=[email])
        return True
    except:
        return False


def push(img_url, content, userid):
    user = User.objects.filter(id=userid).first()
    if user is not None:
        email = user.email
        send_email(img_url=img_url, content=content, email=email)
        push = Push.objects.filter(user_id=userid).first()
        if push is not None and push.flag:
            send_qywx(content, push, f'http://127.0.0.1:8000/{userid}')


def push_html(img_url, content):
    html_content = f"""
    <div>
	<div align="center">
		<div class="open_email" style="margin-left: 8px; margin-top: 8px; margin-bottom: 8px; margin-right: 8px;">
			<div>
				<br>
				<span class="genEmailContent">
					<div id="cTMail-Wrap"
						 style="word-break: break-all;box-sizing:border-box;text-align:center;min-width:320px; max-width:660px; border:1px solid #f6f6f6; background-color:#f7f8fa; margin:auto; padding:20px 0 30px; font-family:'helvetica neue',PingFangSC-Light,arial,'hiragino sans gb','microsoft yahei ui','microsoft yahei',simsun,sans-serif">
						<div class="main-content" style="">
							<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse">
								<tbody>
								<tr style="font-weight:300">
									<td style="width:3%;max-width:30px;"></td>
									<td style="max-width:600px;text-align: center;">
									   
										<h1>Home Guard</h1>
										
										<p style="height:2px;background-color: #00a4ff;border: 0;font-size:0;padding:0;width:100%;margin-top:20px;"></p>

										<div id="cTMail-inner" style="background-color:#fff; padding:23px 0 20px;box-shadow: 0px 1px 1px 0px rgba(122, 55, 55, 0.2);text-align:left;">
											<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse;text-align:left;">
												<tbody>
												<tr style="font-weight:300">
													<td style="width:3.2%;max-width:30px;"></td>
													<td style="max-width:480px;text-align:left;">

														<h1 id="cTMail-title" style="font-size: 20px; line-height: 36px; margin: 0px 0px 22px;text-align: center;">
															绿色守护邮件通知
														</h1>

														<p id="cTMail-userName" style="font-size:14px;color:#333; line-height:24px; margin:0;">
															&ensp;&ensp;您有一条监控通知，请查看：
														</p>
														<br>
														<img style="text-align: center;max-width:480px" src="{img_url}">
														<p id="cTMail-userName" style="font-size:14px;color:#333; line-height:24px; margin:0;">
															详细内容：
														</p>
														<p id="cTMail-userName" style="font-size:14px;color:#333; line-height:24px; margin:0;">
															{content}
														</p>
														
														<p style="font-size: 14px; color: rgb(51, 51, 51); line-height: 24px; margin: 6px 0px 0px; word-wrap: break-word; word-break: break-all;">
															<a  href="http://127.0.0.1:8000" title=""
															   style="font-size: 16px; line-height: 45px; display: block; background-color: rgb(0, 164, 255); color: rgb(255, 255, 255); text-align: center; text-decoration: none; margin-top: 20px; border-radius: 3px;">
																进入官网
															</a>
														</p>
														<dl style="font-size: 14px; color: rgb(51, 51, 51); line-height: 18px; text-align: center;">
															<dd style="margin: 0px 0px 6px; padding: 0px; font-size: 12px; line-height: 22px;">
																<p  style="font-size: 14px; line-height: 26px; word-wrap: break-word; word-break: break-all; margin-top: 32px;">
																	from
																	<strong>Home Guard</strong>
																</p>
															</dd>
														</dl>
													</td>
													<td style="width:3.2%;max-width:30px;"></td>
												</tr>
												</tbody>
											</table>
										</div>

										<div id="cTMail-copy" style="text-align:center; font-size:12px; line-height:18px; color:#999">
											<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse">
												<tbody>
												<tr style="font-weight:300">
													<td style="width:3.2%;max-width:30px;"></td>
													<td style="max-width:540px;">

														<p style="text-align:center; margin:20px auto 14px auto;font-size:12px;color:#999;">
															此为系统邮件，请勿回复。
														</p>

													</td>
													<td style="width:3.2%;max-width:30px;"></td>
												</tr>
												</tbody>
											</table>
										</div>
									</td>
									<td style="width:3%;max-width:30px;"></td>
								</tr>
								</tbody>
							</table>
						</div>
					</div>
				</span>
			</div>
		</div>
	</div>
    </div>
    """
    return html_content


def test_html():
    html_content = """
    <div>
	<div align="center">
		<div class="open_email" style="margin-left: 8px; margin-top: 8px; margin-bottom: 8px; margin-right: 8px;">
			<div>
				<br>
				<span class="genEmailContent">
					<div id="cTMail-Wrap"
						 style="word-break: break-all;box-sizing:border-box;text-align:center;min-width:320px; max-width:660px; border:1px solid #f6f6f6; background-color:#f7f8fa; margin:auto; padding:20px 0 30px; font-family:'helvetica neue',PingFangSC-Light,arial,'hiragino sans gb','microsoft yahei ui','microsoft yahei',simsun,sans-serif">
						<div class="main-content" style="">
							<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse">
								<tbody>
								<tr style="font-weight:300">
									<td style="width:3%;max-width:30px;"></td>
									<td style="max-width:600px;text-align: center;">
									   
										<h1>Home Guard</h1>
										
										<p style="height:2px;background-color: #00a4ff;border: 0;font-size:0;padding:0;width:100%;margin-top:20px;"></p>

										<div id="cTMail-inner" style="background-color:#fff; padding:23px 0 20px;box-shadow: 0px 1px 1px 0px rgba(122, 55, 55, 0.2);text-align:left;">
											<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse;text-align:left;">
												<tbody>
												<tr style="font-weight:300">
													<td style="width:3.2%;max-width:30px;"></td>
													<td style="max-width:480px;text-align:left;">

														<h1 id="cTMail-title" style="font-size: 20px; line-height: 36px; margin: 0px 0px 22px;text-align: center;">
															绿色守护邮件通知
														</h1>

														<p id="cTMail-userName" style="font-size:14px;color:#333; line-height:24px; margin:0;">
															&ensp;&ensp;这是来自绿色守护的测试邮件。如已收到，则您的邮箱设置已生效。
														</p>
														<br>
														<p style="font-size: 14px; color: rgb(51, 51, 51); line-height: 24px; margin: 6px 0px 0px; word-wrap: break-word; word-break: break-all;">
															<a  href="http://127.0.0.1:8000" title=""
															   style="font-size: 16px; line-height: 45px; display: block; background-color: rgb(0, 164, 255); color: rgb(255, 255, 255); text-align: center; text-decoration: none; margin-top: 20px; border-radius: 3px;">
																进入官网
															</a>
														</p>
														<dl style="font-size: 14px; color: rgb(51, 51, 51); line-height: 18px; text-align: center;">
															<dd style="margin: 0px 0px 6px; padding: 0px; font-size: 12px; line-height: 22px;">
																<p  style="font-size: 14px; line-height: 26px; word-wrap: break-word; word-break: break-all; margin-top: 32px;">
																	from
																	<strong>Home Guard</strong>
																</p>
															</dd>
														</dl>
													</td>
													<td style="width:3.2%;max-width:30px;"></td>
												</tr>
												</tbody>
											</table>
										</div>

										<div id="cTMail-copy" style="text-align:center; font-size:12px; line-height:18px; color:#999">
											<table style="width:100%;font-weight:300;margin-bottom:10px;border-collapse:collapse">
												<tbody>
												<tr style="font-weight:300">
													<td style="width:3.2%;max-width:30px;"></td>
													<td style="max-width:540px;">

														<p style="text-align:center; margin:20px auto 14px auto;font-size:12px;color:#999;">
															此为系统邮件，请勿回复。
														</p>

													</td>
													<td style="width:3.2%;max-width:30px;"></td>
												</tr>
												</tbody>
											</table>
										</div>
									</td>
									<td style="width:3%;max-width:30px;"></td>
								</tr>
								</tbody>
							</table>
						</div>
					</div>
				</span>
			</div>
		</div>
	</div>
    </div>
    """
    return html_content