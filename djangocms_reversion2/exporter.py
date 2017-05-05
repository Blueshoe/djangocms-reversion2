# -*- coding: utf-8 -*-
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from sekizai.context import SekizaiContext
# from xlsxwriter.workbook import Workbook
# from decimal import Decimal as D
# from django.utils.translation import ugettext as _
# from djangocms_reversion2.utils import PageRevisionComparator
#
#
# class ReportXLSXFormatter(object):
#     def filename(self, **kwargs):
#         page_id = kwargs.get('page_id')
#         language = kwargs.get('language')
#         return 'audit-trail-page-{}-{}.xlsx'.format(page_id, language)
#
#     def get_xlsx_writer(self, response, **kwargs):
#         return Workbook(response, {'in_memory': True})
#
#     def generate_xlsx(self, response, data, **kwargs):
#         """writes a standard xlsx into the response"""
#         header_row = data.get("header_row")
#         rows = data.get("rows")
#         workbook = self.get_xlsx_writer(response)
#         worksheet = workbook.add_worksheet()
#         bold = workbook.add_format({'bold': True})
#         for i, column in enumerate(header_row):
#             worksheet.write(0, i, enc(column, encoding='utf-8').decode('utf-8'), bold)
#         for y, row in enumerate(rows):
#             for x, column in enumerate(row):
#                 worksheet.write(y+1, x, enc(column, encoding='utf-8').decode('utf-8'))
#         workbook.close()
#
#     def generate_response(self, objects, **kwargs):
#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename=%s' \
#             % self.filename(**kwargs)
#         self.generate_xlsx(response, objects, **kwargs)
#         return response
#
#     def generate_data(self, request, queryset):
#         data = []
#         for rev in queryset.all():
#             prc = PageRevisionComparator(rev, request=request)
#             slot_html = {slot: html for slot, html in prc.slot_html.items() if slot in prc.changed_slots}
#
#             context = SekizaiContext({'slot_html': slot_html})
#             html = str(render_to_string('admin/audit_trail.html', context)
#                        .encode('utf-8', errors='replace')).decode('utf-8')
#             data.append([rev.revision.id, rev.revision.date_created, rev.revision.user.username, rev.revision.comment,
#                          html])
#         return data
#
#     def get_title_row(self):
#         return [_('Revision ID'), _('Date'), _('By'), _('Comment'), _('HTML Content')]
#
#     def get_download_response(self, request, queryset, language=''):
#         header = self.get_title_row()
#         data = self.generate_data(request, queryset)
#         return self.generate_response({'header_row': header, 'rows': data}, page_id=request.rev_page.id,
#                                       language=language)
#
#
# def enc(st, encoding='latin1'):
#     """
#     encodes a string with the given encoding
#     calls the serializer before
#     :param st:
#     :param encoding:
#     :return:
#     """
#     if st is None:
#         st = ''
#     try:
#         string = serialize_field(st)
#     except:
#         raise TypeError
#     return string.encode(encoding, 'replace')
#
#
# def serialize_field(field, fallback=None):
#     """
#     tries to serialize any Model
#     :param fallback: fallback return value
#     :param field: from _meta of a model
#     :return: string
#     """
#
#     serializers = {
#         'unicode': lambda f: f,
#         'int': lambda f: str(f),
#         'float': lambda f: str(f).replace('.', ','),
#         'str': lambda f: f,
#         'datetime': lambda f: f.strftime('%d.%m.%Y %H:%M'),
#         'bool': lambda f: 'WAHR' if f else 'FALSCH',
#         'Decimal': lambda f: str(f.quantize(D('0.01'))).replace('.', ','),
#         'NoneType': lambda f: serialize_field(''),
#     }
#
#     type_name = type(field).__name__
#
#     if type_name in serializers:
#         return serializers[type_name](field)
#     elif not fallback:
#         return "<SERIALIZING MISSING {}>".format(type_name)
#     else:
#         return fallback
