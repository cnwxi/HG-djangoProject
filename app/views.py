import json
import imageio as imageio
import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from pure_pagination import Paginator, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from app.models import Live, Log, Label, Push
from app.tools import base64ToImage, send_qywx, check, send_email, push


# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        print(username, password, email)

        user = User.objects.filter(username=username).first()

        rep = '^[A-Za-z0-9]{4,16}$'
        if check(rep, password):
            if user is not None:
                info = '用户名已存在'
                return render(request, 'register.html', {'info': info})
            else:
                rep = '^[A-Za-z0-9]{4,16}$'
                if check(rep, password):
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    info = '注册成功，请登录'
                    return render(request, 'register.html', {'info': info})
                else:
                    info = '密码格式错误'
                    return render(request, 'register.html', {'info': info})
        else:
            info = '用户名格式错误'
            return render(request, 'register.html', {'info': info})
    else:
        info = '请注册'
    return render(request, 'register.html', {'info': info})


@login_required()
def index(request, userid):
    return render(request, 'index.html', {'username': 'test', 'userid': userid})


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        rep1 = '^[A-Za-z0-9]{4,16}$'
        rep2 = '^[A-Za-z0-9]{6,16}$'
        if not check(rep1, username) or not check(rep2, password):
            info = '账户或密码格式错误'
            return render(request, 'signin.html', {'info': info})
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                print(user.id)
                return redirect('/' + str(user.id))
                # ''/', userid=user.id)
            else:
                info = '你的账户没有激活，请联系管理员'
                return render(request, 'signin.html', {'info': info})
        else:
            info = '账户或密码错误'
        return render(request, 'signin.html', {'info': info})
    else:
        info = '请登录'
        return render(request, 'signin.html', {'info': info})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # 验证登录，正确则authenticate()返回一个User对象，错误则返回一个None类
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)  # 登录用户
                print(username, user.id)
                return redirect('/', {'username': username, 'userid': user.id})
            else:
                not_active_info = '你的账户没有激活，请联系管理员'
                return render(request, 'login.html', {'NOT_ACTIVE': not_active_info})
        else:
            error_info = 'Typing Error'
            return render(request, 'login.html', {'ERROR': error_info})

    else:
        login_info = 'Login System'
        return render(request, 'login.html', {'LOGIN': login_info})


@login_required()
def logout(request):
    auth.logout(request)
    return redirect('/login')


@login_required()
def live(request, userid):
    mylive = Live.objects.filter(user_id=userid).first()
    if mylive is None:
        link = None
        info = '尚未设置监控地址，请到设置页面添加'
    else:
        link = mylive.link
        print(link)
        info = f'当前监控地址为：{link}'
    return render(request, 'mylive.html', {'link': link, 'userid': userid, 'info': info})


@login_required()
def log(request, userid):
    log_list = Log.objects.filter(user_id=userid).order_by('-created_time')
    if log_list is not None:
        paginator = Paginator(log_list, 5, request=request)
        try:
            page_num = request.GET.get('page', 1)
        except PageNotAnInteger:
            page_num = 1
        page_obj = paginator.page(page_num)
        info = None
    else:
        info = '暂无日志'
    return render(request, 'log.html', {'page_obj': page_obj, 'userid': userid, 'info': info})


@login_required()
def setting(request, userid):
    print(userid)
    live = Live.objects.filter(user_id=userid).first()
    user = User.objects.filter(id=userid).first()
    push = Push.objects.filter(user_id=userid).first()
    data = {
        'userid': userid,
        'live': live,
        'push': push,
        'user': user
    }
    return render(request, 'setting.html', data)


@csrf_exempt
def post_case(request):
    if request.method == 'POST':
        print('POST request')
        # 拿到记录帧和预测标签
        received_data = json.loads(request.body)
        # print(type(received_data))
        # 将记录帧转gif存储
        frames = []
        for i in received_data['data']:
            frames.append(base64ToImage(i))
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = f'./static/log/{nowTime}.gif'
        imageio.mimsave(file_name, frames, 'gif', duration=0.1)
        # 获取标签索引对应的标签内容
        info = []
        for i in received_data['label']:
            info.append(Label.objects.get(label_index=i).label_info)
        info_detail = ' '.join(info)
        # 将文件路径写入数据库
        userid = received_data['userid']
        log = Log(user_id=userid, info=info_detail, file_path=file_name[1:])
        log.save()
        # 推送信息
        img_url = 'http://127.0.0.1:8000' + file_name[1:]
        content = f'{nowTime}\n预测出目标动作：{info_detail}，请核实。'
        push(img_url=img_url, content=content, userid=userid)
        # 返回信息
        data = {
            'success': True
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'success': False}), content_type='application/json')


@csrf_exempt
def get_link(request):
    if request.method == 'GET':
        print('GET request')
        received_data = json.loads(request.body)
        username = received_data['username']
        password = received_data['password']
        user = auth.authenticate(username=username, password=password)
        data = {'success': False, 'data': []}
        if user is not None:
            if user.is_superuser:
                live_list = Live.objects.all()
                for i in live_list:
                    data['success'] = True
                    data['data'].append([i.user_id, i.link])
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'success': False}), content_type='application/json')


@csrf_exempt
def check_link(request):
    if request.method == 'GET':
        received_data = json.loads(request.body)
        userid = received_data['userid']
        live = Live.objects.filter(user_id=userid).first()
        data = {}
        if live:
            data['success'] = True
            data['link'] = live.link
        else:
            data['success'] = True
            data['link'] = ''
        return HttpResponse(json.dumps(data), content_type='application/json')


