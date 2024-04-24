from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver



class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()



# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name="Email", unique=True)
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)



class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    # def __str__(self):
	#     return self.course_name



class Subjects(models.Model):
    id =models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, default=1) #need to give defauult course
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

GENERO = [
    ('1', 'Hombre'),
    ('2', 'LGBTQ+'),
    ('3', 'Mujer'),
]

class ProgramaAcademico(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Programa Académico', max_length=100)

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    programa_id = models.ForeignKey(ProgramaAcademico, on_delete=models.DO_NOTHING, null=True)
    gender = models.CharField(max_length=50, choices=GENERO)
    profile_pic = models.FileField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def clean(self):
        super().clean()
        if len(str(self.admin.username)) != 8 or not str(self.admin.username).isdigit():
            raise ValidationError(_('El nombre de usuario debe tener exactamente 8 caracteres y todos deben ser números.'))

    @property
    def username(self):
        return self.admin.username

    @username.setter
    def username(self, value):
        self.admin.username = value
    


class Attendance(models.Model):
    # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


MOTIVOSBAJAS = [
    ('1', 'A SU FAMILIA NO LE GUSTABA LA CARRERA'),
    ('2', 'ACTITUD DE PROFESORES'),
    ('3', 'AMBIENTE ESTUDIANTIL'),
    ('4', 'BAJA ACADÉMICA POR DESEMPEÑO ESCOLAR'),
    ('5', 'BAJA ACADÉMICA POR REPROBACIÓN'),
    ('6', 'CAMBIO DE PAÍS'),
    ('7', 'CAMPO LABORAL DIFÍCIL'),
    ('8', 'DESEMPEÑO ACADÉMICO INADECUADO'),
    ('9', 'DIFICULTAD ACADÉMICA POR LA MODALIDAD EN LÍNEA'),
    ('10', 'DIFICULTAD DE RELACIONARSE CON COMPAÑEROS/MAESTROS'),
    ('11', 'DIFICULTAD EN LAS MATERIAS'),
    ('12', 'ESTADO CIVIL'),
    ('13', 'ESTADO DE ÁNIMO'),
    ('14', 'FALTA DE HABILIDADES DE APRENDIZAJE'),
    ('15', 'HORARIOS COMPLICADOS'),
    ('16', 'INFLUENCIA DE PADRES/AMIGOS EN LA ELECCIÓN DE CARRERA'),
    ('17', 'LUGAR DE DOMICILIO'),
    ('18', 'MÉTODOS DE ENSEÑANZA'),
    ('19', 'MOTIVOS PERSONALES'),
    ('20', 'NO ERA MI VOCACIÓN'),
    ('21', 'PÉRDIDA DE INTERÉS POR LA CARRERA'),
    ('22', 'PERFIL DE LA CARRERA'),
    ('23', 'PROBLEMAS PERSONALES'),
    ('24', 'REPROBACIÓN'),
    ('25', 'SER ACEPTADO EN OTRA UNIVERSIDAD'),
    ('26', 'SITUACIÓN ECONÓMICA COMPLICADA'),
    ('27', 'TENER QUE TRABAJAR'),
    ('28', 'OTRO'),
    
]

class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
#Opciones de preguntas

SEMESTRE = [
    ('1', '1er. Semestre'),
    ('2', '2do. Semestre'),
    ('3', '3er. Semestre'),
    ('4', '4to. Semestre'),
    ('5', '5to. Semestre'),
    ('6', '6to. Semestre'),
    ('7', '7mo. Semestre'),
    ('8', '8vo. Semestre'),
    ('9', '9no. Semestre'),
    ('10', '10mo. Semestre'),
]

EXISTENCIA = [
    ('1', 'Exporienta'),
    ('2', 'Familiar o conocido'),
    ('3', 'Inf. Proporcionada por otra persona'),
    ('4', 'Página de la UAZ'),
    ('5', 'Redes Sociales'),
    ('6', 'Otro'),
]

SINO = [
    ('1', 'Si'),
    ('2', 'No'),
]

MEDIOS = [
    ('1', 'Calculadora'),
    ('2', 'Computadora'),
    ('3', 'Escritorio'),
    ('4', 'Impresora'),
    ('5', 'Internet'),
    ('6', 'Tablet'),
    ('7', 'Todas las anteriores'),
]

RECURSOS = [
    ('1', 'Insuficientes'),
    ('2', 'Nulos'),
    ('3', 'Suficientes'),
]

EXTRAORDINARIOS = [
    ('1', 'Calculadora'),
    ('2', 'Computadora'),
    ('3', 'Escritorio'),
]

ORDINARIOS = [
    ('1', 'Calculadora'),
    ('2', 'Computadora'),
    ('3', 'Escritorio'),
]

SERVICIOS = [
    ('1', 'Orientación vocacional'),
    ('2', 'Estrategias de Aprendizaje'),
    ('3', 'Asesoría Psicologica'),
    ('3', 'Mentorías'),
    ('3', 'Perfil de ingreso'),
    ('3', 'Becas de alimentación y de hospedaje'),
    ('3', 'Personas con discapacidad'),
    
]

TIPOBAJA = [
    ('1', 'Temporal'),
    ('2', 'Definitiva'),

    
]

class Diagnostico(models.Model):
    id = models.AutoField(primary_key=True)
    genero = models.CharField(max_length=1, choices=GENERO)
    genero = models.CharField(max_length=6)
    semestre = models.CharField(max_length=2, choices=SEMESTRE)
    existencia = models.CharField(max_length=2, choices=EXISTENCIA)
    otra = models.CharField(max_length=50)
    
    
    
    


#Creating Django Signals

# It's like trigger in database. It will run only when Data is Added in CustomUser model

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(admin=instance, address="", profile_pic="", gender="")
    

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()
    


#ENCUESTAS DEFINICIONES

class Choices(models.Model):
    choice = models.CharField(max_length=5000)
    is_answer = models.BooleanField(default=False)

class Questions(models.Model):
    question = models.CharField(max_length= 10000)
    question_type = models.CharField(max_length=20)
    required = models.BooleanField(default= False)
    answer_key = models.CharField(max_length = 5000, blank = True)
    score = models.IntegerField(blank = True, default=0)
    feedback = models.CharField(max_length = 5000, null = True)
    choices = models.ManyToManyField(Choices, related_name = "choices")

class Answer(models.Model):
    answer = models.CharField(max_length=5000)
    answer_to = models.ForeignKey(Questions, on_delete = models.CASCADE ,related_name = "answer_to")

class Form(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000, blank = True)
    creator = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = "creator")
    background_color = models.CharField(max_length=20, default = "#d9efed")
    text_color = models.CharField(max_length=20, default="#272124")
    collect_email = models.BooleanField(default=False)
    authenticated_responder = models.BooleanField(default = False)
    edit_after_submit = models.BooleanField(default=False)
    confirmation_message = models.CharField(max_length = 10000, default = "Your response has been recorded.")
    is_quiz = models.BooleanField(default=False)
    allow_view_score = models.BooleanField(default= True)
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)
    questions = models.ManyToManyField(Questions, related_name = "questions")

