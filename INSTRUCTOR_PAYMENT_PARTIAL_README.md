# Багшийн цалинг зардлын гүйлгээнээс хэсэгчлэн төлөх - Хураангуй

## Асуудал:
Банкны зардлын гүйлгээнээс багшийн цалинтай хэсэгчлэн холбож болохгүй байсан. Урьд нь багшийн төлбөр бүхэлдээ нэг гүйлгээтэй холбогддог байв.

## Шийдэл:

### 1. Шинэ модель үүсгэсэн: `InstructorPaymentAllocation`
```python
class InstructorPaymentAllocation(models.Model):
    """Банкны зардлын гүйлгээг багшийн төлбөртэй холбох (хэсэгчлэн төлөх боломжтой)"""
    bank_transaction = ForeignKey(BankTransaction)
    instructor_payment = ForeignKey(MonthlyInstructorPayment)
    amount = DecimalField  # Төлсөн дүн
    notes = TextField
    created_at, created_by
```

### 2. MonthlyInstructorPayment моделд өөрчлөлт:
- **Нэмсэн талбар**: `paid_amount` - Одоогоор төлсөн нийт дүн
- **Нэмсэн методууд**:
  - `get_remaining_amount()` - Үлдсэн дүнг allocations-аас тооцоолно
  - `update_paid_amount()` - Allocations-аас дүн тооцоолж шинэчилнэ
  - `get_payment_status()` - "Төлөгдөөгүй" / "Хэсэгчлэн төлөгдсөн" / "Бүрэн төлөгдсөн"

### 3. BankTransaction.get_allocated_amount() шинэчилсэн:
Зардлын гүйлгээнээс:
```python
expense_total + instructor_payment_total  # Хоёуланг нь тооцоолно
```

### 4. Views өөрчлөлт (`bank_transaction_match`):
**Өмнөх байдал**:
```python
# Checkbox сонгоод бүхэл дүнг холбодог байв
payment.bank_transaction = transaction
payment.is_paid = True
```

**Шинэ байдал**:
```python
# Checkbox + дүн оруулж хэсэгчлэн холбоно
for payment_id, amount in zip(payment_ids, amounts):
    InstructorPaymentAllocation.objects.create(
        bank_transaction=transaction,
        instructor_payment=payment,
        amount=amount,  # Хэсэгчилсэн дүн
        notes=notes
    )
    payment.update_paid_amount()  # Автомат тооцоолно
```

### 5. Template өөрчлөлт (`bank_transaction_match.html`):
**Шинэ UI элементүүд**:
- Checkbox - Багш сонгох
- Дүн оруулах талбар (max=үлдсэн дүн)
- Тайлбар оруулах талбар
- Үлдсэн дүн харуулах
- JavaScript функц: `toggleInstructorPaymentAmount()`

### 6. Admin шинэчилсэн:
- `InstructorPaymentAllocation` бүртгэсэн
- `MonthlyInstructorPaymentAdmin`-д `paid_amount` readonly талбар нэмсэн

## Ажиллах механизм:

1. Зардлын гүйлгээ сонгох
2. "Багшийн цалин" төрөл сонгох
3. Төлөх багш нарын checkbox сонгох
4. Төлөх дүн оруулах (үлдсэн дүнээс хэтрэхгүй)
5. Тайлбар нэмэх (заавал биш)
6. Хадгалах
7. Систем автоматаар:
   - InstructorPaymentAllocation үүсгэнэ
   - payment.paid_amount шинэчилнэ
   - payment.is_paid шалгана (бүрэн төлөгдсөн эсэх)
   - transaction.status шинэчилнэ

## Давуу тал:

✅ Хэсэгчлэн төлөх боломжтой
✅ Олон гүйлгээнээс нэг багшид төлөх
✅ Дэлгэрэнгүй түүх хадгална
✅ Үлдсэн дүн автомат тооцогдоно
✅ Төлбөрийн төлөв автомат шинэчлэгдэнэ

## Файлууд:

### Migration:
- `0017_monthlyinstructorpayment_paid_amount_and_more.py`

### Шинэчилсэн файлууд:
- `models.py` - InstructorPaymentAllocation модель, paid_amount талбар, методууд
- `views.py` - bank_transaction_match логик өөрчилсөн
- `admin.py` - Шинэ админ класс
- `bank_transaction_match.html` - UI шинэчилсэн

### Тест скриптүүд:
- `test_instructor_payment_allocation.py` - Систем шалгах

## Жишээ ашиглалт:

```
Багшийн цалин: 100,000₮

Гүйлгээ #1: 50,000₮ төлөх
  → paid_amount = 50,000₮
  → get_remaining_amount() = 50,000₮
  → is_paid = False
  → status = "Хэсэгчлэн төлөгдсөн"

Гүйлгээ #2: 50,000₮ төлөх
  → paid_amount = 100,000₮
  → get_remaining_amount() = 0₮
  → is_paid = True
  → status = "Бүрэн төлөгдсөн"
```
