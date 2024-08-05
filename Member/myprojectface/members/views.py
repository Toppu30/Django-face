# members/views.py

import base64
import face_recognition
import numpy as np
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
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
                face_encodings = face_recognition.face_encodings(image, num_jitters=5 , model='large' )
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
            unknown_face_encodings = face_recognition.face_encodings(image, num_jitters=5 , model='large' )
            
            if unknown_face_encodings:
                unknown_face_encoding = unknown_face_encodings[0]
                members = Member.objects.all()
                for member in members:
                    if member.face_encoding:
                        print(member.face_encoding)
                        known_face_encoding = np.fromstring(member.face_encoding[1:-1], sep=' ')
                        result_face = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding,tolerance=0.4)[0]
                        if result_face == False:
                            error = 'No match found'
    
                        else:
                            distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding)[0]
                            similarity_percentage = (1 - distance) * 100
                            return render(request, 'members/scan_face.html', {'member': member, 'similarity': similarity_percentage})
                        
                return render(request, 'members/scan_face.html', {'error': error})
                            
            else:
                error = 'No face detected'
    
    return render(request, 'members/scan_face.html', {'member': member, 'error': error})

def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return redirect('member_list')
