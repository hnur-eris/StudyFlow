from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.contrib.auth import logout
from django.conf import settings
from django.db.models import Q

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/index.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('')

#for showing signup/login button for admin()
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/adminclick.html')


#for showing signup/login button for teacher()
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/teacherclick.html')


#for showing signup/login button for student()
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/studentclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'school/adminsignup.html',{'form':form})




def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher=teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'school/teachersignup.html',context=mydict)


def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.assignedTeacherId=request.POST.get('assignedTeacherId')
            student=student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'school/studentsignup.html',context=mydict)






#-----------for checking user is teacher , student or admin()
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,TEACHER OR STUDENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_teacher(request.user):
        accountapproval=models.Teacher.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher-dashboard')
        else:
            return render(request,'school/teacher_wait_for_approval.html')
    elif is_student(request.user):
        accountapproval=models.Student.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('student-dashboard')
        else:
            return render(request,'school/student_wait_for_approval.html')








#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    teachers=models.Teacher.objects.all().order_by('-id')
    students=models.Student.objects.all().order_by('-id')
    #for three cards
    teachercount=models.Teacher.objects.all().filter(status=True).count()
    pendingteachercount=models.Teacher.objects.all().filter(status=False).count()

    studentcount=models.Student.objects.all().filter(status=True).count()
    pendingstudentcount=models.Student.objects.all().filter(status=False).count()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'teachers':teachers,
    'students':students,
    'teachercount':teachercount,
    'pendingteachercount':pendingteachercount,
    'studentcount':studentcount,
    'pendingstudentcount':pendingstudentcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'school/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_teacher_view(request):
    return render(request,'school/admin_teacher.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_view(request):
    teachers=models.Teacher.objects.all().filter(status=True)
    return render(request,'school/admin_view_teacher.html',{'teachers':teachers})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_from_school_view(request,pk):
    teacher=models.Teacher.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-view-teacher')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_teacher_view(request,pk):
    teacher=models.Teacher.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)

    userForm=forms.TeacherUserForm(instance=user)
    teacherForm=forms.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST,instance=user)
        teacherForm=forms.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.status=True
            teacher.save()
            return redirect('admin-view-teacher')
    return render(request,'school/admin_update_teacher.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_teacher_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST, request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.status=True
            teacher.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-teacher')
    return render(request,'school/admin_add_teacher.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_teacher_view(request):
    #those whose approval are needed
    teachers=models.Teacher.objects.all().filter(status=False)
    return render(request,'school/admin_approve_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_teacher_view(request,pk):
    teacher=models.Teacher.objects.get(id=pk)
    teacher.status=True
    teacher.save()
    return redirect(reverse('admin-approve-teacher'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_teacher_view(request,pk):
    teacher=models.Teacher.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-approve-teacher')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_specialisation_view(request):
    teachers=models.Teacher.objects.all().filter(status=True)
    return render(request,'school/admin_view_teacher_specialisation.html',{'teachers':teachers})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_student_view(request):
    return render(request,'school/admin_student.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_view(request):
    students=models.Student.objects.all().filter(status=True)
    return render(request,'school/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_from_school_view(request,pk):
    student=models.Student.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-view-student')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_student_view(request,pk):
    student=models.Student.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)

    userForm=forms.StudentUserForm(instance=user)
    studentForm=forms.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST,instance=user)
        studentForm=forms.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.status=True
            student.assignedTeacherId=request.POST.get('assignedTeacherId')
            student.save()
            return redirect('admin-view-student')
    return render(request,'school/admin_update_student.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_student_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            student=studentForm.save(commit=False)
            student.user=user
            student.status=True
            student.assignedTeacherId=request.POST.get('assignedTeacherId')
            student.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-student')
    return render(request,'school/admin_add_student.html',context=mydict)



#------------------FOR APPROVING STUDENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_student_view(request):
    #those whose approval are needed
    students=models.Student.objects.all().filter(status=False)
    return render(request,'school/admin_approve_student.html',{'students':students})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_student_view(request,pk):
    student=models.Student.objects.get(id=pk)
    student.status=True
    student.save()
    return redirect(reverse('admin-approve-student'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_student_view(request,pk):
    student=models.Student.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-approve-student')



#--------------------- FOR DISCHARGING STUDENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_student_view(request):
    students=models.Student.objects.all().filter(status=True)
    return render(request,'school/admin_discharge_student.html',{'students':students})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_student_view(request,pk):
    student=models.Student.objects.get(id=pk)
    days=(date.today()-student.admitDate) #2 days, 0:00:00
    assignedTeacher=models.User.objects.all().filter(id=student.assignedTeacherId)
    d=days.days # only how many day that is 2
    studentDict={
        'studentId':pk,
        'name':student.get_name,
        'mobile':student.mobile,
        'address':student.address,
        'symptoms':student.symptoms,
        'admitDate':student.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedTeacherName':assignedTeacher[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'teacherFee':request.POST['teacherFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['teacherFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        studentDict.update(feeDict)
        #for updating to database studentDischargeDetails (pDD)
        pDD=models.StudentDischargeDetails()
        pDD.studentId=pk
        pDD.studentName=student.get_name
        pDD.assignedTeacherName=assignedTeacher[0].first_name
        pDD.address=student.address
        pDD.mobile=student.mobile
        pDD.symptoms=student.symptoms
        pDD.admitDate=student.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.teacherFee=int(request.POST['teacherFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['teacherFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'school/student_final_bill.html',context=studentDict)
    return render(request,'school/student_generate_bill.html',context=studentDict)



#--------------for discharge student bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.StudentDischargeDetails.objects.all().filter(studentId=pk).order_by('-id')[:1]
    dict={
        'studentName':dischargeDetails[0].studentName,
        'assignedTeacherName':dischargeDetails[0].assignedTeacherName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'teacherFee':dischargeDetails[0].teacherFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('school/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'school/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'school/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.teacherId=request.POST.get('teacherId')
            appointment.studentId=request.POST.get('studentId')
            appointment.teacherName=models.User.objects.get(id=request.POST.get('teacherId')).first_name
            appointment.studentName=models.User.objects.get(id=request.POST.get('studentId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'school/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'school/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ TEACHER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    #for three cards
    studentcount=models.Student.objects.all().filter(status=True,assignedTeacherId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,teacherId=request.user.id).count()
    studentdischarged=models.StudentDischargeDetails.objects.all().distinct().filter(assignedTeacherName=request.user.first_name).count()

    #for  table in teacher dashboard
    appointments=models.Appointment.objects.all().filter(status=True,teacherId=request.user.id).order_by('-id')
    studentid=[]
    for a in appointments:
        studentid.append(a.studentId)
    students=models.Student.objects.all().filter(status=True,user_id__in=studentid).order_by('-id')
    appointments=zip(appointments,students)
    mydict={
    'studentcount':studentcount,
    'appointmentcount':appointmentcount,
    'studentdischarged':studentdischarged,
    'appointments':appointments,
    'teacher':models.Teacher.objects.get(user_id=request.user.id), #for profile picture of teacher in sidebar
    }
    return render(request,'school/teacher_dashboard.html',context=mydict)



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_student_view(request):
    mydict={
    'teacher':models.Teacher.objects.get(user_id=request.user.id), #for profile picture of teacher in sidebar
    }
    return render(request,'school/teacher_student.html',context=mydict)





@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_student_view(request):
    students=models.Student.objects.all().filter(status=True,assignedTeacherId=request.user.id)
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    return render(request,'school/teacher_view_student.html',{'students':students,'teacher':teacher})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def search_view(request):
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    students=models.Student.objects.all().filter(status=True,assignedTeacherId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'school/teacher_view_student.html',{'students':students,'teacher':teacher})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_discharge_student_view(request):
    dischargedstudents=models.StudentDischargeDetails.objects.all().distinct().filter(assignedTeacherName=request.user.first_name)
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    return render(request,'school/teacher_view_discharge_student.html',{'dischargedstudents':dischargedstudents,'teacher':teacher})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_appointment_view(request):
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    return render(request,'school/teacher_appointment.html',{'teacher':teacher})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_appointment_view(request):
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,teacherId=request.user.id)
    studentid=[]
    for a in appointments:
        studentid.append(a.studentId)
    students=models.Student.objects.all().filter(status=True,user_id__in=studentid)
    appointments=zip(appointments,students)
    return render(request,'school/teacher_view_appointment.html',{'appointments':appointments,'teacher':teacher})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_delete_appointment_view(request):
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,teacherId=request.user.id)
    studentid=[]
    for a in appointments:
        studentid.append(a.studentId)
    students=models.Student.objects.all().filter(status=True,user_id__in=studentid)
    appointments=zip(appointments,students)
    return render(request,'school/teacher_delete_appointment.html',{'appointments':appointments,'teacher':teacher})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    teacher=models.Teacher.objects.get(user_id=request.user.id) #for profile picture of teacher in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,teacherId=request.user.id)
    studentid=[]
    for a in appointments:
        studentid.append(a.studentId)
    students=models.Student.objects.all().filter(status=True,user_id__in=studentid)
    appointments=zip(appointments,students)
    return render(request,'school/teacher_delete_appointment.html',{'appointments':appointments,'teacher':teacher})



#---------------------------------------------------------------------------------
#------------------------ TEACHER RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ STUDENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student=models.Student.objects.get(user_id=request.user.id)
    teacher=models.Teacher.objects.get(user_id=student.assignedTeacherId)
    mydict={
    'student':student,
    'teacherName':teacher.get_name,
    'teacherMobile':teacher.mobile,
    'teacherAddress':teacher.address,
    'symptoms':student.symptoms,
    'teacherDepartment':teacher.department,
    'admitDate':student.admitDate,
    }
    return render(request,'school/student_dashboard.html',context=mydict)



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_appointment_view(request):
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    return render(request,'school/student_appointment.html',{'student':student})



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_book_appointment_view(request):
    appointmentForm=forms.StudentAppointmentForm()
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'student':student,'message':message}
    if request.method=='POST':
        appointmentForm=forms.StudentAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('teacherId'))
            desc=request.POST.get('description')

            teacher=models.Teacher.objects.get(user_id=request.POST.get('teacherId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.teacherId=request.POST.get('teacherId')
            appointment.studentId=request.user.id #----user can choose any student but only their info will be stored
            appointment.teacherName=models.User.objects.get(id=request.POST.get('teacherId')).first_name
            appointment.studentName=request.user.first_name #----user can choose any student but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('student-view-appointment')
    return render(request,'school/student_book_appointment.html',context=mydict)



def student_view_teacher_view(request):
    teachers=models.Teacher.objects.all().filter(status=True)
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    return render(request,'school/student_view_teacher.html',{'student':student,'teachers':teachers})



def search_teacher_view(request):
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    teachers=models.Teacher.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'school/student_view_teacher.html',{'student':student,'teachers':teachers})




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_view_appointment_view(request):
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    appointments=models.Appointment.objects.all().filter(studentId=request.user.id)
    return render(request,'school/student_view_appointment.html',{'appointments':appointments,'student':student})



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_discharge_view(request):
    student=models.Student.objects.get(user_id=request.user.id) #for profile picture of student in sidebar
    dischargeDetails=models.StudentDischargeDetails.objects.all().filter(studentId=student.id).order_by('-id')[:1]
    studentDict=None
    if dischargeDetails:
        studentDict ={
        'is_discharged':True,
        'student':student,
        'studentId':student.id,
        'studentName':student.get_name,
        'assignedTeacherName':dischargeDetails[0].assignedTeacherName,
        'address':student.address,
        'mobile':student.mobile,
        'symptoms':student.symptoms,
        'admitDate':student.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'teacherFee':dischargeDetails[0].teacherFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(studentDict)
    else:
        studentDict={
            'is_discharged':False,
            'student':student,
            'studentId':request.user.id,
        }
    return render(request,'school/student_discharge.html',context=studentDict)


#------------------------ STUDENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'school/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'school/contactussuccess.html')
    return render(request, 'school/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------

