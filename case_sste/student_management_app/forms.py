from django import forms
from student_management_app.models import MOTIVOSBAJAS, BAJACLASIFICACION, ESTADOCAMBIO, ServiciosCase, ProgramaAcademico, BAJACLASIFICACION, SEMESTRE, TIPOBAJA, CustomUser


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    username = forms.CharField(label="Matricula", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Contraseña", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Nombre(s)", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Apellidos", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Dirección", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))        
    
    gender_list = (
        ('1', 'Hombre'),
        ('2', 'LGBTQ+'),
        ('3', 'Mujer'),
    )
    
    programa_list = ProgramaAcademico.objects.values_list('id', 'nombre')
    programa = forms.ChoiceField(label="Programa Académico", choices=programa_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Género", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))

    def clean_programa(self):
        programa_id = self.cleaned_data['programa']
        return ProgramaAcademico.objects.get(id=programa_id)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) != 8:
            raise forms.ValidationError("La matricula 8 caracteres.")
        if not username.isdigit():
            raise forms.ValidationError("El nombre de usuario debe contener sólo números.")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Nombre(s)", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Apellidos", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Matricula", max_length=50, widget=forms.TextInput(attrs={"class":"form-control","readonly":True}))
    address = forms.CharField(label="Dirección", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    gender_list = (
        ('1', 'Hombre'),
        ('2', 'LGBTQ+'),
        ('3', 'Mujer'),
    )
    
    programa_id = forms.ChoiceField(label="Programa Académico", widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Género", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Imágen de perfil", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        programa_list = kwargs.pop('programa_list', None)
        super().__init__(*args, **kwargs)
        if programa_list:
            self.fields['programa'].choices = programa_list
    


OPCIONES = [
    ('1', 'Calculadora'),
    ('2', 'Computadora'),
    ('3', 'Escritorio'),
]


class BajasAlumnosForm(forms.Form):
    #Datos del alumno (solo para mostrar)
    student_id =forms.CharField( max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "readonly":True, "hidden":True}))
    first_name = forms.CharField(label="Nombre(s)", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Apellidos", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    programa_academico = forms.CharField(label="Programa Académico", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    #Datos de la baja
    semestre = forms.ChoiceField(label="Semestre", choices=SEMESTRE, widget=forms.Select(attrs={"class":"form-control"}))
    tipo_baja = forms.ChoiceField(label="Tipo de baja", choices=TIPOBAJA, widget=forms.Select(attrs={"class":"form-control"}))
    motivo_de_baja = forms.MultipleChoiceField(choices=MOTIVOSBAJAS, widget=forms.CheckboxSelectMultiple)
    fecha_de_baja = forms.DateField(label="Fecha de baja", widget=forms.DateInput(attrs={"type":"date"}))
    estado = forms.ChoiceField(label="Estado", choices=ESTADOCAMBIO, widget=forms.Select(attrs={"class":"form-control"}))
    info_cambio = forms.CharField(label="A donde se realiza el cambio", widget=forms.TextInput(attrs={"class":"form-control"}))
    baja_clasificacion = forms.MultipleChoiceField(label="Baja clasificación", choices=BAJACLASIFICACION, widget=forms.CheckboxSelectMultiple)

class ServiciosForm(forms.ModelForm):
    class Meta:
        model = ServiciosCase
        fields = '__all__'
        widgets = {
            "nombreServicio": forms.TextInput(attrs={'class': 'form-control'}),
            "informacionServicio": forms.Textarea(attrs={'class': 'form-control'}),
            
        }
        
class ProgramaAcademicoForm(forms.ModelForm):
    class Meta:
        model = ProgramaAcademico
        fields = '__all__'
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
        }