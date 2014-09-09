import gtk
import os

from widgets.settings_page import SettingsPage

DEFAULT_NAME = _('Default')

main_window = None
options = None
item_sessions = None
config = None

class SessionsOptions(SettingsPage):
	"""Sessions options extension class"""

	def __init__(self, parent, application):
		SettingsPage.__init__(self, parent, application, 'sessions', _('Sessions'))
		self._tab_options = application.tab_options

		# create list box
		container = gtk.ScrolledWindow()
		container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		container.set_shadow_type(gtk.SHADOW_IN)

		self._session_store = gtk.ListStore(str, str, int)

		self._treeview = gtk.TreeView()
		self._treeview.set_model(self._session_store)
		self._treeview.set_rules_hint(True)

		cell_name = gtk.CellRendererText()
		cell_name.set_property('editable', True)
		cell_name.set_property('mode', gtk.CELL_RENDERER_MODE_EDITABLE)
		cell_name.connect('edited', self._handle_edited_name, 0)

		col_name = gtk.TreeViewColumn(_('Name'), cell_name, text=0)
		col_name.set_min_width(200)
		col_name.set_resizable(True)

		self._treeview.append_column(col_name)
		container.add(self._treeview)

		# create controls
		button_box = gtk.HBox(False, 5)

		button_add = gtk.Button(stock=gtk.STOCK_ADD)
		button_add.connect('clicked', self._handle_add_session)

		button_delete = gtk.Button(stock=gtk.STOCK_DELETE)
		button_delete.connect('clicked', self._handle_delete_session)

		image_up = gtk.Image()
		image_up.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_BUTTON)

		button_move_up = gtk.Button(label=None)
		button_move_up.add(image_up)
		button_move_up.set_tooltip_text(_('Move Up'))
		button_move_up.connect('clicked', self._handle_move_session, -1)

		image_down = gtk.Image()
		image_down.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_BUTTON)

		button_move_down = gtk.Button(label=None)
		button_move_down.add(image_down)
		button_move_down.set_tooltip_text(_('Move Down'))
		button_move_down.connect('clicked', self._handle_move_session, 1)

		# pack ui
		button_box.pack_start(button_add, False, False, 0)
		button_box.pack_start(button_delete, False, False, 0)
		button_box.pack_end(button_move_down, False, False, 0)
		button_box.pack_end(button_move_up, False, False, 0)

		self.pack_start(container, True, True, 0)
		self.pack_start(button_box, False, False, 0)

	def _load_options(self):
		"""Load options and update interface"""
		self._session_store.clear()
		sessions = options.section('sessions').get('list')
		for i, session in enumerate(sessions):
			name = session.get('name')
			self._session_store.append((name, name, i))

	def _save_options(self):
		"""Method called when save button is clicked"""
		# default panel
		home_panel = {
		        "active_tab": 0, 
		        "tabs": [{
		                'class': 'FileList',
		                'sort_ascending': True,
		                'sort_column': 0,
		                'uri': os.path.expanduser('~')
		            }]
		    }
		
		# prepare data in convince way
		old_sessions = {s.get('name'): s for s in options.section('sessions').get('list')}

		# add new sessions
		new_sessions = []
		for store in self._session_store:
			try:
				# copy old session
				session = old_sessions[store[1]]
				left = session['left']
				right = session['right']
			except:
				# create new session
				left, right = home_panel, home_panel

			# add session
			new_sessions.append({
			        'name': store[0],
			        'left': left,
			        'right': right,
			    })

		# update current sessions id
		sessions = options.section('sessions')
		old_current = sessions.get('current')
		new_current = 0
		try:
			while self._session_store[new_current][2] != old_current:
				new_current += 1
		except:
			new_current = 0
			change_session(None, 0) 

		# save
		sessions.set('current', new_current)
		sessions.set('list', new_sessions)
		options.save()

		# recreate menu
		item_sessions.remove_submenu()
		_create_menu()

	def _handle_edited_name(self, cell, path, text, column):
		"""Filter new names"""
		# check if name already exists
		for session in self._session_store:
			if text == session[0]:
				return
		
		# change name
		iter_ = self._session_store.get_iter(path)
		self._session_store.set_value(iter_, column, text)

		# enable save button
		self._parent.enable_save()
	
	def _handle_add_session(self, widget, data=None):
		"""Add new session to the store"""
		# generate unique name
		names = [s[0] for s in self._session_store]
		new_name = new_session = _('New session')
		if new_name in names:
			num = 0
			while True:
				num += 1
				new_name = '%s %i' % (new_session, num)
				if new_name not in names:
					break
			
		# add session
		self._session_store.append((new_name, new_name, -1))

		# enable save button
		self._parent.enable_save()
	
	def _handle_delete_session(self, widget, data=None):
		"""Remove selected field from store"""
		selection = self._treeview.get_selection()
		item_list, selected_iter = selection.get_selected()

		if (len(item_list) > 1) and (selected_iter is not None):
			# remove item from the store
			item_list.remove(selected_iter)

			# enable save button if item was removed
			self._parent.enable_save()
	
	def _handle_move_session(self, widget, direction):
		"""Move selected bookmark up or down"""
		selection = self._treeview.get_selection()
		item_list, selected_iter = selection.get_selected()

		if selected_iter is not None:
			# get iter index
			index = item_list.get_path(selected_iter)[0]

			# depending on direction, swap iters
			if (direction == -1 and index > 0) \
			or (direction == 1 and index < len(item_list) - 1):
				item_list.swap(selected_iter, item_list[index + direction].iter)

			# enable save button if iters were swapped
			self._parent.enable_save()


