# members/views.py

import base64
import face_recognition
import numpy as np
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse
import datetime
from .models import *
from .forms import *

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'members/register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'members/scan_face.html', {'user': request.user})

class CustomLoginView(auth_views.LoginView):
    template_name = 'members/login.html'

def is_manager(user):
    return user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def user_list(request):
    managers = CustomUser.objects.filter(role='manager')
    cashiers = CustomUser.objects.filter(role='cashier')
    users = list(managers) + list(cashiers)
    return render(request, 'members/user_list.html', {'users': users})

@login_required
@user_passes_test(is_manager)
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'members/edit_user.html', {'form': form, 'user': user})

def add_member(request):
    error = None  # กำหนดตัวแปร error เป็น None
    if request.method == 'POST':  # ตรวจสอบว่าคำขอเป็นแบบ POST หรือไม่
        form = MemberForm(request.POST, request.FILES)  # รับข้อมูลจากฟอร์ม
        if form.is_valid():  # ตรวจสอบว่าฟอร์มถูกต้องหรือไม่
            member = form.save(commit=False)  # สร้างออบเจ็กต์ Member แต่ยังไม่บันทึกลงฐานข้อมูล
            photo_data = form.cleaned_data.get('photo_data')  # รับข้อมูลรูปภาพจากฟอร์ม
            
            if photo_data:  # ตรวจสอบว่ามีข้อมูลรูปภาพหรือไม่
                format, imgstr = photo_data.split(';base64,')  # แยกส่วนที่เป็นรูปแบบและข้อมูลที่เข้ารหัส Base64 ออกจากกัน
                ext = format.split('/')[-1]  # ดึงนามสกุลไฟล์จากรูปแบบ
                member.face_image.save(f'{member.name}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)  # บันทึกภาพใบหน้า
            
                if member.face_image:  # ตรวจสอบว่ามีการบันทึกภาพใบหน้าแล้วหรือไม่
                    image = face_recognition.load_image_file(member.face_image)  # โหลดรูปภาพ
                    face_encodings = face_recognition.face_encodings(image, num_jitters=5, model='large')  # ดึง face encodings จากรูปภาพ
                    if len(face_encodings) > 1:  # ตรวจสอบว่ามีใบหน้ามากกว่าหนึ่งใบหน้าหรือไม่
                        error = 'พบใบหน้ามากกว่าหนึ่งใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้าเพียงใบหน้าเดียว'
                    elif len(face_encodings) == 1:  # ตรวจสอบว่ามีใบหน้าเพียงหนึ่งใบหน้าหรือไม่
                        member.face_encoding = np.array2string(face_encodings[0])  # เก็บ face encoding เป็นสตริง
                        member.save()  # บันทึกสมาชิกลงฐานข้อมูล
                        return redirect('member_list')  # ย้ายไปหน้ารายการสมาชิก
                    else:  # ไม่พบใบหน้าในภาพ
                        error = 'ไม่พบใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้า'
    
    else:
        form = MemberForm()  # สร้างฟอร์มเปล่า
    return render(request, 'members/add_member.html', {'form': form, 'error': error})  # แสดงฟอร์มเพื่อเพิ่มสมาชิกพร้อมข้อความข้อผิดพลาด (ถ้ามี)

def check_faces(request):
    if request.method == 'POST':  # ตรวจสอบว่าคำขอเป็นแบบ POST หรือไม่
        photo_data = request.POST.get('photo_data')  # รับข้อมูลรูปภาพจากคำขอ POST
        if photo_data:  # ตรวจสอบว่ามีข้อมูลรูปภาพหรือไม่
            format, imgstr = photo_data.split(';base64,')  # แยกส่วนที่เป็นรูปแบบและข้อมูลที่เข้ารหัส Base64 ออกจากกัน
            ext = format.split('/')[-1]  # ดึงนามสกุลไฟล์จากรูปแบบ
            image_data = base64.b64decode(imgstr)  # ถอดรหัสข้อมูล Base64 เป็นข้อมูลไบนารี
            # โหลดรูปภาพจากข้อมูลไบนารี
            image = face_recognition.load_image_file(ContentFile(image_data, 'scan_image.' + ext))
            # ดึง face encodings จากรูปภาพด้วยการตั้งค่า num_jitters และ model
            face_encodings = face_recognition.face_encodings(image, num_jitters=1, model='small')
            
            if len(face_encodings) > 1:  # ตรวจสอบว่ามีใบหน้ามากกว่าหนึ่งใบหน้าหรือไม่
                return JsonResponse({'error': 'พบใบหน้ามากกว่าหนึ่งใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้าเพียงใบหน้าเดียว'})
            elif len(face_encodings) == 0:  # ตรวจสอบว่าไม่พบใบหน้าในภาพหรือไม่
                return JsonResponse({'error': 'ไม่พบใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้า'})
            else:  # พบใบหน้าเพียงหนึ่งใบหน้า
                return JsonResponse({'success': 'พบใบหน้าเพียงใบหน้าเดียวในภาพ'})
    return JsonResponse({'error': 'คำขอไม่ถูกต้อง'})

@login_required
def member_list(request):
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})

