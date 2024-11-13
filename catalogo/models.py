from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver

class UsuarioManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('O campo login é obrigatório')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Admin'),
        ('bibliotecario', 'Bibliotecário'),
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
        ('externo', 'Externo'),
    ]

    nome = models.CharField(max_length=255)
    tipo_usuario = models.CharField(max_length=50, choices=TIPO_USUARIO_CHOICES)
    numero_registro = models.CharField(max_length=50, blank=True, null=True)
    login = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['nome', 'tipo_usuario']

    def __str__(self):
        return self.nome
    
class Livro(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255, blank=True, null=True)
    editora = models.CharField(max_length=255, blank=True, null=True)
    assunto = models.CharField(max_length=100, blank=True, null=True)
    edicao = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class Exemplar(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    codigo_exemplar = models.CharField(max_length=50, unique=True)
    data_inclusao = models.DateField(auto_now_add=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_exemplar} - {self.livro.titulo}"

    class Meta:
        verbose_name = "Exemplar"
        verbose_name_plural = "Exemplares"
    
class Emprestimo(models.Model):
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Em Aberto')
    atraso = models.BooleanField(default=False)
    renovacoes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.nome} - {self.exemplar.codigo_exemplar}"

class Reserva(models.Model):
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    data_reserva = models.DateField(auto_now_add=True)
    status_reserva = models.CharField(max_length=50, default='Ativa')

    def __str__(self):
        return f"Reserva de {self.usuario.nome} - {self.exemplar.livro.titulo}"
    
class Multa(models.Model):
    emprestimo = models.ForeignKey(Emprestimo, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_geracao = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pendente')

    def __str__(self):
        return f"Multa de {self.emprestimo.usuario.nome} - {self.valor} R$"
    
@receiver(post_save, sender=Multa)
def bloquear_usuario_automaticamente(sender, instance, **kwargs):
    usuario = instance.emprestimo.usuario
    if usuario.tipo_usuario == 'aluno':
        multas_ativas = Multa.objects.filter(emprestimo__usuario=usuario, status='Pendente').count()
        if multas_ativas >= 2:
            usuario.is_blocked = True
            usuario.save()