class Responses(models.Model):
    response_code = models.CharField(max_length=20)
    response_to = models.ForeignKey(Form, on_delete = models.CASCADE, related_name = "response_to")
    responder_ip = models.CharField(max_length=30)
    responder = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = "responder", blank = True, null = True)
    responder_email = models.EmailField(blank = True)
    response = models.ManyToManyField(Answer, related_name = "response")
    
ESTADOCAMBIO = [
    ('3', "Cambio de carrera dentro de la misma universidad"),
    ('2', "Cambio de carrera y de universidad"),
    ('3', "Desconoce"),
]

BAJACLASIFICACION = [
        ('1', 'Académica'),
        ('2', 'Administrativa'),
        ('3', 'No académica'),
    ]


class BajasAlumnos(models.Model):
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    semestre = models.CharField('Semestre', max_length=50, choices=SEMESTRE)
    fecha_baja = models.DateTimeField(auto_now_add = True)
    tipo_baja = models.CharField('Tipo de baja' , max_length=2, choices=TIPOBAJA)
    motivo_de_baja = models.CharField('Motivo de baja', max_length=2, choices=MOTIVOSBAJAS)
    fecha_de_baja = models.DateField('Fecha de baja')
    estado = models.CharField('Estado del cambio', max_length=50, choices=ESTADOCAMBIO)
    info_cambio = models.CharField('A donde se realiza el cambio', max_length=150)
    baja_clasificacion = models.CharField('Clasificación general de la baja', max_length=50, choices=BAJACLASIFICACION)
    
    def motivos(self):
        motivos_de_baja = ""
        lista_motivos = [x for x in self.motivo_de_baja if x.isdigit()]
        for motivo in lista_motivos:
            motivos_de_baja += MOTIVOSBAJAS[int(motivo)-1][1] + "\n"
        return motivos_de_baja[:-1]
    
    def clasificaciones(self):
        baja_clasificaciones = ""
        lista_clasificacion = [x for x in self.baja_clasificacion if x.isdigit()]
        for motivo in lista_clasificacion:
            baja_clasificaciones += BAJACLASIFICACION[int(motivo)-1][1] + "\n"
        return baja_clasificaciones[:-1]
    
    def __str__(self):
        return self.student_id.username
    
    

    
class ServiciosCase(models.Model):
    nombreServicio = models.CharField('Nombre de servicio', max_length=100, unique=True, null=False)
    informacionServicio = models.TextField('Información',null=True)
    imagenServicio = models.FileField(null=True)