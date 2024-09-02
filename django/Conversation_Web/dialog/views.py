import os
import random
from django.shortcuts import render
from datetime import datetime
from dialog.models import personality

def select_persona(request):
   total_number = 15
   all_num = [i for i in range(total_number)]
   all_num = random.sample(all_num, 5)
   personality.objects.
   return render(request,"dialog.html")

# def select_local_img(request):
#    fileDir = '/home/user/project/django/Conversation_Web/static/img/persona/'
#    pathDir = os.listdir(fileDir)
#    sample = random.sample(pathDir, 5)
#    n = 0
#    for filename in sample:
#       n += 1
#       globals()['n%s' % n] = "{% static 'img/persona/"+str(filename)+"' %}"
#    return render(request,"dialog.html",{'n1':n1})

