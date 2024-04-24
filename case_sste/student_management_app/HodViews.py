from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.db import transaction
from django.db.models import Count
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
import io
import csv
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import BajasAlumnos, ServiciosCase, SEMESTRE, TIPOBAJA
from student_management_app.models import CustomUser, ProgramaAcademico, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, BajasAlumnosForm, EditStudentForm, ServiciosForm


def admin_home(request):
    all_student_count = Students.objects.all().count()
    staff_count = Staffs.objects.all().count()

    context = {
        "all_student_count": all_student_count,
        "staff_count": staff_count,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(
                username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')


def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def add_programa(request):
    return render(request, "hod_template/add_programa_template.html")


def add_programa_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_programa')
    else:
        programa = request.POST.get('programa')
        try:
            programa_model = ProgramaAcademico(nombre=programa)
            programa_model.save()
            messages.success(
                request, "Programa Académico guardado correctamente!")
            return redirect('add_programa')
        except:
            messages.error(request, "Fallo al guardar el Programa Académico!")
            return redirect('add_programa')


def manage_programa(request):
    programas = ProgramaAcademico.objects.all()
    context = {
        "programas": programas
    }
    return render(request, 'hod_template/manage_programa_template.html', context)


def edit_programa(request, programa_id):
    programa = ProgramaAcademico.objects.get(id=programa_id)
    context = {
        "programa": programa,
        "id": programa_id
    }
    return render(request, 'hod_template/edit_programa_template.html', context)


def edit_programa_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        programa_id = request.POST.get('programa_id')
        nombre = request.POST.get('programa')

        try:
            programa = ProgramaAcademico.objects.get(id=programa_id)
            programa.nombre = nombre
            programa.save()

            messages.success(request, "Programa actualizado.")
            return redirect('manage_programa')

        except:
            messages.error(request, "Fallo la edición del programa.")
            return redirect('/edit_programa/'+programa_id)


def delete_programa(request, programa_id):
    programa = ProgramaAcademico.objects.get(id=programa_id)
    try:
        programa.delete()
        messages.success(
            request, "Programa académico eliminado correctamente.")
        return redirect('manage_programa')
    except:
        messages.error(
            request, "Fallo la eliminación del programa académico")
        return redirect('manage_programa')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(
                session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)


def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Error de registro")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            programa_id = form.cleaned_data['programa']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                    user.students.address = address
                    user.students.programa_id = programa_id
                    user.students.gender = gender
                    user.students.profile_pic = profile_pic_url
                    user.save()
                    messages.success(request, "El estudiante se ha agregado")
                    return redirect('manage_student')
            except Exception as error:
                print(error)
                messages.error(request, "Error al agregar estudiante")
                return redirect('add_student')
        else:
            messages.error(request, form.errors)
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = AddStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['gender'].initial = student.gender

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            programa_id = form.cleaned_data['programa'].id

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address
                student_model.programa_id_id = programa_id

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Failed to Uupdate Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Estudiante eliminado.")
        return redirect('manage_student')
    except:
        messages.error(request, "Fallo al eliminar estudiante")
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)


def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)

        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name,
                               course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff

            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))
            # return redirect('/edit_subject/'+subject_id)


def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    bajas = BajasAlumnos.objects.all()
    context = {
        "bajas": bajas
    }
    return render(request, 'hod_template/student_leave_view.html', context)


def eliminar_baja(request, baja_id):
    bajas = BajasAlumnos.objects.get(id=baja_id)
    try:
        bajas.delete()
        messages.success(request, "Baja de alumno eliminada.")
        return redirect('student_leave_view')
    except:
        messages.error(request, "Error al borrar baja.")
        return redirect('student_leave_view')


