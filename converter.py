from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QKeySequence
from pathlib import PurePath, Path
from os import path
from PIL import Image
from PIL.ExifTags import TAGS

class ImageItem(QtWidgets.QTreeWidgetItem):
	def __init__(self, parent, path):
		self.file = PurePath(path)
		super().__init__(parent, [self.file.name, self.file.suffix.upper()])


class ImageList(QtWidgets.QTreeWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setHeaderLabels(["Name", "Current Extension"])
		self.setAcceptDrops(True)
		self.resize(600, 600)
		self.files = []
		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls:
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
			for url in event.mimeData().urls():
				if url.isLocalFile():
					self.add_file(url.toLocalFile())
				else:
					self.add_file(url.toString())
		else:
			event.ignore()
	
	def add_file(self, path):
		item = ImageItem(self, path)
		self.files.append(item.file)
		self.addTopLevelItem(item)
		self.resizeColumnToContents(0)

	def clear(self):
		self.files = []
		super().clear()
	
	def remove(self):
		for i in self.selectedItems():
			self.takeTopLevelItem(self.indexOfTopLevelItem(i))
			self.files.remove(i.file)



class ImageConverter(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.open_files_dialog = QtWidgets.QFileDialog(self, "Images", str(Path.home()), "Images (*.png *.jpg *.jpeg *.gif *.webp *.bpm *.tiff *.ico)")
		self.destination_dir_dialog = QtWidgets.QFileDialog(self, "Select Directory", str(Path.home()))
		# self.initUI()

	def initUI(self):
		self.resize(800, 500)
		self.setWindowTitle("Image Converter")

		self.central_layout = QtWidgets.QVBoxLayout(self)
		self.central_layout.setContentsMargins(5, 5, 5, 5)
		self.central_layout.setSpacing(4)

		self.image_list = ImageList(self)
		self.image_list.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding))
		self.image_list.setSortingEnabled(True)

		# image options
		self.image_options = QtWidgets.QTabWidget(self)
		self.image_options.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum))

		# SCALE TAB
		self.scale_tab = QtWidgets.QWidget()
		self.scale_vlayout = QtWidgets.QVBoxLayout(self.scale_tab)
		self.scale_type = QtWidgets.QComboBox(self.scale_tab)
		self.scale_type.addItems(["Scale Image", "Image Dimensions", "Width", "Height", "Longest Size"])
		self.scale_widgets_layout = QtWidgets.QVBoxLayout()
		self.scale_vlayout.addWidget(self.scale_type)
		self.scale_vlayout.addLayout(self.scale_widgets_layout)

		# WATERMARK TAB
		self.watermark_tab = QtWidgets.QWidget()
		self.watermark_flayout = QtWidgets.QFormLayout(self.watermark_tab)

		self.watermark_text = QtWidgets.QLineEdit(self.watermark_tab)
		self.font_combobox  = QtWidgets.QFontComboBox(self.watermark_tab)
		self.color_btn      = QtWidgets.QPushButton("#ffffff", self.watermark_tab)
		self.visibility     = QtWidgets.QSlider(self.watermark_tab)
		self.rotation       = QtWidgets.QSlider(self.watermark_tab)
		self.padding        = QtWidgets.QSlider(self.watermark_tab)
		self.size           = QtWidgets.QSlider(self.watermark_tab)
		self.tile_checkbox  = QtWidgets.QCheckBox("Tiled", self.watermark_tab)

		self.visibility.setOrientation(QtCore.Qt.Horizontal)
		self.rotation.setOrientation(QtCore.Qt.Horizontal)
		self.padding.setOrientation(QtCore.Qt.Horizontal)
		self.size.setOrientation(QtCore.Qt.Horizontal)

		self.watermark_flayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Text", self.watermark_tab))
		self.watermark_flayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.watermark_text)
		self.watermark_flayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Font", self.watermark_tab))
		self.watermark_flayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.font_combobox)
		self.watermark_flayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Color", self.watermark_tab))
		self.watermark_flayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.color_btn)
		self.watermark_flayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Visibility", self.watermark_tab))
		self.watermark_flayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.visibility)
		self.watermark_flayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Rotation", self.watermark_tab))
		self.watermark_flayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.rotation)
		self.watermark_flayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Padding", self.watermark_tab))
		self.watermark_flayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.padding)
		self.watermark_flayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.size)
		self.watermark_flayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.tile_checkbox)
		self.watermark_flayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Size", self.watermark_tab))

		# CROP TAB
		self.crop_tab = QtWidgets.QWidget()
		self.crop_flayout = QtWidgets.QFormLayout(self.crop_tab)
		self.crop_pos_x = QtWidgets.QSpinBox(self.crop_tab)
		self.crop_pos_y = QtWidgets.QSpinBox(self.crop_tab)
		self.crop_area_w = QtWidgets.QSpinBox(self.crop_tab)
		self.crop_area_h = QtWidgets.QSpinBox(self.crop_tab)

		self.crop_flayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Crop Position X", self.crop_tab))
		self.crop_flayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.crop_pos_x)
		self.crop_flayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Crop Position Y", self.crop_tab))
		self.crop_flayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.crop_pos_y)
		self.crop_flayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Crop area W", self.crop_tab))
		self.crop_flayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.crop_area_w)
		self.crop_flayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Crop area H", self.crop_tab))
		self.crop_flayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.crop_area_h)

		# ADD TABS
		self.image_options.addTab(self.scale_tab, "Scale")
		self.image_options.addTab(self.watermark_tab, "Watermark")
		self.image_options.addTab(self.crop_tab, "Crop")

		############################
		# self.image_options.hide()
		############################

		# CONVERT OPTIONS
		self.convert_flayout = QtWidgets.QFormLayout()
		self.convert_format = QtWidgets.QComboBox(self)
		self.convert_format.addItems(["JPEG", "WEBP", "PNG", "GIF", "BMP", "TIFF", "ICO"])

		self.quality = QtWidgets.QSlider(self)
		self.quality.setOrientation(QtCore.Qt.Horizontal)

		self.detination_dir = str(Path.home())
		self.detination_dir_input = QtWidgets.QLineEdit(self)
		self.detination_dir_btn = QtWidgets.QPushButton(self.detination_dir, self)
		# QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

		self.convert_flayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Destination directory", self))
		# self.convert_flayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.detination_dir_input)
		self.convert_flayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.detination_dir_btn)
		self.convert_flayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Convert to", self))
		self.convert_flayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.convert_format)
		self.convert_flayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, QtWidgets.QLabel("Image Quality", self))
		self.convert_flayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.quality)

		# PROGRESS BAR
		self.progressbar = QtWidgets.QProgressBar(self)
		self.progressbar.setValue(0)
		self.progressbar.setAlignment(QtCore.Qt.AlignCenter)

		# BUTTONS
		self.cancel_btn = QtWidgets.QPushButton(QtGui.QIcon.fromTheme("window-close"), "Cancel", self)
		self.execute_btn = QtWidgets.QPushButton("Execute", self)

		self.bottom_btn_hlayout = QtWidgets.QHBoxLayout()
		self.bottom_btn_hlayout.addStretch()
		self.bottom_btn_hlayout.addWidget(self.cancel_btn)
		self.bottom_btn_hlayout.addWidget(self.execute_btn)

		# MAIN LAYOUT WIDGETS
		self.central_layout.addWidget(self.image_list)
		self.central_layout.addWidget(self.image_options)
		self.central_layout.addLayout(self.convert_flayout)
		self.central_layout.addWidget(self.progressbar)
		self.central_layout.addLayout(self.bottom_btn_hlayout)

	def open_files(self):
		files, _ = self.open_files_dialog.getOpenFileNames()
		for f in files:
			self.image_list.add_file(f)
		# self.image_list.addItems(files)

	def remove_files(self):
		self.image_list.remove()

	def clear_files(self):
		self.image_list.clear()
	
	def get_destination(self):
		self.detination_dir = self.destination_dir_dialog.getExistingDirectory()
		self.detination_dir_btn.setText(self.detination_dir)

	def execute(self):
		files = self.image_list.files
		suffix = "." + self.convert_format.currentText().lower()
		file_num = len(files)

		for i, f in enumerate(files):
			new_file = f.with_suffix(suffix).name
			new_path = path.join(self.detination_dir, new_file)
			print(f, " -> ", new_path)
			try:
				img = Image.open(str(f))
				img.save(new_path)
			except Exception as e:
				print(e)
			self.progressbar.setValue(i * 100/file_num)
		
		# reset
		self.progressbar.setValue(0)

	def open_preview(self):
		if len(self.image_list.selectedItems()) == 0:
			return
		
		item = self.image_list.selectedItems()[0]
		# do something when a single item is selected
		try:
			image = Image.open(str(item.file))
			exifdata = image.getexif()
			# iterating over all EXIF data fields
			for tag_id in exifdata:
				# get the tag name, instead of human unreadable tag id
				tag = TAGS.get(tag_id, tag_id)
				data = exifdata.get(tag_id)
				# decode bytes 
				if isinstance(data, bytes):
					data = data.decode()
				print(f"{tag:25}: {data}")
		except Exception as e:
			print(e)

	def make_connections(self):
		self.detination_dir_btn.clicked.connect(self.get_destination)
		self.execute_btn.clicked.connect(self.execute)
		self.image_list.itemSelectionChanged.connect(self.open_preview)


