from django import forms

class mesosticForm(forms.Form):
    ORACLE = forms.CharField(label='Source text',
                             widget=forms.Textarea)
    SEED = forms.CharField(label='Spine text',
                           initial='Cage',
                           max_length=100,
                           widget=forms.TextInput(attrs={'size': '40'}))
    ITERS = forms.IntegerField(label='How many times should the spine text '+\
                                     'appear (1 - 99)?',
                               initial='1',
                               min_value=1,
                               max_value=99,
                               widget=forms.TextInput(attrs={'size': '3'}))
    ODDS = forms.ChoiceField(label='How sparse should the wing text be '+\
                                   '(# words between spine words)?\n',
                             choices=((2, 'Normal'),
                                      (4, 'Sparse'),
                                      (8, 'Very Sparse')))
    strippunct = forms.BooleanField(label='Strip punctuation?', required=False)