def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    old_image_path = member.face_image.path if member.face_image else None  # เก็บ path ของรูปภาพเก่า
    error = None

    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            member = form.save(commit=False)
            photo_data = form.cleaned_data.get('photo_data')

            if photo_data:
                # ลบไฟล์รูปภาพเก่าถ้ามีการอัปโหลดรูปภาพใหม่
                if old_image_path and os.path.exists(old_image_path):
                    os.remove(old_image_path)

                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                member.face_image.save(f'{member.name}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)

                if member.face_image:
                    image = face_recognition.load_image_file(member.face_image)
                    face_encodings = face_recognition.face_encodings(image, num_jitters=5, model='large')
                    if len(face_encodings) > 1:
                        error = 'พบใบหน้ามากกว่าหนึ่งใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้าเพียงใบหน้าเดียว'
                    elif len(face_encodings) == 1:
                        member.face_encoding = np.array2string(face_encodings[0])
                        member.save()
                        return redirect('member_list')
                    else:
                        error = 'ไม่พบใบหน้าในภาพ กรุณาอัปโหลดภาพที่มีใบหน้า'
            else:
                member.save()
                return redirect('member_list')

    else:
        form = MemberForm(instance=member)

    return render(request, 'members/edit_member.html', {'form': form, 'member': member, 'error': error})

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
                        known_face_encoding = np.fromstring(member.face_encoding[1:-1], sep=' ')
                        result_face = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding,tolerance=0.4)[0]
                        if result_face == False:
                            error = 'No match found'
    
                        elif result_face == True:
                            distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding)[0]
                            similarity_percentage = (1 - distance) * 100
                            CustomerVisit.objects.create(date=timezone.now(), member=member, is_member=True)
                            return render(request, 'members/scan_face.html', {'member': member, 'similarity': similarity_percentage})
                
                CustomerVisit.objects.create(date=timezone.now(), is_member=False)
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

def dashboard(request):
    today = timezone.localtime().date()  # ใช้ localtime เพื่อให้แน่ใจว่าใช้ Timezone ที่ถูกต้อง
    visits_today = CustomerVisit.objects.filter(date=today).count()
    member_visits_today = CustomerVisit.objects.filter(date=today, is_member=True).count()
    non_member_visits_today = CustomerVisit.objects.filter(date=today, is_member=False).count()

    # เตรียมข้อมูลสำหรับ 7 วันที่ผ่านมา
    labels = []
    member_data = []
    non_member_data = []

    for i in range(7):
        day = today - datetime.timedelta(days=i)
        labels.append(day.strftime('%Y-%m-%d'))
        member_data.append(CustomerVisit.objects.filter(date=day, is_member=True).count())
        non_member_data.append(CustomerVisit.objects.filter(date=day, is_member=False).count())

    context = {
        'visits_today': visits_today,
        'member_visits_today': member_visits_today,
        'non_member_visits_today': non_member_visits_today,
        'labels': labels[::-1],  # สลับลำดับเพื่อให้วันล่าสุดอยู่ก่อน
        'member_data': member_data[::-1],
        'non_member_data': non_member_data[::-1],
    }
    return render(request, 'members/dashboard.html', context)
