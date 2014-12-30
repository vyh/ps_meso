from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

def home(request):
    return render(request, 'home.html', {'right_now':datetime.utcnow()})

@csrf_protect
def psmeso(request):
    from forms import mesosticForm
    #c = {}
    if request.method == 'POST':
        form = mesosticForm(request.POST)
        if form.is_valid():
            ORACLE = form.cleaned_data['ORACLE']
            SEED = form.cleaned_data['SEED']
            ITERS = form.cleaned_data['ITERS']
            ODDS = int(form.cleaned_data['ODDS'])
            strippunct = form.cleaned_data['strippunct']
            import psMesoWeb
            message, mesostic = psMesoWeb.mesosticize(ORACLE, SEED, ITERS, ODDS,
                                                      strippunct)
            return render_to_response('mesosticize.html',
                                     {'message': message, 'mesostic': mesostic})
    else:
        form = mesosticForm()
    return render(request, 'ps.html', {'form': form})

def aboutmeso(request):
    return render(request, 'aboutmeso.html')

def mesosticize(request):
    return render(request, 'mesosticize.html')

def redirToPS(request):
    return HttpResponseRedirect('/psmeso/')