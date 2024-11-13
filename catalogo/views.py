from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Livro, Exemplar, Emprestimo, Reserva, Multa, Usuario
import random
import string

def home(request):
    if request.user.is_authenticated:
        usuario = request.user
        if usuario.tipo_usuario == "aluno":
            return render(request, 'home_aluno.html')
        elif usuario.tipo_usuario == "bibliotecario":
            return render(request, 'home_bibliotecario.html')
        elif usuario.tipo_usuario == "externo":
            return render(request, 'home_externo.html')
        else:
            exemplares_disponiveis = Exemplar.objects.filter(disponivel=True)
            return render(request, 'home_admin.html', {'exemplares_disponiveis': exemplares_disponiveis})
    return render(request, 'home_deslogado.html')

def gerar_numero_registro():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_usuario = request.POST.get('tipo_usuario')
        login_user = request.POST.get('login')
        senha = request.POST.get('senha')
        numero_registro = gerar_numero_registro()

        User = get_user_model()
        novo_usuario = User.objects.create_user(
            login=login_user,
            password=senha,
            nome=nome,
            tipo_usuario=tipo_usuario,
            numero_registro=numero_registro
        )

        return redirect('login_usuario')
    
    return render(request, 'cadastrar_usuario.html')


def login_usuario(request):
    if request.method == 'POST':
        login_user = request.POST.get('login')
        senha = request.POST.get('senha')
        
        user = authenticate(request, username=login_user, password=senha)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse('Credenciais inválidas. Tente novamente.')

    return render(request, 'login.html')

def logout_usuario(request):
    logout(request)
    return redirect('login_usuario')

@login_required
def cadastrar_livro(request):
    if request.user.tipo_usuario != "bibliotecario":
        return HttpResponse("Acesso negado: apenas bibliotecários podem cadastrar livros.")

    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        editora = request.POST.get('editora')
        assunto = request.POST.get('assunto')
        edicao = request.POST.get('edicao')

        novo_livro = Livro(isbn=isbn, titulo=titulo, autor=autor, editora=editora, assunto=assunto, edicao=edicao)
        novo_livro.save()

        return HttpResponse('Livro cadastrado com sucesso!')
    
    return render(request, 'cadastrar_livro.html')

@login_required
def listar_livros(request):
    livros = Livro.objects.all()
    return render(request, 'listar_livros.html', {'livros': livros})

def consultar_catalogo(request):
    query = request.GET.get('q', '')
    livros = Livro.objects.all()

    if query:
        livros = livros.filter(
            titulo__icontains=query
        ) | livros.filter(
            autor__icontains=query
        ) | livros.filter(
            isbn__icontains=query
        ) | livros.filter(
            assunto__icontains=query
        )

    return render(request, 'consultar_catalogo.html', {'livros': livros, 'query': query})

@login_required
def emprestar_livro(request):
    if request.user.tipo_usuario != "bibliotecario":
        return HttpResponse("Acesso negado: apenas bibliotecários podem realizar empréstimos.")

    if request.method == 'POST':
        codigo_exemplar = request.POST.get('codigo_exemplar')
        usuario_id = request.POST.get('usuario_id')

        try:
            usuario = Usuario.objects.get(id=usuario_id)
            if usuario.is_blocked:
                return HttpResponse('Usuário bloqueado: não é possível realizar empréstimos.')

            exemplar = Exemplar.objects.get(codigo_exemplar=codigo_exemplar, disponivel=True)
            emprestimo = Emprestimo(exemplar=exemplar, usuario=usuario)
            emprestimo.save()

            exemplar.disponivel = False
            exemplar.save()

            return HttpResponse('Livro emprestado com sucesso!')
        except Exemplar.DoesNotExist:
            return HttpResponse('Exemplar não disponível ou não encontrado.')
        except Usuario.DoesNotExist:
            return HttpResponse('Usuário não encontrado.')
    
    exemplares = Exemplar.objects.filter(disponivel=True)
    usuarios = Usuario.objects.all()
    return render(request, 'emprestar_livro.html', {'exemplares': exemplares, 'usuarios': usuarios})

@login_required
def devolver_livro(request):
    if request.user.tipo_usuario != "bibliotecario":
        return HttpResponse("Acesso negado: apenas bibliotecários podem processar devoluções.")

    if request.method == 'POST':
        codigo_exemplar = request.POST.get('codigo_exemplar')

        try:
            emprestimo = Emprestimo.objects.get(exemplar__codigo_exemplar=codigo_exemplar, data_devolucao__isnull=True)
            emprestimo.data_devolucao = request.POST.get('data_devolucao')
            emprestimo.save()

            exemplar = emprestimo.exemplar
            exemplar.disponivel = True
            exemplar.save()

            if emprestimo.atraso:
                Multa.objects.create(emprestimo=emprestimo, valor=10.0, status='Pendente')

            return HttpResponse('Livro devolvido com sucesso!')
        except Emprestimo.DoesNotExist:
            return HttpResponse('Nenhum empréstimo ativo para este exemplar.')

    exemplares_emprestados = Exemplar.objects.filter(disponivel=False)
    return render(request, 'devolver_livro.html', {'exemplares': exemplares_emprestados})

@login_required
def reservar_livro(request):
    if request.user.tipo_usuario not in ["aluno", "professor"]:
        return HttpResponse("Acesso negado: apenas alunos e professores podem reservar livros.")

    if request.method == 'POST':
        codigo_exemplar = request.POST.get('codigo_exemplar')
        usuario_id = request.POST.get('usuario_id')

        try:
            exemplar = Exemplar.objects.get(codigo_exemplar=codigo_exemplar, disponivel=False)
            usuario = Usuario.objects.get(id=usuario_id)

            reserva = Reserva(exemplar=exemplar, usuario=usuario)
            reserva.save()

            return HttpResponse('Livro reservado com sucesso!')
        except Exemplar.DoesNotExist:
            return HttpResponse('Exemplar não disponível para reserva.')
        except Usuario.DoesNotExist:
            return HttpResponse('Usuário não encontrado.')

    exemplares = Exemplar.objects.filter(disponivel=False)
    usuarios = Usuario.objects.all()
    return render(request, 'reservar_livro.html', {'exemplares': exemplares, 'usuarios': usuarios})

@login_required
def visualizar_multas(request):
    multas = Multa.objects.all()
    return render(request, 'visualizar_multas.html', {'multas': multas})

@login_required
def editar_usuario(request, usuario_id):
    if request.user.tipo_usuario != "admin":
        return HttpResponse("Acesso negado: apenas o administrador pode editar usuários.")
        
    usuario = Usuario.objects.get(id=usuario_id)
    if request.method == 'POST':
        usuario.nome = request.POST.get('nome')
        usuario.login = request.POST.get('login')
        usuario.tipo_usuario = request.POST.get('tipo_usuario')
        usuario.save()

        return HttpResponse('Usuário atualizado com sucesso!')
    
    return render(request, 'editar_usuario.html', {'usuario': usuario})

@login_required
def marcar_exemplar_indisponivel(request, exemplar_id):
    if request.user.tipo_usuario != "bibliotecario":
        return HttpResponse("Acesso negado: apenas bibliotecários podem marcar exemplares como indisponíveis.")
        
    exemplar = Exemplar.objects.get(id=exemplar_id)
    if request.method == 'POST':
        exemplar.disponivel = False
        exemplar.save()

        return HttpResponse('Exemplar marcado como indisponível.')

    return render(request, 'marcar_exemplar_indisponivel.html', {'exemplar': exemplar})