def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(
        subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small = {"id": attendance_single.id, "attendance_date": str(
            attendance_single.attendance_date), "session_year_id": attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.first_name +
                      " "+student.student_id.admin.last_name, "status": student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context = {
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def staff_profile(request):
    pass


def student_profile(requtest):
    pass


def baja_alumnos_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/baja_alumnos.html', context)


def serviciosCase(request):
    return render(request, "hod_template/servicios.html")


def bajasAlumnos(request):
    form = BajasAlumnosForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/baja_alumnos.html', context)


def bajasAlumnosSave(request):
    if request.method != "POST":
        messages.error(request, "Error de registro")
        return redirect('baja_alumnos')
    else:
        form = BajasAlumnosForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario validados
            student_id = Students.objects.get(
                id=form.cleaned_data['student_id'])
            semestre = form.cleaned_data['semestre']
            tipo_baja = form.cleaned_data['tipo_baja']
            motivo_de_baja = form.cleaned_data['motivo_de_baja']
            fecha_de_baja = form.cleaned_data['fecha_de_baja']
            estado = form.cleaned_data['estado']
            info_cambio = form.cleaned_data['info_cambio']
            baja_clasificacion = form.cleaned_data['baja_clasificacion']

            try:
                # Crear una nueva instancia de BajasAlumnos y guardarla en la base de datos
                nueva_baja = BajasAlumnos(student_id=student_id, semestre=semestre,
                                          tipo_baja=tipo_baja, motivo_de_baja=motivo_de_baja,
                                          fecha_de_baja=fecha_de_baja, estado=estado, info_cambio=info_cambio,
                                          baja_clasificacion=baja_clasificacion)
                nueva_baja.save()
                messages.success(request, "Baja registrada correctamente!")
                return redirect('reporte_baja_pdf/'+str(nueva_baja.id))
            except Exception as error:
                print(error)
                messages.error(request, "Error al registrar la baja")
                return redirect('baja_alumnos')
        else:
            print("error")
            messages.error(request, form.errors)
            return redirect('baja_alumnos')


def editarBaja(request, id):
    baja = BajasAlumnos.objects.get(id=id)
    if request.method == 'POST':
        form = BajasAlumnosForm(request.POST, request.FILES, instance=baja)
        if form.is_valid():
            form.save()
            messages.success(
                request, "¡El servicio ha sido actualizado exitosamente!")
            return redirect('baja_alumnos')
        else:
            messages.error(
                request, "Por favor, corrija los errores del formulario.")
    else:
        form = BajasAlumnosForm(instance=baja)
    return render(request, 'hod_template/editar_baja.html', {'form': form, 'baja': baja})


def buscar_estudiante(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        username = request.POST.get('username')
        try:
            student = Students.objects.get(admin__username=username)
            # Aquí creamos un diccionario con los datos del estudiante que queremos devolver
            data = {
                'student_id': student.id,
                'first_name': student.admin.first_name,
                'last_name': student.admin.last_name,
                'programa_academico': student.programa_id.nombre
            }
            # Enviamos los datos al cliente en formato JSON
            return JsonResponse({'success': True, 'data': data})
        except Students.DoesNotExist:
            # Si el estudiante no existe, enviamos un mensaje de error al cliente
            return JsonResponse({'success': False, 'message': 'No se encontró un estudiante con esa matrícula.'})
    else:
        # Si la petición no es Ajax, devolvemos un error 400 Bad Request
        return JsonResponse({'success': False, 'message': 'Petición inválida.'}, status=400)


def reporte_baja_pdf(request, baja_id):
    baja = BajasAlumnos.objects.get(id=baja_id)
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%d de %B de %Y")
    motivos = baja.motivos().replace('\n', ', ')
    datos = {
        'baja': baja,
        'student': baja.student_id,
        'fecha': fecha_formateada,
        'motivos': motivos
    }
    template = get_template(
        'pdf/template_reporte_baja_pdf.html')
    html = template.render(datos)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
        #return redirect('student_leave_view')
    return reload()


def contarResponsables(request):
    cantidadResponsables = Staffs.objects.count()
    return render(request, 'admin_home.html', {'my_objects_count': cantidadResponsables})


def export_csv_baja_alumnos(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Bajas.csv"'
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['id', 'Matricula', 'Nombre del alumno', 'Semestre', 'Genero', 'Programa académico',
                     'Fecha de baja', 'Tipo de baja', 'Motivos para el abandono de la carrera', 'Estado general de la baja',
                     'A donde se realiza el cambio', 'Clasificación general de la baja'])  # Aquí añadimos las columnas que queremos exportar

    queryset = BajasAlumnos.objects.all()
    for bajasAlumnos in queryset:
        writer.writerow([bajasAlumnos.id, bajasAlumnos.student_id.admin.username, (bajasAlumnos.student_id.admin.first_name + ' '+bajasAlumnos.student_id.admin.last_name),
                         bajasAlumnos.get_semestre_display(), bajasAlumnos.student_id.get_gender_display(),
                         bajasAlumnos.student_id.programa_id.nombre, bajasAlumnos.fecha_baja, bajasAlumnos.get_tipo_baja_display(),
                         bajasAlumnos.motivos(), bajasAlumnos.get_estado_display(), bajasAlumnos.info_cambio, bajasAlumnos.clasificaciones()])  # Aquí añadimos los datos de cada registro
    response.write(csv_file.getvalue().encode('utf-8'))
    return response


def registrarServicios(request):
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio registrado!")
            return redirect('servicios')
    else:
        form = ServiciosForm()
    return render(request, 'hod_template/registrar_servicios.html', {'form': form})


def mostrarServicios(request):
    servicios = ServiciosCase.objects.all()
    context = {
        'servicios': servicios,
    }
    return render(request, 'hod_template/servicios.html', context)


def editarServicio(request, id):
    servicio = ServiciosCase.objects.get(id=id)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(
                request, "¡El servicio ha sido actualizado exitosamente!")
            return redirect('servicios')
        else:
            messages.error(
                request, "Por favor, corrija los errores del formulario.")
    else:
        form = ServiciosForm(instance=servicio)
    return render(request, 'hod_template/editar_servicio.html', {'form': form, 'servicio': servicio})


def contar_servicios(request):
    count = ServiciosCase.objects.count()
    return render(request, 'servicios.html', {'count': count})


def vistaDetallada(request, id):
    evento = ServiciosCase.objects.get(id=id)
    return render(request, 'detalle_evento.html', {'evento': evento})


def eliminarServicio(request, id):
    ServiciosCase.objects.get(id=id).delete()
    return redirect('servicios')


# calendario
def calendarioSesiones(request):
    return render(request, "hod_template/calendario.html")


def reporte_alumnos(request):
    # Bajas por semestre
    bajas_por_semestre = BajasAlumnos.objects.values(
        'semestre').annotate(total=Count('id'))
    for resultado in bajas_por_semestre:
        resultado['semestre'] = SEMESTRE[int(resultado['semestre'])-1][1]
    bajas_por_semestre = json.dumps(
        list(bajas_por_semestre), cls=DjangoJSONEncoder)

    # Bajas por tipo de baja
    baja_tipo = BajasAlumnos.objects.values(
        'tipo_baja').annotate(total=Count('id'))
    for resultado in baja_tipo:
        resultado['tipo_baja'] = TIPOBAJA[int(resultado['tipo_baja'])-1][1]
    baja_tipo = json.dumps(list(baja_tipo), cls=DjangoJSONEncoder)

    context = {
        'bajas_por_semestre': bajas_por_semestre,
        'baja_tipo': baja_tipo
    }
    return render(request, "hod_template/reportes_alumnos.html", context)
