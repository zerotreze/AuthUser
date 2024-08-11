from django.shortcuts import render, redirect
from empresarios.models import Empresas, Documento
from django.db import models
from django.contrib.auth.models import User
from .models import PropostaInvestimento, Empresas
from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse, Http404

def sugestao(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    areas = Empresas.AREA_CHOICES
    if request.method == "GET":
        return render(request, 'sugestao.html', {'areas': areas})
    elif request.method == "POST":
        tipo = request.POST.get('tipo')
        area = request.POST.getlist('area')
        valor = request.POST.get('valor')
        
        if tipo == 'C':
            empresas = Empresas.objects.filter(tempo_existencia='+5').filter(estagio="E")
        elif tipo == 'D':
            empresas = Empresas.objects.filter(tempo_existencia__in=['-6', '+6', '+1']).exclude(estagio="E")
            # + 1 tipo generico:MEDIANO

        empresas = empresas.filter(area__in=area)

        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            print(empresa.nome,percentual)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)
        
        return render(request, 'sugestao.html', {'empresas': empresas_selecionadas, 'areas': areas})

def ver_empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)

    percentual_vendido = 0
    for pi in proposta_investimentos:
        if pi.status == 'PA':
            percentual_vendido += pi.percentual

    limiar = (80 * empresa.percentual_equity) / 100
    concretizado = False
    if percentual_vendido >= limiar:
        concretizado = True

    # Ensure `perc` is defined or used correctly
    perc = percentual_vendido  # Example: initializing `perc`

    return render(request, 'ver_empresa.html', {
        'empresa': empresa,
        'percentual_vendido': percentual_vendido,
        'concretizado': concretizado,
        'perc': perc,  # Ensure `perc` is passed to the template if needed
        # Other context variables
    })

def realizar_proposta(request, id):
    # Retrieve and clean input values
    valor_str = request.POST.get('valor').strip()
    percentual_str = request.POST.get('percentual').strip()

    # Convert to float and handle potential conversion errors
    try:
        valor = float(valor_str)
        percentual = float(percentual_str)
    except ValueError:
        messages.add_message(request, constants.ERROR, 'Valores inválidos fornecidos.')
        return redirect(f'/investidores/ver_empresa/{id}')

    empresa = Empresas.objects.get(id=id)

    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa, status='PA')
    total = sum(pa.percentual for pa in propostas_aceitas)

    if total + percentual > empresa.percentual_equity:
        messages.add_message(request, constants.WARNING, 'O percentual solicitado ultrapassa o percentual máximo.')
        return redirect(f'/investidores/ver_empresa/{id}')

    # Debug: print types and values
    print(f"valor (float): {valor}, type: {type(valor)}")
    print(f"percentual (float): {percentual}, type: {type(percentual)}")
    print(f"empresa.valuation: {empresa.valuation}, type: {type(empresa.valuation)}")

    # Ensure empresa.valuation is a float or integer
    if isinstance(empresa.valuation, str):
        empresa_valuation = float(empresa.valuation)
    else:
        empresa_valuation = empresa.valuation

    valuation = (100 * valor) / percentual

    if valuation < (empresa_valuation / 2):
        messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo R${empresa_valuation / 2}')
        return redirect(f'/investidores/ver_empresa/{id}')

    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user,
    )
    pi.save()

    # messages.add_message(request, constants.SUCCESS, 'Proposta enviada com sucesso')
    return redirect(f'/investidores/assinar_contrato/{pi.id}')


def assinar_contrato(request, id):
    pi = PropostaInvestimento.objects.get(id=id)
    
    if pi.status != "AS":
        raise Http404()
    
    if request.method == "GET":
        return render(request, 'assinar_contrato.html', {'pi': pi})
    
    elif request.method == "POST":
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        
        # Debug print to check if files are being received
        print(request.FILES)

        # Update proposal with files and change status
        pi.selfie = selfie
        pi.rg = rg
        pi.status = 'PE'
        pi.save()
        
        # Add success message and redirect
        messages.add_message(request, constants.SUCCESS, 'Contrato assinado com sucesso, sua proposta foi enviada à empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')



