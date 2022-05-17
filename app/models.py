from django.contrib.auth.models import User
from django.db import models
import json


# Create your models here.
class Live(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户名')
    link = models.URLField('拉流地址', max_length=100)

    class Meta:
        verbose_name = '监控流'
        verbose_name_plural = '监控流'
        unique_together = (('user', 'link'))


class Log(models.Model):
    file_path = models.FileField('文件地址', max_length=100)
    created_time = models.DateTimeField('记录时间', auto_now_add=True)
    info = models.TextField('信息', max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户名')

    class Meta:
        verbose_name = '日志'
        verbose_name_plural = '日志'
        unique_together = (("user", "created_time"))


class Label(models.Model):
    label_index = models.IntegerField('标签索引', primary_key=True)
    label_info = models.CharField('标签信息', max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'


class Push(models.Model):
    flag = models.BooleanField('开关标识', default=True)
    corp_id = models.CharField('企业编号', max_length=100)
    agent_id = models.CharField('应用编号', max_length=100)
    corp_secret = models.CharField('应用密钥', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户名')

    class Meta:
        verbose_name = '企业微信推送'
        verbose_name_plural = '企业微信推送'
        unique_together = (('user', 'corp_id'))
