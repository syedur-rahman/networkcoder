""" napalm quick deploy
quickly deploy commands using the napalm library """

# import connection library
import napalm

# import cli coloring library
import colorama

# import input library for passwords
import getpass

# import collections for ordered dictionary
import collections

# initiate colorama which is required for windows
# autoreset also allows to clear colorama settings per print statement
colorama.init(autoreset=True)

def _get_user_credentials():
    """ get user credentials
    this function initiates a prompt for the user's credentials

    returns
    -------
    username
        str variable representing the username
    password
        str variable representing the password
    secret
        str variable representing the enable secret

    """

    # iterate until the user provides username & password
    while True:
        # initialize username & password
        usr_msg = "Please provide your credentials."
        print(usr_msg)
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        secret = getpass.getpass("Secret: ").strip()

        # check if user entered username and password
        if username and password:
            pass
        else:
            # alert user that the username or password was not provided
            usr_msg = "\nCritical: Username or password was not provided."
            usr_msg += "Please try again.\n"
            print(colorama.Fore.RED + usr_msg)

            # re-initates loop
            continue

        # if secret was not provided by the user
        if not secret:
            # alert user that the secret was not provided
            usr_msg = "\nWarning: Please note that secret was not provided.\n"
            usr_msg += "Secret will be assumed to be the same as the password."
            print(colorama.Fore.CYAN + usr_msg)

            # set secret and password sa the same
            secret = password

        # return the username and password
        return username, password, secret

def _read_file(filename):
    """ read file
    iterate through the file and store
    the data the user provided in a list

    parameters
    ----------
    filename : str
        the filename of the file

    returns
    -------
    user_items
        list variable representing all the items the user provided

    """

    # initialize user items
    user_items = []

    try:
        # open a context handler for the file
        with open(filename, 'r') as user_file:
            # iterate through the file
            for line in user_file.read().splitlines():
                # skip lines that start with # as it implies a comment
                if line.strip().startswith('#'):
                    # re-initiate loop
                    continue

                # add line to user items assuming it is not empty
                if line.strip():
                    user_items.append(line)
    # if file was not found - ignore issue as there is a clause to exit
    # the script in case there are no items in the user_items datastructure
    except FileNotFoundError:
        pass

    # return user items
    return user_items

