from django import forms
from .models import BankTransaction, PaymentAllocation, Student


class BankTransactionUploadForm(forms.Form):
    """Excel файл импортлох форм - Монгол банкны формат"""
    
    BANK_FORMAT_CHOICES = [
        ('custom', 'Өөрийн тохиргоо'),
        ('standard', 'Стандарт формат (Гүйлгээний огноо, Кредит гүйлгээ, ...)'),
    ]
    
    excel_file = forms.FileField(
        label='Excel файл',
        help_text='Банкны гүйлгээний мэдээлэл агуулсан Excel файл (.xlsx, .xls)',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
            'accept': '.xlsx,.xls'
        })
    )
    
    bank_format = forms.ChoiceField(
        label='Файлын формат',
        choices=BANK_FORMAT_CHOICES,
        initial='standard',
        widget=forms.RadioSelect(attrs={
            'class': 'format-choice'
        })
    )
    
    # Стандарт банкны баганы нэрс
    date_header = forms.CharField(
        label='Огнооны баганы толгой',
        initial='Гүйлгээний огноо',
        help_text='Excel-ийн толгой мөрөнд байгаа огнооны баганы нэр',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 header-field',
        })
    )
    
    amount_header = forms.CharField(
        label='Дүнгийн баганы толгой',
        initial='Кредит гүйлгээ',
        help_text='Орлогын (кредит) баганы нэр',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 header-field',
        })
    )
    
    description_header = forms.CharField(
        label='Утгын баганы толгой',
        initial='Гүйлгээний утга',
        help_text='Гүйлгээний утга баганы нэр',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 header-field',
        })
    )
    
    payer_header = forms.CharField(
        label='Төлөгчийн баганы толгой',
        initial='Харьцсан данс',
        required=False,
        help_text='Харьцсан данс/төлөгчийн нэр баганы нэр',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 header-field',
        })
    )
    
    # Manual багана сонголт (custom формат)
    date_column = forms.CharField(
        label='Огнооны багана',
        initial='A',
        required=False,
        help_text='Огноо байгаа баганы үсэг (жнь: A)',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 column-field',
            'placeholder': 'A'
        })
    )
    
    amount_column = forms.CharField(
        label='Дүнгийн багана',
        initial='D',
        required=False,
        help_text='Кредит гүйлгээний баганы үсэг',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 column-field',
            'placeholder': 'D'
        })
    )
    
    description_column = forms.CharField(
        label='Гүйлгээний утгын багана',
        initial='F',
        required=False,
        help_text='Гүйлгээний утга байгаа баганы үсэг',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 column-field',
            'placeholder': 'F'
        })
    )
    
    payer_name_column = forms.CharField(
        label='Төлөгчийн нэрийн багана',
        initial='G',
        required=False,
        help_text='Харьцсан данс байгаа баганы үсэг',
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 column-field',
            'placeholder': 'G'
        })
    )
    
    start_row = forms.IntegerField(
        label='Эхлэх мөр',
        initial=2,
        min_value=1,
        help_text='Өгөгдөл эхлэх мөрийн дугаар (толгой мөр орхих)',
        widget=forms.NumberInput(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '2'
        })
    )


class PaymentAllocationForm(forms.ModelForm):
    """Төлбөр хуваарилах форм"""
    
    class Meta:
        model = PaymentAllocation
        fields = ['student', 'payment_month', 'amount', 'notes']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full'
            }),
            'payment_month': forms.DateInput(attrs={
                'type': 'month',
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active students
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
        self.fields['notes'].required = False
