# Багш нарын эрхийн тохиргоо - Хураангуй

## Хийсэн өөрчлөлтүүд:

### 1. Model (models.py)
- `Instructor` моделд `allowed_class_types` ManyToMany талбар нэмсэн
- Энэ талбар нь багшийн харах эрхтэй ангиудыг тодорхойлно
- Хоосон байвал бүх ангийг харна

### 2. Views (views.py)
- `instructor_payment_list`: Багш нарын төлбөрийг харуулахдаа allowed_class_types-аар шүүнэ
- `monthly_payment_report`: Төлбөрийн тайланг харуулахдаа allowed_class_types-аар шүүнэ
- `instructor_create`: Шинэ багш үүсгэхэд allowed_class_types тохируулна
- `instructor_edit`: Багшийн мэдээлэл засахдаа allowed_class_types шинэчилнэ

### 3. Templates (instructor_form.html)
- Ангиудыг сонгох checkbox нэмсэн
- Хэрэглэгчид ойлгомжтой тайлбар нэмсэн

### 4. Admin (admin.py)
- InstructorAdmin-д filter_horizontal нэмж, админ интерфэйст ангиудыг сонгох боломжтой болгосон
- "Эрхийн тохиргоо" гэсэн fieldset нэмсэн

### 5. Migration
- 0016_instructor_allowed_class_types.py migration үүсгэсэн

## Тохируулсан эрхүүд:

1. **Галбадрах багш** - Хүүхдийн ангийн төлбөр харна
2. **Амгаланбаяр багш** - Өглөөний ангийн төлбөр харна  
3. **Баясгалан багш** - Бүх ангийн төлбөр харна (Өглөө + Орой + Хүүхэд)
4. **Алтанбагана багш** - Бүх ангийн төлбөр харна (хоосон)

## Ажиллах механизм:

- Багш нэвтрэх үед системд instructor профайлтай эсэхийг шалгана
- Staff эсэх (is_staff=False) шалгана
- Instructor бол зөвхөн өөрийн төлбөрүүдийг харна
- allowed_class_types-д ангиуд байвал зөвхөн тэдгээрийг харна
- allowed_class_types хоосон бол бүх ангийг харна
- Staff хэрэглэгч бол бүх багшийн бүх төлбөрийг харна

## Ашигласан файлууд:

- `setup_instructor_permissions.py` - Эхний тохиргоог хийх скрипт
- `test_instructor_permissions.py` - Эрхүүд зөв ажиллаж байгааг шалгах скрипт
