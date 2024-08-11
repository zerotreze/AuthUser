from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import constants
from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento

def cadastrar_empresa(request):
    if not request.user.is_authenticated:
      return redirect('/usuarios/logar')

    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', {
           'tempo_existencia': Empresas.TEMPO_EXISTENCIA_CHOICES,
           'areas': Empresas.AREA_CHOICES
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
    
def listar_empresas(request):
 if not request.user.is_authenticated:
    return redirect('/usuarios/logar')
 if request.method == "GET":
    #REALIZAR FILTROS DAS EMPRESAS
    empresas = Empresas.objects.filter(user=request.user)
    return render(request, 'listar_empresas.html', {'empresas': empresas})

def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
    
    percentual_vendido = 0
    total_captado = 0  # Initialize total_captado

    for pi in proposta_investimentos:
        if pi.status == 'PA':
            percentual_vendido += pi.percentual
            total_captado += pi.valor  # Accumulate total_captado if necessary

    # Add additional logic or context preparation as needed
    valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0 
    return render(request, 'empresa.html', {
        'empresa': empresa,
        'percentual_vendido': percentual_vendido,
        'total_captado': total_captado,
        'valuation_atual': valuation_atual,
        # Other context variables
    })

   
def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    
    if extensao[1] != 'pdf':
        messages.add_message(request, constants.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/empresa/{id}')

    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{id}')



    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}') # type: ignore

def excluir_dc(request, id):
    documento = Documento.objects.get(id=id)
    if documento.empresa.user != request.user:
       messages.add_message(request, constants.ERROR, "Esse documento não é seu")
       return redirect(f'/empresarios/empresa/{empresa.id}')
    
 
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}') # type: ignore

def add_metrica(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')

    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()
    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}') # type: ignore

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)
    
    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada')
        pi.status = 'PR'
    
    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')
