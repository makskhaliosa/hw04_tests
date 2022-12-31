from django.core.paginator import Paginator


def pagination(request, post_list, items_num):
    # Показывать по items_num записей на странице.
    paginator = Paginator(post_list, items_num)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    return page_obj
