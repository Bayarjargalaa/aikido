from django import forms
from django.core.exceptions import ValidationError
from .models import BankTransaction, PaymentAllocation, Student, Instructor, ClassType, ClassSession
from datetime import date


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


# ============================================================================
# ДААЛГАВРЫН ШААРДЛАГА - 3 Form нэмэх
# ============================================================================

class StudentForm(forms.ModelForm):
    """Сурагч үүсгэх/засах форм"""
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'date_of_birth',
            'kyu_rank', 'dan_rank', 'current_rank_date',
            'monthly_fee', 'is_fee_exempt', 'fee_note',
            'class_types', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'Нэр'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'Овог'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': '99119911'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'example@email.com'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'kyu_rank': forms.Select(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'dan_rank': forms.Select(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'current_rank_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'monthly_fee': forms.NumberInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'is_fee_exempt': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'fee_note': forms.Textarea(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'rows': 3,
                'placeholder': 'Төлбөрийн тайлбар'
            }),
            'class_types': forms.CheckboxSelectMultiple(),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
    
    def clean(self):
        """Зэрэг цолын validation"""
        cleaned_data = super().clean()
        kyu_rank = cleaned_data.get('kyu_rank')
        dan_rank = cleaned_data.get('dan_rank')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        phone = cleaned_data.get('phone')
        
        # Кюү болон Дан зэрэг хоёуланг нь сонгож болохгүй
        if kyu_rank and dan_rank:
            raise ValidationError(
                'Кюү болон Дан зэрэг хоёуланг нь сонгож болохгүй. Нэгийг нь сонгоно уу.'
            )
        
        # Давхардсан бүртгэлээс сэргийлэх (овог + нэр + утас)
        if first_name and last_name and phone:
            # Хэрэв засч байгаа бол өөрийгөө оруулахгүй
            existing_query = Student.objects.filter(
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            # Хэрэв update (засах) хийж байгаа бол тухайн бүртгэлийг хасах
            if self.instance and self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)
            
            if existing_query.exists():
                existing_student = existing_query.first()
                raise ValidationError(
                    f'Ийм мэдээлэлтэй сурагч аль хэдийн бүртгэлтэй байна: '
                    f'{existing_student.last_name} {existing_student.first_name} ({existing_student.phone}). '
                    f'Бүртгэгдсэн огноо: {existing_student.enrollment_date.strftime("%Y-%m-%d")}'
                )
        
        return cleaned_data


class InstructorForm(forms.ModelForm):
    """Багш үүсгэх/засах форм"""
    
    class Meta:
        model = Instructor
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'kyu_rank', 'dan_rank', 'current_rank_date',
            'allowed_class_types', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'Нэр'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'Овог'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': '99119911'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 w-full',
                'placeholder': 'example@email.com'
            }),
            'kyu_rank': forms.Select(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'dan_rank': forms.Select(attrs={
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'current_rank_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'allowed_class_types': forms.CheckboxSelectMultiple(),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
    
    def clean(self):
        """Зэрэг цолын validation"""
        cleaned_data = super().clean()
        kyu_rank = cleaned_data.get('kyu_rank')
        dan_rank = cleaned_data.get('dan_rank')
        
        # Багш нь дан зэрэгтэй байх ёстой
        if not dan_rank and not kyu_rank:
            raise ValidationError('Багш заавал зэрэг цолтой байх ёстой.')
        
        # Кюү болон Дан зэрэг хоёуланг нь сонгож болохгүй
        if kyu_rank and dan_rank:
            raise ValidationError(
                'Кюү болон Дан зэрэг хоёуланг нь сонгож болохгүй. Нэгийг нь сонгоно уу.'
            )
        
        return cleaned_data


class AttendanceRecordForm(forms.Form):
    """Ирц бүртгэх форм"""
    
    session_date = forms.DateField(
        label='Хичээлийн огноо',
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class_type = forms.ModelChoiceField(
        queryset=ClassType.objects.all(),
        label='Ангийн төрөл',
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    start_time = forms.TimeField(
        label='Эхлэх цаг',
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    end_time = forms.TimeField(
        label='Дуусах цаг',
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    def clean(self):
        """Цагийн validation"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('Эхлэх цаг дуусах цагаас өмнө байх ёстой.')
        
        return cleaned_data
