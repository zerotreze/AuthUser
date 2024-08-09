from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import constants
from .models import Empresas

def cadastrar_empresa(request):
    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', {
            'tempo_existencia': Empresas.tempo_existencia_choices,
            'areas': Empresas.area_choices
        })

    elif request.method == "POST":
        # Captura os dados do formulário
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.getlist('estagio')  # Captura uma lista de valores para o estágio
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        # Concatena os valores de `estagio` em uma string separada por vírgulas
        estagio_str = ','.join(estagio) if estagio else None

        try:
            # Cria uma nova instância da empresa e salva no banco de dados
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio_str,  # Usa a string concatenada
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()

            # Adiciona uma mensagem de sucesso
            messages.add_message(request, constants.SUCCESS, 'Empresa adicionada com sucesso')

        except Exception as e:
            # Em caso de erro, uma mensagem de erro é adicionada
            messages.add_message(request, constants.ERROR, f'Erro interno do sistema: {str(e)}')

        # Redireciona de volta para a página de cadastro
        return redirect('/empresarios/cadastrar_empresa')