class ICWindow(QtWidgets.QMainWindow, ImageConverter):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.make_connections()

	def initUI(self):
		super().initUI()
		self.setWindowTitle("Image Converter")

		# menubar
		self.menubar = QtWidgets.QMenuBar(self)
		self.init_menubar()
		self.setMenuBar(self.menubar)

		# toolbar
		self.toolbar = QtWidgets.QToolBar(self)
		self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
		self.init_toolbar()

		# statusbar
		self.statusbar = QtWidgets.QStatusBar(self)
		self.setStatusBar(self.statusbar)
		self.statusbar.showMessage("Status bar")

		central_widget = QtWidgets.QWidget()
		self.setCentralWidget(central_widget)
		central_widget.setLayout(self.central_layout)

	def make_connections(self):
		super().make_connections()
	
	def init_menubar(self):
		self.file_menu = self.menubar.addMenu("File")
		self.edit_menu = self.menubar.addMenu("Edit")

		self.action_add    = QtWidgets.QAction(QtGui.QIcon.fromTheme("list-add"), "Open files", triggered=self.open_files, shortcut="Ctrl+o")
		self.action_remove = QtWidgets.QAction(QtGui.QIcon.fromTheme("list-remove"), "Remove", triggered=self.remove_files, shortcut="Ctrl+r")
		self.action_clear  = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-delete"), "Clear", triggered=self.clear_files, shortcut="Ctrl+l")

		self.file_menu.addAction(self.action_add)
		self.file_menu.addAction(self.action_remove)
		self.file_menu.addAction(self.action_clear)
	
	def init_toolbar(self):
		# self.toolbar.addSeparator()
		self.toolbar.addAction(self.action_add)
		self.toolbar.addAction(self.action_remove)
		self.toolbar.addAction(self.action_clear)






import sys

# Application
app = QtWidgets.QApplication(sys.argv)
gui = ICWindow()

images_dir = "/home/matej/Desktop/tmp_images/"
for i in range(10):
	f = images_dir + f"image_{i}.jpg"
	gui.image_list.add_file(f)

gui.show()
sys.exit(app.exec_())