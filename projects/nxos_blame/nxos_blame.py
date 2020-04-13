""" nxos blame
extension of the existing nxos account parse script 
builds a gui to showcase accounting information from cisco nexus devices """

# import pyside2 for gui
from PySide2 import QtWidgets, QtGui, QtCore

# import sys to exit application
import sys

# import connection library
import netmiko

# import datetime for parsing purposes
import datetime

# import sockets library for dns lookups
import socket

class NXOSBlame(QtWidgets.QDialog):

    def __init__(self):
        # inherit properties from QDialog
        super().__init__()

        # set up title of application
        self.setWindowTitle('NXOS Blame - NetworkCoder')

        # set up application icon
        self.setWindowIcon(QtGui.QIcon('nxos_blame.png'))

        # set up stylesheet
        # this is nothing fancy - this is more or less to demonstrate the idea of stylesheets
        # in this project as an example
        # in a production setting, it would be a good idea to work on the style sheet
        # a little more to add a nice visual component to the application
        self.setStyleSheet("QListView::item:selected { background-color: #008000 }")

        # set up parent layout
        self.layout = QtWidgets.QVBoxLayout()

        # center the application
        self.center_application()

        # build the before, during, after screens
        self.build_screens()

        # build the network devices input
        self.build_network_devices_input()

        # build the credentials input
        self.build_credentials_input()

        # build the during display
        self.build_during_display()

        # build the after display
        self.build_after_display()

        # initialize the layout for the application
        self.setLayout(self.layout)

        # initialize the final result dataset
        self.final_result = {}

    def center_application(self):
        """ center application
        centers the application to the user's screen """

        # set up the window of the application
        self.setGeometry(0, 0, 400, 500)
        frame_geometry = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centerPoint)
        self.move(frame_geometry.topLeft())

    def build_screens(self):
        """ build screens
        build the before, during, and after screens for the user to see
        the before screen will be where the user enters in their parameters
        while the after screen will be where the user sees the results """

        # build the before screen
        self.before_screen_frame = QtWidgets.QFrame()
        self.before_screen_layout = QtWidgets.QGridLayout()
        self.before_screen_layout.setContentsMargins(0,0,0,0)
        self.before_screen_frame.setLayout(self.before_screen_layout)
        self.layout.addWidget(self.before_screen_frame)

        # build the during screen
        self.during_screen_frame = QtWidgets.QFrame()
        self.during_screen_layout = QtWidgets.QVBoxLayout()
        self.during_screen_layout.setContentsMargins(0,0,0,0)
        self.during_screen_frame.setLayout(self.during_screen_layout)
        self.layout.addWidget(self.during_screen_frame)

        # build the after screen
        self.after_screen_frame = QtWidgets.QFrame()
        self.after_screen_layout = QtWidgets.QGridLayout()
        self.after_screen_layout.setContentsMargins(0,0,0,0)
        self.after_screen_frame.setLayout(self.after_screen_layout)
        self.layout.addWidget(self.after_screen_frame)

        # hide the inactive screens from the user
        self.during_screen_frame.hide()
        self.after_screen_frame.hide()

    def build_network_devices_input(self):
        """ build network devices input
        builds the gui component to enable user to enter in a list
        of network devices to access """

        # network devices field
        self.network_devices_field = QtWidgets.QTextEdit()
        self.network_devices_field.setPlaceholderText("one device per line here...")

        # build onto the before screen layout
        self.before_screen_layout.addWidget(self.network_devices_field, 0, 0, 1, 2)

    def build_credentials_input(self):
        """ build credentials input
        builds the gui component to enable user to enter their
        network device credentials """

        # username field
        self.username_field = QtWidgets.QLineEdit()
        self.username_field.setPlaceholderText("username here...")

        # password field
        self.password_field = QtWidgets.QLineEdit()
        self.password_field.setPlaceholderText("password here...")
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)

        # submit button
        self.submit_button = QtWidgets.QPushButton("SUBMIT")
        self.submit_button.clicked.connect(self.click_submit)

        # build onto the before screen layout
        self.before_screen_layout.addWidget(self.username_field, 1, 0, 1, 1)
        self.before_screen_layout.addWidget(self.password_field, 1, 1, 1, 1)
        self.before_screen_layout.addWidget(self.submit_button, 2, 0, 1, 2)

    def build_during_display(self):
        """ build during display
        this is the display that is shown while the application is
        collecting data from the devices in question """

        # network devices field
        self.during_display = QtWidgets.QTextEdit()
        self.during_display.setReadOnly(True)

        # build onto the during screen layout
        self.during_screen_layout.addWidget(self.during_display)

    def build_after_display(self):
        """ build after display
        this is the display that showcases the results to the user! """

        # network device selection
        self.device_selection = QtWidgets.QListWidget()
        self.device_selection.itemSelectionChanged.connect(self.select_device)

        # blame display
        self.blame_display = QtWidgets.QListWidget()
        self.blame_display.itemSelectionChanged.connect(self.show_blame)

        # user details
        self.user_details = QtWidgets.QLineEdit()
        self.user_details.setReadOnly(True)

        # build onto the after screen layout
        self.after_screen_layout.addWidget(self.device_selection, 0, 0, 6, 1)
        self.after_screen_layout.addWidget(self.blame_display, 0, 1, 5, 1)
        self.after_screen_layout.addWidget(self.user_details, 5, 1, 1, 1)

    def click_submit(self):
        """ click submit
        action to take when the submit button is pressed by the user """

        # initialize the credentials
        self.username = self.username_field.text()
        self.password = self.password_field.text()

        # initialize the devices
        raw_device_data = self.network_devices_field.toPlainText().splitlines()
        self.devices = [device.strip() for device in raw_device_data]

        # initialize the width of the screen
        # this will modify the entire screen real estate based on configuration
        self.largest_width = 0

        # hide the before screen and activate the during screen
        self.before_screen_frame.hide()
        self.during_screen_frame.show()

        # run the nxos parse logic
        self.nxos_account_parse()

        # build device selection
        self.build_device_selection()

        # display the after screen & hide during screen
        self.during_screen_frame.hide()
        self.after_screen_frame.show()

    def build_device_selection(self):
        """ build device selection
        builds the device selection for the after display """

        # used to resize size of the device selection menu
        # to make sure the characters are visible on the user's menu
        largest_character_width = 0

        # iterate through the devices
        for device in self.devices:
            # initialize the character width of the device based on font size
            character_width = self.device_selection.fontMetrics().boundingRect(device).width()

            # update the width of the widget based on the largest character width
            if character_width > largest_character_width:
                # update the largest character width with the current character width
                largest_character_width = character_width

                # update the size of the width
                self.device_selection.setFixedWidth(largest_character_width + 5)

            # add the device to the device selection widget
            self.device_selection.addItem(device)

    def update_during_display(self, usr_msg):
        """ update during display
        as displays are not generally updated dynamically
        this method ensures that the during display is updated while
        progress is being made to inform the user of what is going on """

        # append the message to the during display
        self.during_display.append(usr_msg)

        # call the application to process the events
        # this is necessary to update the screen as progress is being made
        QtWidgets.QApplication.processEvents()

    def _parse_show_accounting_log(self, accounting_log_output):
        """ parse show accounting log
        helper function with the parsing logic for the show accounting log command

        returns
        -------
        parsed_accounting_data
            dict representing the parsed data of show accounting log
            will contain the date as key and user->[config] data as values

            example format listed below:

            { '2019-01-01': { 'admin': [ config_lines ] } }

        """
        # initialize parsed accounting data
        parsed_accounting_data = {}

        # iterate through the device output
        for line in accounting_log_output.splitlines():
            # skip if this was not a configuration update
            if 'configure' not in line:
                continue
            # skip if the configuration is not defined as success
            elif not line.strip().endswith('(SUCCESS)'):
                continue

            # remove the success tag of the line
            line = line.replace('(SUCCESS)', '')

            # cisco date format
            # this is the way cisco format's their date in the command
            cisco_date_format = '%a %b %d %H:%M:%S %Y:'

            # date of change date format
            date_of_change_date_format = '%Y-%m-%d'

            # determine date of change
            raw_date_from_line = line.split('type')[0]

            # convert raw date from show command to a datetime object
            date_object = datetime.datetime.strptime(raw_date_from_line, cisco_date_format)

            # convert datetime object to a string in the date of change date format
            date_of_change = date_object.strftime(date_of_change_date_format)

            # grab user from the line
            user = line.split(':')[-2].split('=')[-1]

            # grab change from the line
            change = line.split(';')[-1].strip()

            # for formatting, add spaces to command based off ';' in line
            number_of_spaces = line.count(';') - 1
            change = 2*number_of_spaces*' ' + change

            # initialize parsed data with date of change
            if date_of_change not in parsed_accounting_data:
                parsed_accounting_data[date_of_change] = {}
            # initialize parsed data with user
            if user not in parsed_accounting_data[date_of_change]:
                parsed_accounting_data[date_of_change][user] = []

            # add change the user did that day to the parsed data
            parsed_accounting_data[date_of_change][user].append(change)

        return parsed_accounting_data

    def _compare_run_with_account(self, run_output, parsed_accounting_data):
        """ compare run with account
        takes the show run output and compares with the accounting log
        to tie the configuration together with the user that modified it

        returns
        -------
        comparison
            list representing what was modified in show run
            which includes the following - user that modified and date
            each entry in list will be a dictionary

            example format listed below:

            [
                { 'hostname nexus': { 'user': 'ethan', 'date': '2020-01-20' } },
                { 'enable secret *': { 'user': 'frank', 'date': '2020-01-20' } }
            ]

        """

        # initialize comparison
        comparison = []
        parent_run_line = ''
        parent_change_line = ''

        # iterate through the run output
        for line in run_output.splitlines():
            # initialize flag for when a change is detected in show run
            found_change_in_data = False

            # figure out what the parent line of the current line is
            # example: interface loopback100 is parent of description test
            # this is important in case there are duplicate configuration
            # in order to differentiate between who did which configuration
            # we must know the parent line of the configuration
            leading_spaces_of_line = len(line) - len(line.lstrip(' '))
            leading_spaces_of_parent_run_line = len(parent_run_line) - len(parent_run_line.lstrip(' '))

            # update the parent run line
            if leading_spaces_of_line <= leading_spaces_of_parent_run_line:
                parent_run_line = line

            # iterate through the parsed accounting data
            for date_of_change, user_info in reversed(sorted(parsed_accounting_data.items())):
                # iterate through the user info
                for user, changes in user_info.items():
                    # iterate through the changes
                    for change in changes:

                        # this specific logic is to figure out the parent line of the
                        # configuration from the changes performed that were
                        # captured in the accounting show command
                        leading_spaces_of_change = len(change) - len(change.lstrip(' '))
                        leading_spaces_of_parent_change = len(parent_change_line) - len(parent_change_line.lstrip(' '))

                        # update the parent change line
                        if leading_spaces_of_change <= leading_spaces_of_parent_change:
                            parent_change_line = change

                        # check if change is equal to the line
                        if line == change:
                            # if the parent of the run and change are the same
                            if parent_run_line == parent_change_line:
                                # add to comparison
                                data = {line: {'user': user, 'date': date_of_change}}
                                comparison.append(data)
                                # set flag to true
                                found_change_in_data = True
                                break

                        # chain the breaks
                        if found_change_in_data:
                            break

                    # chain the breaks
                    if found_change_in_data:
                        break

                # chain the breaks
                if found_change_in_data:
                    break

            # store the configuration with no one to blame
            if not found_change_in_data:
                data = {line: {'user': 'unknown', 'date': '???'}}
                comparison.append(data)

        return comparison

    def nxos_account_parse(self):
        """ nxos account parse
        parses the accounting information on cisco nexus switches """

        # introduction message to the user
        usr_msg = "<span style=\" font-size:14pt; font-weight:600; color:#410056;\" >"
        usr_msg += "NXOS Blame - Collect & Parse"
        usr_msg += "</span>"

        # set the during display text and process events
        self.during_display.setText(usr_msg)
        QtWidgets.QApplication.processEvents()

        # initialize parsed data
        parsed_data = {}

        # iterate through the devices
        for device in self.devices:
            # build netmiko device profile
            network_device_profile = {
                'device_type': 'cisco_nxos',
                'ip': device,
                'username': self.username,
                'password': self.password,
                'secret': self.password,
            }

            # initialize the connection handler of netmiko
            usr_msg = "<br><span style=\" font-size:12pt; font-weight:600; color:#0F52BA;\" >"
            usr_msg += f"Connecting to {device.lower()}"
            usr_msg += "</span>"
            self.update_during_display(usr_msg)
            net_connect = netmiko.ConnectHandler(**network_device_profile)

            # initialize show account log command
            command = 'show accounting log all'

            # capture device output from show command
            usr_msg = "<i><span style=\" font-size:12pt;\" >"
            usr_msg += "...Running 'show accounting log all'"
            usr_msg += "</span></i>"
            self.update_during_display(usr_msg)
            accounting_log_output = net_connect.send_command(command)

            # parse the device output
            usr_msg = "<i><span style=\" font-size:12pt;\" >"
            usr_msg += "...Parsing 'show accounting log all'"
            usr_msg += "</span></i>"
            self.update_during_display(usr_msg)
            parsed_accounting_data = self._parse_show_accounting_log(accounting_log_output)

            # initialize show run command
            command = 'show run'

            # capture device output from show command
            usr_msg = "<i><span style=\" font-size:12pt;\" >"
            usr_msg += "...Running 'show run'"
            usr_msg += "</span></i>"
            self.update_during_display(usr_msg)
            run_output = net_connect.send_command(command)

            # parse the device output
            usr_msg = "<i><span style=\" font-size:12pt;\" >"
            usr_msg += "...Compare 'show accounting log all' with 'show run'"
            usr_msg += "</span></i>"
            self.update_during_display(usr_msg)

            # build final result dataset
            self.final_result[device] = {}
            self.final_result[device] = self._compare_run_with_account(run_output, parsed_accounting_data)

            # disconnect from the nexus switch
            net_connect.disconnect()

        # display last message of the during display before the transition to after
        usr_msg = "<br><i>Rendering Results. Please standby...</i>"
        self.update_during_display(usr_msg)

    def select_device(self):
        """ select device
        user selected a device in the after display
        this updates the blame display with the selected device's information """

        # initialize device
        device = self.device_selection.currentItem().text()

        self.blame_display.clear()

        # check if device is not in final result
        if device not in self.final_result:
            self.blame_display.addItem('<i>No data found for this device...</i>')
            return

        # initialize current configuration items
        # this will be used to keep track of which user did what change
        # based on the row the chang is on in the list widget
        self.current_configuration_items = []

        # iterate through the line data from the final results
        for line_data in self.final_result[device]:
            # initialize the line, user, date
            line = list(line_data.keys())[0]
            user = list(line_data.values())[0]['user']
            date = list(line_data.values())[0]['date']

            # add the data to the configuration items
            self.current_configuration_items.append([user, date])

            # add line to the blame display if not empty
            if line.strip():
                self.build_config_selection(line)
            # otherwise just add "!" for empty spaces
            # this is mostly just for formatting reasons
            else:
                self.blame_display.addItem("!")

    def build_config_selection(self, line):
        """ build config selection
        builds the config selection for the after display """

        # initialize the width of the device selection
        width = self.blame_display.fontMetrics().boundingRect(line).width()

        # update the largest width assuming the width is larger
        if width > self.largest_width:
            # set the largest width accordingly
            self.largest_width = width

            # update the actual display accordingly
            self.blame_display.setFixedWidth(self.largest_width + 5)

        # add the configuration line to the blame display
        self.blame_display.addItem(line)

    def show_blame(self):
        """ show blame
        show who is to blame! """

        # initialize the user and date based on the row of the configuration selected
        user = self.current_configuration_items[self.blame_display.currentRow()][0]
        date = self.current_configuration_items[self.blame_display.currentRow()][1]

        # update the widget to display who to blame for this configuration
        self.user_details.setText(f'Modified by {user} on {date}')

if __name__ == '__main__':
    # create pyside application
    app = QtWidgets.QApplication(sys.argv)

    # create and display nxos blame application
    nxos_blame_application = NXOSBlame()
    nxos_blame_application.show()

    # run the main qt loop till user exits
    sys.exit(app.exec_())