def _first_start_specific_actions():
	"""Adds required options to configuration if they are not present"""
	options.create_section('sessions').update({
	        'list': [{'name': DEFAULT_NAME}],
	        'current': 0
	    })

def _create_menu():
	"""Creates menu"""
	# create items
	menu_sessions = gtk.Menu()
	_rename_menu()
	item_manage = gtk.MenuItem(_('Manage sessions'))
	item_separator = gtk.MenuItem()

	sessions = options.section('sessions')
	current_session = sessions.get('current')

	# pack menus and connect signals
	group = None
	for i, session in enumerate(sessions.get('list')):
		item = gtk.RadioMenuItem(group, session.get('name'))
		menu_sessions.append(item)
		if i == current_session:
			item.set_active(True)
		item.connect('activate', change_session, i)
		group = item
	item_sessions.set_submenu(menu_sessions)

	menu_sessions.append(item_separator)	
	menu_sessions.append(item_manage)
	item_manage.connect('activate', show_sessions_manager)

	# add to file menu and show it
	item_sessions.show_all()
	
def _rename_menu():
	"""Creates menu"""
	sessions = options.section('sessions')
	current_session = sessions.get('current')
	current_name = sessions.get('list')[current_session]['name']
	item_sessions.set_label('%s: %s' % (_('Session'), current_name))

def _close_tabs(notebook, num):
	"""Closes first 'num' pages in 'notebook'"""
	page = notebook.get_current_page()
	for i in range(num):
		main_window.close_tab(notebook, notebook.get_nth_page(0))
	main_window.set_active_tab(notebook, page)

def show_sessions_manager(widget, data=None):
	"""Shows preferences window"""
	main_window.preferences_window._show(None, 'sessions')

def save_current_session():
	main_window.save_tabs(main_window.left_notebook, 'left')
	main_window.save_tabs(main_window.right_notebook, 'right')

def change_session(item, new):
	"""Changes session"""
	left_pages = main_window.left_notebook.get_n_pages()
	right_pages = main_window.right_notebook.get_n_pages()

	sessions = options.section('sessions')
	sessions_list = sessions.get('list')
	current = sessions.get('current')

	# forbid changing to the same session
	if current == new:
		return

	session_current = sessions_list[current]
	session_new = sessions_list[new]
	session_new_left = session_new['left']
	session_new_right = session_new['right']
	left = options.section('left')
	right = options.section('right')
	
	# save current session
	save_current_session()

	# swap config
	session_current['left'] = left._get_data()
	session_current['right'] = right._get_data()
	left.set('active_tab', session_new_left['active_tab'])
	right.set('active_tab', session_new_right['active_tab'])
	left.set('tabs', session_new_left['tabs'])
	right.set('tabs', session_new_right['tabs'])
	options.save()

	# load new session
	main_window.load_tabs(main_window.left_notebook, 'left')
	main_window.load_tabs(main_window.right_notebook, 'right')
	sessions.set('current', new)

	# close old tabs
	_close_tabs(main_window.left_notebook, left_pages)
	_close_tabs(main_window.right_notebook, right_pages)

	# rename menu
	_rename_menu()

def register_plugin(application):
	"""Method that Sunflower calls once plugin is loaded"""
	global main_window
	main_window = application
	global options
	options = main_window.tab_options
	
	_first_start_specific_actions()

	# create menu
	global item_sessions
	item_sessions = gtk.MenuItem(_('Sessions'))
	_create_menu()
	main_window.menu_bar.append(item_sessions)
	item_sessions.set_right_justified(True)
	
	# add configuration
	global config
	config = SessionsOptions(main_window.preferences_window, main_window)

