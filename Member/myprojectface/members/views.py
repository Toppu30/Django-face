# members/views.py

import base64
import face_recognition
import numpy as np
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .models import Member
from .forms import MemberForm

def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            photo_data = form.cleaned_data.get('photo_data')
            
            if photo_data:
                format, imgstr = photo_data.split(';base64,') 
                ext = format.split('/')[-1] 
                member.face_image.save(f'{member.name}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
            
            if member.face_image:
                image = face_recognition.load_image_file(member.face_image)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    member.face_encoding = np.array2string(face_encodings[0])
            member.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'members/add_member.html', {'form': form})

def member_list(request):
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})

def scan_face(request):
    member = None
    error = None

    if request.method == 'POST':
        photo_data = request.POST.get('photo_data')
        if photo_data:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = base64.b64decode(imgstr)
            image = face_recognition.load_image_file(ContentFile(image_data, 'scan_image.' + ext))
            unknown_face_encodings = face_recognition.face_encodings(image)

            if unknown_face_encodings:
                unknown_face_encoding = unknown_face_encodings[0]
                members = Member.objects.all()
                threshold = 0.6  # คุณสามารถปรับค่า threshold นี้ตามต้องการ
                for member in members:
                    if member.face_encoding:
                        known_face_encoding = np.fromstring(member.face_encoding[1:-1], sep=' ')
                        distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding)[0]
                        if distance < threshold:
                            similarity_percentage = (1 - distance) * 100
                            return render(request, 'members/scan_face.html', {'member': member, 'similarity': similarity_percentage})

                error = 'No match found'
            else:
                error = 'No face detected'
    
    return render(request, 'members/scan_face.html', {'member': member, 'error': error})
