import gtk

class MenuManager:
	"""Menu handling class

	This class also supports local cache for menus used in 'Open With'
	menu.

	"""
	_named_items = {}
	_accel_group = None

	def __init__(self, application):
		self._application = application

		self._accel_group = gtk.AccelGroup()
		self._application.add_accel_group(self._accel_group)

	def _item_normal(self, item):
		"""Create normal menu item"""
		return gtk.MenuItem(label = item['label'], use_underline = True)

	def _item_checkbox(self, item):
		"""Create checkbox menu item"""
		active = item['active'] if 'active' in item else False
		result = gtk.CheckMenuItem(label = item['label'], use_underline = True)
		result.set_active(active)

		return result

	def _item_radio(self, item):
		"""Create radio menu item"""
		if item.has_key('group'):
			group = item['group']
		else:
			group = None

		return gtk.RadioMenuItem(group, item['label'], use_underline = True)

	def _item_separator(self, item):
		"""Create separator"""
		return gtk.SeparatorMenuItem()

	def _item_image(self, item):
		"""Create normal menu item with image"""
		result = gtk.ImageMenuItem()
		image = gtk.Image()

		if item.has_key('image'):
			image.set_from_icon_name(item['image'], gtk.ICON_SIZE_MENU)

		elif item.has_key('stock'):
			image.set_from_stock(item['stock'], gtk.ICON_SIZE_MENU)

		try:
			result.set_label(item['label'])
			result.set_use_underline(True)
		except:
			# walk-around for problems with GTK+ on windows systems
			item = gtk.Label(item['label'])
			item.set_use_underline(True)
			item.set_alignment(0, 0.5)

			result.add(item)

		result.set_image(image)

		return result

	def _open_with_callback(self, widget, data):
		"""Callback event for menu items from 'open with' menu"""
		self._application.associations_manager.open_file(data['selection'], application_info=data['application'])
	
	def _open_with_custom_callback(self, widget, data):
		"""Callback event for menu items from custom 'open with' menu"""
		self._application.associations_manager.open_file(data['selection'], exec_command=data['command'])

	def get_accel_group(self):
		"""Return accelerator group"""
		return self._accel_group

	def get_item_by_name(self, name):
		"""Get menu by specified name"""
		if name in self._named_items:
			result = self._named_items[name]
		else:
			result = None

		return result

	def get_items_for_type(self, mime_type, selection):
		"""Get list of MenuItems for specified mime type"""
		application_list = self._application.associations_manager.get_application_list_for_type(mime_type)
		result = []

		for application in application_list:
			# create menu item
			item = gtk.ImageMenuItem()
			item.set_label(application.name)
			item.set_always_show_image(True)

			# create new image
			if application.icon:
				image = gtk.Image()
				image.set_from_icon_name(application.icon, gtk.ICON_SIZE_MENU)
				item.set_image(image)

			data = {
				'selection': selection,
				'application': application
				}

			# connect signals
			item.connect('activate', self._open_with_callback, data)
			item.show()

			result.append(item)

		return result

	def get_custom_items_for_type(self, mime_type, selection):
		"""Get list of MenuItems for custom mime type"""
		result = []

		# local variable pointing to options
		associations = self._application.association_options

		# create custom open with menu
		if associations.has_section(mime_type):
			item_count = len(associations.options(mime_type)) / 2

			# add options for mime type
			for index in xrange(1, item_count + 1):
				name = associations.get(mime_type, 'name_{0}'.format(index))
				command = associations.get(mime_type, 'command_{0}'.format(index))

				# create menu item
				menu_item = gtk.MenuItem(name)
				menu_item.show()

				# prepare data for item
				data = {
					'selection': selection,
					'command': command
					}

				# connect an event
				menu_item.connect('activate', self._open_with_custom_callback, data)

				result.append(menu_item)

		return result

	def create_menu_item(self, item):
		"""Create new menu item from definition"""

		# ensure we don't get confused with item type
		if item.has_key('type'):
			item_type = item['type']
		else:
			item_type = 'item'

		# item type creator calls
		create_item_call = {
			'item': self._item_normal,
			'checkbox': self._item_checkbox,
			'radio': self._item_radio,
			'separator': self._item_separator,
			'image': self._item_image
		}

		# create item
		new_item = create_item_call[item_type](item)

		# if item has children then make submenu
		if item_type is not 'separator' and item.has_key('submenu'):
			submenu = gtk.Menu()
			submenu.set_accel_group(self._accel_group)

			for sub_item in item['submenu']:
				submenu.append(self.create_menu_item(sub_item))
			new_item.set_submenu(submenu)

		# connect signals
		if item.has_key('callback'):
			data = None
			if item.has_key('data'): data = item['data']

			if item_type is 'checkbox':
				# connect checkbox event
				new_item.connect('toggled', item['callback'], data)

			elif item_type is 'radio':
				# connect group changed event
				new_item.connect('group-changed', item['callback'], data)

			else:
				# connect on click event
				new_item.connect('activate', item['callback'], data)

		elif not item.has_key('callback') and not item.has_key('submenu'):
			# item doesn't have a callback, so we disable it
			new_item.set_sensitive(False)

		# if menu should be right aligned
		if item.has_key('right') and item['right']:
			new_item.set_right_justified(item['right'])

		# add item if name is specified
		if item.has_key('name'):
			self._named_items[item['name']] = new_item

		# set accelerator path
		if item.has_key('path'):
			new_item.set_accel_path(item['path'])

		# set initial item visibility
		visible = item['visible'] if item.has_key('visible') else True

		try:
			# try using newer method
			new_item.set_visible(visible)

		except AttributeError:
			# use legacy way of setting item visibility
			if visible: new_item.show()

		new_item.set_property('no-show-all', not visible)
		
		return new_item
