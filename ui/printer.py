from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtCore import QDateTime, Qt, QRect
from PyQt5.QtGui import QPainter, QFont
import os


def _render_table_on_printer(table_widget, printer, header_lines=None, footer_text=None):
	painter = QPainter(printer)

	# Ensure A4 if possible
	try:
		printer.setPageSize(QPrinter.A4)
	except Exception:
		try:
			from PyQt5.QtGui import QPageSize
			printer.setPageSize(QPageSize(QPageSize.A4))
		except Exception:
			pass

	page_rect = printer.pageRect()
	left = page_rect.left() + 40
	top = page_rect.top() + 60
	right = page_rect.right() - 40
	bottom = page_rect.bottom() - 60
	content_width = right - left

	cols = table_widget.columnCount()
	header = table_widget.horizontalHeader()
	# Use header section sizes to keep relative widths; fall back to equal widths
	try:
		col_sizes = [header.sectionSize(i) for i in range(cols)]
	except Exception:
		col_sizes = [1] * cols
	total = sum(col_sizes) if sum(col_sizes) > 0 else cols
	col_widths = [max(40, int(content_width * (size / total))) for size in col_sizes]

	font = QFont('Arial', 16)
	header_font = QFont('Arial', 18)
	header_font.setBold(True)
	painter.setFont(font)
	fm = painter.fontMetrics()
	row_height = fm.height() + 14

	y = top

	def draw_page_header():
		nonlocal y
		painter.setFont(header_font)
		title = header_lines[0] if header_lines else ''
		if title:
			painter.drawText(QRect(left, y, content_width, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, title)
			y += fm.height() + 10
		# Draw column headers in French
		painter.setFont(header_font)
		x = left
		french_headers = ['Nom du Produit', 'Catégorie', 'Référence', 'Quantité', "Date d'entrée", 'Date de sortie', 'Actions']
		for i in range(cols):
			text = french_headers[i] if i < len(french_headers) else ''
			rect = QRect(x, y, col_widths[i], row_height)
			painter.drawRect(rect)
			painter.drawText(rect.adjusted(4, 0, -4, 0), Qt.AlignLeft | Qt.AlignVCenter, text)
			x += col_widths[i]
		y += row_height
		painter.setFont(font)

	draw_page_header()

	rows = table_widget.rowCount()
	for r in range(rows):
		if y + row_height > bottom:
			printer.newPage()
			y = top
			draw_page_header()
		x = left
		for c in range(cols):
			item = table_widget.item(r, c)
			text = item.text() if item else ''
			rect = QRect(x, y, col_widths[c], row_height)
			painter.drawRect(rect)
			painter.drawText(rect.adjusted(4, 0, -4, 0), Qt.AlignLeft | Qt.AlignVCenter, text)
			x += col_widths[c]
		y += row_height

	# Footer
	if footer_text:
		painter.drawText(QRect(left, bottom + 10, content_width, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, footer_text)
	painter.end()


def preview_widget(widget, parent=None, title='Preview'):
	printer = QPrinter(QPrinter.HighResolution)
	preview = QPrintPreviewDialog(printer, parent)

	def paint(pr):
		if hasattr(widget, 'rowCount') and hasattr(widget, 'columnCount'):
			# table-like widget
			_render_table_on_printer(widget, pr)
		else:
			painter = QPainter(pr)
			widget.render(painter)
			painter.end()

	preview.paintRequested.connect(paint)
	preview.exec_()


def save_table_to_pdf(table_widget, pdf_path, header_lines=None, footer_text=None):
		printer = QPrinter(QPrinter.HighResolution)
		printer.setOutputFormat(QPrinter.PdfFormat)
		printer.setOutputFileName(pdf_path)
		# Always use French headers for PDF export
		_render_table_on_printer(table_widget, printer, header_lines=['Inventaire des produits'], footer_text=footer_text)


def print_table(table_widget, parent=None, header_lines=None, footer_text=None):
		printer = QPrinter(QPrinter.HighResolution)
		dialog = QPrintDialog(printer, parent)
		if dialog.exec_() == QPrintDialog.Accepted:
			# Always use French headers for print
			_render_table_on_printer(table_widget, printer, header_lines=['Inventaire des produits'], footer_text=footer_text)

