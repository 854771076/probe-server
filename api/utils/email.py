
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
def send_Email(title,messages:list,emails:list,user:list):
	# 构建邮件内容
	email_from = f'Probe资讯平台 <{settings.DEFAULT_FROM_EMAIL}>'  # 发件人邮箱
	template_name = 'email.html'  # 模板文件路径
	for index,email in enumerate(emails) :
		context = {'title': title,'message':messages[index],'email':email,'user':user}
		html_message = render_to_string(template_name, context)
		send_mail(subject=title,message=messages[index], from_email=email_from, recipient_list=[email], html_message=html_message)