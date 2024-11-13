from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group, Permission
from .models import Usuario, Livro, Exemplar, Emprestimo, Reserva, Multa
from .views import gerar_numero_registro

def configurar_grupos():
    grupos_permissoes = {
        'externo': ['view_livro'],
        'aluno': ['view_livro', 'reserve_exemplar', 'view_multa'],
        'professor': ['view_livro', 'reserve_exemplar', 'view_multa'],
        'bibliotecario': [
            'view_livro', 'add_livro', 'change_livro', 'delete_livro',
            'add_exemplar', 'change_exemplar', 'delete_exemplar', 'view_exemplar',
            'add_emprestimo', 'change_emprestimo', 'view_emprestimo', 'delete_emprestimo',
            'add_reserva', 'change_reserva', 'view_reserva', 'delete_reserva',
            'add_multa', 'change_multa', 'view_multa'
        ],
        'admin': ['view', 'add', 'change', 'delete'],
    }

    for nome_grupo, permissoes in grupos_permissoes.items():
        grupo, created = Group.objects.get_or_create(name=nome_grupo)
        if created:
            for codename in permissoes:
                for model in [Livro, Exemplar, Emprestimo, Reserva, Multa]:
                    try:
                        permission = Permission.objects.get(codename=f"{codename}_{model._meta.model_name}")
                        grupo.permissions.add(permission)
                    except Permission.DoesNotExist:
                        continue

configurar_grupos()

class UsuarioCreationForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'tipo_usuario', 'login', 'is_active', 'is_staff', 'is_blocked']

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.numero_registro:
            user.numero_registro = gerar_numero_registro()
        if commit:
            user.save()
            grupo = Group.objects.get(name=user.tipo_usuario)
            user.groups.add(grupo)
        return user

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioCreationForm
    list_display = ['nome', 'tipo_usuario', 'login', 'is_active', 'is_staff', 'is_blocked']
    search_fields = ['nome', 'login']
    list_filter = ['tipo_usuario', 'is_active', 'is_staff']
    exclude = ['user_permissions', 'last_login', 'date_joined']

admin.site.register(Usuario, UsuarioAdmin)

class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'isbn', 'autor', 'editora', 'assunto']
    search_fields = ['titulo', 'isbn', 'autor']
    list_filter = ['assunto', 'editora']

admin.site.register(Livro, LivroAdmin)

class ExemplarAdmin(admin.ModelAdmin):
    list_display = ['codigo_exemplar', 'livro', 'disponivel']
    search_fields = ['codigo_exemplar', 'livro__titulo']
    list_filter = ['disponivel']

admin.site.register(Exemplar, ExemplarAdmin)

class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'exemplar', 'data_emprestimo', 'data_devolucao', 'status', 'atraso']
    search_fields = ['usuario__nome', 'exemplar__codigo_exemplar']
    list_filter = ['status', 'atraso']

admin.site.register(Emprestimo, EmprestimoAdmin)

class ReservaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'exemplar', 'data_reserva', 'status_reserva']
    search_fields = ['usuario__nome', 'exemplar__codigo_exemplar']
    list_filter = ['status_reserva']

admin.site.register(Reserva, ReservaAdmin)

class MultaAdmin(admin.ModelAdmin):
    list_display = ['emprestimo', 'valor', 'data_geracao', 'status']
    search_fields = ['emprestimo__usuario__nome']
    list_filter = ['status']

admin.site.register(Multa, MultaAdmin)