class QuickDeploy:
    """ quick deploy
    logs into specified switches and runs specified commands """

    def __init__(self):
        # get user credentials
        self.username, self.password, self.secret = _get_user_credentials()

        # get log filename
        self.log_filename = input('\nPlease provide a log filename: ').strip()

        # build commands list
        self.commands = _read_file('commands.txt')

        # build devices list
        self.devices = _read_file('devices.txt')

        # initialize log with ordered dictionary
        # this is on the off chance the user is using an older python version
        self.log = collections.OrderedDict()

    def _write_log_data_to_file(self):
        """ write log data to file
        method to write captured data from the switch
        to a file the user has already specified """

        # append the txt extension to the filename
        if self.log_filename.endswith('.txt'):
            pass
        else:
            self.log_filename += '.txt'

        # only write log file if there are contents
        if not self.log:
            # exit method
            return

        # open a context handler for the file
        with open(self.log_filename, 'w') as fn:
            # iterate through the log ordered dictionary
            for device, captured_data_list in self.log.items():
                # iterate through the captured data
                for captured_data in captured_data_list:
                    # initialize show command and device output
                    show_command = captured_data[0]
                    device_output = captured_data[1]

                    # write header in log file which includes show command
                    header = device + " - " + show_command + "\n"
                    fn.write("~"*len(header) + "\n")
                    fn.write(header)
                    fn.write("~"*len(header) + "\n")

                    # write device output in the log file
                    for line in device_output.splitlines():
                        fn.write(line + "\n")

    def _check_user_provided_data_for_errors(self):
        """ check user provided data for errors
        do a cursory preview of the user provided data via the
        commands.txt and devices.txt file and make sure
        the data provided is per specification

        returns
        -------
        valid_data
            bool variable representing whether the data provided
            by the user is valid or invalid

        """

        # initialize valid data
        # assume by default the user has provided valid data
        valid_data = True

        # check if user provided devices
        if not self.devices:
            usr_msg = "\nAlert: No devices were provided."
            usr_msg += " Please check the devices.txt file.\n"
            print(colorama.Fore.RED + usr_msg)

            valid_data = False

        # check if user provided commands
        elif not self.commands:
            usr_msg = "\nAlert: No commands were provided."
            usr_msg += " Plese check the commands.txt file.\n"
            print(colorama.Fore.RED + usr_msg)

            valid_data = False

        else:
            # initialize conf t and end counters
            conf_line_count = 0
            end_line_count = 0

            # check is user formatted commands file correctly
            for command in self.commands:
                # check if line starts with either
                if command.strip().startswith('conf'):
                    conf_line_count += 1
                elif command.strip().startswith('end'):
                    end_line_count += 1

            # if conf t and end do not match in count
            # then command file is formatted improperly
            # per the specifications of the quick deploy script
            if conf_line_count != end_line_count:
                usr_msg = "\nAlert: Configuration lines were improperly formatted."
                usr_msg += " Plese check the commands.txt file."
                print(colorama.Fore.RED + usr_msg)

                valid_data = False

        return valid_data

    def deploy_commands(self):
        """ deploy commands
        the primary method of the quick deploy class
        runs all the commands against the devices the user has provided """

        # stop deploy if the data the user provided is not valid
        if not self._check_user_provided_data_for_errors():
            return

        # iterate through the devices
        for device in self.devices:
            # initialize device type
            # by default set to cisco ios to play it safe
            device_type = 'ios'

            # if the user has provided the device type
            if ',' in device:
                # re-initialize device and device type
                device_type = device.split(',')[-1].strip().lower()
                device = device.split(',')[0].strip()

            # provide context for user
            usr_msg = "\n# Running Commands Against: " + device.upper()
            print(colorama.Fore.MAGENTA + usr_msg)

            # initialize the driver for napalm
            driver = napalm.get_network_driver(device_type)

            # initialize the connection handler for napalm
            try:
                # setup driver profile
                net_connect = driver(
                    hostname=device,
                    username=self.username,
                    password=self.password,
                    optional_args={'secret': self.secret},
                )

                # open connection
                net_connect.open()

            # in case of authentication failure
            # user will be informed and the program will exit
            except napalm.base.exceptions.ConnectionException:
                # in case there were any successfully collected
                # data in the previous network devices
                # write to the log file to successfully save
                if self.log:
                    self._write_log_data_to_file()

                usr_msg = "\nAuthentication Failure - Exiting Quick Deploy."
                print(colorama.Fore.RED + usr_msg)

                # exit program
                return

            # configuration set
            # napalm enables the use of sending bulk
            # configuration commands over so all configuration
            # related commands will be stored here
            config_set = ''

            # flag to check if commands are configuration related
            config_flag = False

            # iterate through the commands
            for command in self.commands:
                # remove leading or trailing spacing from command
                command = command.strip()

                # check if command starts with conf
                # this signifies the start of the configuration
                if command.startswith('conf'):
                    # set config flag to true
                    config_flag = True

                # check if the command starts with end
                # this signifies the end of the configuration
                elif command.startswith('end'):
                    # provide context for user
                    for config_line in config_set.strip().splitlines():
                        usr_msg = "...Running Config: " + config_line
                        print(usr_msg)

                    # reset the config flag
                    config_flag = False

                    # send the configuration set over to the device
                    net_connect.load_merge_candidate(config=config_set)
                    net_connect.commit_config()

                    # reset the configuration set
                    config_set = ''

                # if config flag is true
                elif config_flag:
                    # add command to the configuration set
                    config_set += command + '\n'

                # otherwise send command over to switch normally
                # generally used when there are show commands involved
                else:
                    # provide context for user
                    usr_msg = "...Running Command: " + command
                    print(usr_msg)

                    # capture device output from show command
                    device_output = net_connect.cli([command])

                    # initialize log for the device
                    # only invoked when the user has run show commands
                    if device not in self.log:
                        self.log[device] = []

                    # initialize the capture to save to log file later
                    self.log[device].append([command, list(device_output.values())[0]])

            # disconnect from the device
            net_connect.close()

        # write captured data to log file
        self._write_log_data_to_file()

def main():
    # message to the user about the quick deploy script
    usr_msg = "# Quick Deploy - Napalm Edition"
    usr_msg += "\n# Deploy commands easily to network devices!\n"
    print(colorama.Fore.YELLOW + usr_msg)

    # initialize the quick deploy class
    quick_deploy = QuickDeploy()

    # deploy commands
    try:
        quick_deploy.deploy_commands()

    # this is a normally a lazy catch all for errors
    # but in this instance, we are just forcing the quick deploy
    # script to write to the log before crashing out in case
    # there was an error that it came across that was unexpected
    # that is why the error will still be raised in this exception clause
    except:
        # write log file before raising exception
        quick_deploy._write_log_data_to_file()
        raise

    # message to the user about the quick deploy ending
    usr_msg = "\nThe quick deploy script has completed running!\n"
    # add additional information if log file was generated with content
    if quick_deploy.log:
        usr_msg += "Please check the generated log file - " + quick_deploy.log_filename + ".\n"
        
    print(usr_msg)

if __name__ == '__main__':
    main()