@login_required()
def data(request):
    with open('./static/label.json', 'r', encoding='utf-8') as f:
        label = json.load(f)
        f.close()

    for i in label:
        index = int(i)
        info = label[i]
        print(info)
        log = Label(label_index=index, label_info=info)
        log.save()

    return HttpResponse('success')


@login_required()
def change_link(request, userid):
    if request.method == 'POST':
        link = request.POST.get('link')
        data = {'msg': ''}
        re = '^(?:(http|https|ftp):\/\/)?((?:[\w-]+\.)+[a-z0-9]+)((?:\/[^/?#]*)+)?(\?[^#]+)?(#.+)?$'
        if check(re, link):
            live = Live.objects.filter(user_id=userid).first()
            if live is not None:
                if live.link != link:
                    live.link = link
                    live.save()
                    data['msg'] = '后端信息：监控地址修改成功'
                else:
                    data['msg'] = '后端信息：新地址和旧地址一致，不需要修改'
            else:
                live = Live(user_id=userid, link=link)
                live.save()
                data['msg'] = '后端信息：新建监控地址'
        else:
            data['msg'] = '后端信息：地址格式错误'
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': '错误请求'})


@login_required()
def change_push(request, userid):
    if request.method == 'POST':
        corp_id = request.POST.get('corp_id')
        agent_id = request.POST.get('agent_id')
        corp_secret = request.POST.get('corp_secret')
        data = {'msg': ''}
        if len(corp_id) == 0 or len(agent_id) == 0 or len(corp_secret) == 0:
            data['msg'] = '后端信息：请输入完整配置'
        else:
            push = Push.objects.filter(user_id=userid).first()
            if push is not None:
                if corp_id == push.corp_id and agent_id == push.agent_id and corp_secret == push.corp_secret:
                    data['msg'] = '后端信息：新配置与旧配置一致，不需要更改'
                else:
                    push.corp_id = corp_id
                    push.agent_id = agent_id
                    push.corp_secret = corp_secret
                    push.save()
                    data['msg'] = '后端信息：配置修改成功'
            else:
                push = Push(user_id=userid, corp_id=corp_id, agent_id=agent_id, corp_secret=corp_secret)
                push.save()
                data['msg'] = '后端信息：新建配置'
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': '错误请求'})


@login_required()
def on_off_push(request, userid):
    if request.method == "GET":
        data = {'msg': ''}
        push = Push.objects.filter(user_id=userid).first()
        if push is not None:
            push.flag = not push.flag
            push.save()
            data['msg'] = '后端信息，修改成功'
            data['flag'] = push.flag
            return JsonResponse(data)
    else:
        return JsonResponse({'msg': '错误请求'})


@login_required()
def change_email(request, userid):
    if request.method == 'POST':
        email = str(request.POST.get('email'))
        print(email)
        data = {'msg': '', 'email': email}
        re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        if check(re, email):
            user = User.objects.get(id=userid)
            if email == user.email:
                data['msg'] = '后端信息：新邮箱和旧邮箱一致，修改失败'
            else:
                if user is not None:
                    user.email = email
                    user.save()
                    data['msg'] = '后端信息：邮箱修改成功'
        else:
            data['msg'] = '后端信息：邮箱格式错误'
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': '错误请求'})


@login_required()
def change_password(request, userid):
    if request.method == 'POST':
        old_pw = request.POST.get('old_pw')
        new_pw = request.POST.get('new_pw')
        re = '^[A-Za-z0-9]{6,16}$'
        data = {'msg': ''}
        if not check(re, old_pw) or not check(re, new_pw):
            data['msg'] = '后端信息：密码格式不正确'
        else:
            user = User.objects.get(id=userid)
            if user is not None:
                if user.check_password(old_pw):
                    if old_pw != new_pw:
                        user.set_password(new_pw)
                        user.save()
                        data['msg'] = '后端信息：密码修改成功'
                    else:
                        data['msg'] = '后端信息：新密码与旧密码一致'
                else:
                    data['msg'] = '后端信息：旧密码不正确'
            else:
                data['msg'] = '后端信息：当前用户不存在'
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': '错误请求'})


@login_required()
def check_push(request, userid):
    if request.method == 'GET':
        data = {}
        user = User.objects.filter(id=userid).first()
        if user is None:
            data['msg'] = '用户不存在'
            return JsonResponse(data)
        email = user.email
        send_msg = '推送测试，如果您收到了此信息说明您的推送设置已生效'
        msg = ''
        if send_email(email=email):
            msg += '邮件发送成功\n'
        else:
            msg += '邮件设置有误，请检查\n'
        push = Push.objects.filter(user_id=userid).first()
        if push is not None:
            if send_qywx(send_msg, push, f'http://127.0.0.1:8000/{userid}'):
                msg += '企业微信推送成功\n'
            else:
                msg += '企业微信推送配置有误，请检查\n'
        else:
            msg += '企业微信未配置\n'
        return JsonResponse({'msg': msg})
    else:
        return JsonResponse({'msg': '错误请求'})


def test(request):
    user = Live.objects.filter(id=2)
    json_data = serializers.serialize('json', user)
    # json_data = user.toJson()
    print(json_data)
    return HttpResponse(json_data)
