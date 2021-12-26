from flask import Blueprint, render_template, request, redirect, url_for
from models import Records
from .forms import Record_form
from app import data_base
from datetime import datetime


# блюпринт кусок изолированной функциональности
# record обработчик блюпринта
# аргументы: название блюпринта, приложение, и путь к шаблонам
records = Blueprint('records', __name__, template_folder='templates')



# страница представления контента(таблицы)
@records.route('/', methods=['POST', 'GET'])
def index():
    # добавление компании.
    if request.method == 'POST':
        company_name = request.form['company_name']
        short_info = request.form['short_info']
        long_info = request.form['long_info']
        try:
            record = Records(company_name=company_name, short_info=short_info, long_info=long_info)
            data_base.session.add(record)
            data_base.session.commit()
        except:
            data_base.session.rollback()
            print('Ошибка записи в базу данных.')
        return redirect( url_for('records.index') )
    form = Record_form()

    # принимаем в переменную page объект request со значениями из фронтенда
    page = request.args.get('page')
    # проверка значения переменной page, если переменная не пустая и является цифрой,
    # тогда приводим её к целочисленному типу, иначе страница будет первой
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    # в переменную search считывается то, что пользователь ввёл в строку поиска
    search = request.args.get('search')
    # Условие: если переменная search содержит что - либо, тогда у класса Records - модели запросов в б.д.
    # запрашиваем данные по сравниванию пользовательского запроса с именами компаний или содержанию краткого отчёта
    if search:
        records = Records.query.filter(Records.company_name.contains(search) | Records.short_info.contains(search))
    # иначе рендерится страница со всеми записями
    else:
        records = Records.query.order_by(Records.updated.desc())

    # records является объектом BaseQuery одним из его методов является paginate()
    # он принимает три именованых аргумента: 1- номер страницы
    # 2- количество записей из б.д. (сколько записей будет на каждой странице, установил пока что 5)
    # 3- error_out(можно не указывать явно) - установлен по умолчанию в True, сигнализирует об ошибках
    pages = records.paginate(page=page, per_page=5)
    return render_template('records/index.html', form=form, pages=pages)

# роут для формы редактирования записи
@records.route('/<slug>/edit/', methods=['POST', 'GET'])
def edit_record(slug):
    # получаем данные конкретной компании по слагу
    record = Records.query.filter(Records.slug == slug).first()
    # добавил отдельно обновление даты т.к. в формах дата не указывается, а генерится автоматически.
    record.updated = datetime.now()
    # при пост запросе получаем в форму html данные из объекта record
    if request.method == 'POST':
        form = Record_form(formdata=request.form, obj=record)
        # метод populate_obj заменяет новыми данными поля формы
        form.populate_obj(record)
        # комит для б.д. чтобы сохранить изменения
        data_base.session.commit()
        return redirect( url_for('records.record_detail', slug=record.slug) )

    form = Record_form(obj=record)
    return render_template('records/edit_record.html', record=record, form=form)


# поиск по слагу в б.д. <...> - это переменная динамической ссылки
@records.route('/<slug>')
def record_detail(slug):
    # query.filter может выдать запрос списком если нашлось несколько результатов,
    # так как слаг уникальный, то берём первый попавшийся результат ( метод .first() )
    record = Records.query.filter(Records.slug == slug).first()
    # возвращается страница с детальной информацией о компании
    return render_template('records/record_detail.html', record=record)