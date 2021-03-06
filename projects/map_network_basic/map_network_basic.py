""" map network basic
quickly deploy commands using the napalm library """

# import connection library
import napalm

# import cli coloring library
import colorama

# import input library for passwords
import getpass

# import networkx and matplotlib for graphing purposes
import networkx as nx
import matplotlib.pyplot as plt

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

class MapNetworkBasic:
    """ map network basic
    logs into specified switches and generates a map of the connectivity """

    def __init__(self):
        # get user credentials
        self.username, self.password, self.secret = _get_user_credentials()

        # build devices list
        self.devices = _read_file('devices.txt')

        # set up lldp info datastructure
        self.lldp_info = {}

        # set up hostname datastructure
        self.hostname = {}

    def _check_user_provided_data_for_errors(self):
        """ check user provided data for errors
        do a cursory preview of the user provided data via the devices.txt
        file and make sure the data provided is per specification

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


        return valid_data

    def run_commands(self):
        """ run commands
        runs the napalm getters to get the neighborship information of switches """

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
            usr_msg = "\n# Retrieving neighbor information of: " + device.upper()
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

                self.lldp_info[device] = net_connect.get_lldp_neighbors_detail()
                self.hostname[device] = net_connect.get_facts()['hostname']

            # in case of authentication failure
            # user will be informed and the program will exit
            except napalm.base.exceptions.ConnectionException:
                usr_msg = "\nAuthentication Failure - Exiting Quick Deploy."
                print(colorama.Fore.RED + usr_msg)

                # exit program
                return

            # disconnect from the device
            net_connect.close()

    def generate_map(self):
        """ generate map """

        connections = []

        for switch, connection_details in self.lldp_info.items():
            for interface, interface_details in connection_details.items():
                for interface_detail in interface_details:
                    connection = {
                        'local_interface': interface,
                        'local_switch': self.hostname[switch],
                        'remote_interface': interface_detail['remote_port'],
                        'remote_switch': interface_detail['remote_system_name'],
                    }

                    connections.append(connection)

        g = nx.MultiGraph()

        for connection in connections:
            g.add_edge(connection['local_switch'], connection['remote_switch'])

        nx.draw(g, with_labels=True)

        plt.savefig("basic_diagram.png", format="PNG")

def main():
    # message to the user about the quick deploy script
    usr_msg = "# Map Network Basic - Napalm Edition"
    usr_msg += "\n# Map a basic network diagram automatically!!\n"
    print(colorama.Fore.YELLOW + usr_msg)

    # initialize the map network basic class
    map_network_basic = MapNetworkBasic()

    # run the commands via the napalm interface
    map_network_basic.run_commands()

    # generate map
    map_network_basic.generate_map()

    # message to the user about the quick deploy ending
    usr_msg = "\nThe map has been generated! Check the local directory!\n"        
    print(usr_msg)

if __name__ == '__main__':
    main()