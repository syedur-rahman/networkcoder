""" netmiko mac arp parse
parses the mac and arp tables into one table and outputs results to csv """

# import connection library
import napalm

# import cli coloring library
import colorama

# import input library for passwords
import getpass

#import csv library for command output
import csv

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

class DeviceProfiler:
    """ device profiler
    logs into specified switches and collects a large variety of information and
    outputs it into a couple csv files """
    
    def __init__(self):
        # get user credentials
        self.username, self.password, self.secret = _get_user_credentials()

        # build devices list
        self.devices = _read_file('devices.txt')

        # set up get environment datastructure
        self.get_environment = {}

        # set up get facts datastructure
        self.get_facts = {}
        
        # set up inventory output datastructure
        self.parsed_inventory = {}
        
        # get log filename for inventory output
        self.inv_filename = input('\nPlease provide an inventory output filename: ').strip()
        
        # get log filename for device profiler output
        self.device_filename = input('\nPlease provide a device profile output filename: ').strip()
        
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
        
    def _run_commands(self):
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
            
            # initialize the driver for napalm
            driver = napalm.get_network_driver(device_type)
            
            # provide context for user
            usr_msg = "\nConnecting to " + device.upper()
            print(colorama.Fore.MAGENTA + usr_msg)

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
                
                # message to user to show inventory information is being collected
                usr_msg = "Collecting Inventory...."
                print(colorama.Fore.CYAN + usr_msg)
                
                # initialize get_environment and get_facts functions to retrieve
                # switch information about its environment and resources
                self.get_environment[device] = net_connect.get_environment()
                self.get_facts[device] = net_connect.get_facts()
                
                # collect unformatted inventory information
                command = ['show inventory']
                inventory_raw = net_connect.cli(command)
                self.parsed_inventory[device] = self._parse_inventory(inventory_raw['show inventory'])
                
                    
            # in case of authentication failure
            # user will be informed and the program will exit
            except napalm.base.exceptions.ConnectionException:

                usr_msg = "\nAuthentication Failure - Exiting Device Profiler.\n"
                print(colorama.Fore.RED + usr_msg)

                # exit program
                return
            
            # message to user to show inventory information is being collected
            usr_msg = "Done!"
            print(colorama.Fore.CYAN + usr_msg)
            # disconnect from the device
            net_connect.close()
    
    def device_profiler(self):
        """ device_profiler
        main function that is the catalyst of the script by executing all
        other functions """
        
        # initiate _run_commands function
        self._run_commands()
        
        # check if log files name ends with csv
        if not self.inv_filename.endswith('.csv'):
            self.inv_filename = self.inv_filename + '.csv'
            
        if not self.device_filename.endswith('.csv'):
            self.device_filename = self.device_filename + '.csv'
            
        # open csv log file
        inventory_parse_csv = open(self.inv_filename, 'w', newline='')
        
        # initialize csv writer
        inventory_parse_csv_writer = csv.writer(inventory_parse_csv)
        
        # write header for csv file
        inventory_parse_csv_writer.writerow(['Device', 'Inventory Name', 
                                             'Description', 'Product ID',
                                             'Product Version', 'Serial Number'
                                            ])
        
        # iterate over parsed_routing_table dictionary items
        for device, device_values in self.parsed_inventory.items():
            
            for inventory_part, inventory_values in device_values.items():

                # store values in readable names for output
                description = inventory_values['descr']
                product_id = inventory_values['pid']
                serial_number = inventory_values['sn']
                product_version = inventory_values['vid']
                    
                # write information to csv log file
                inventory_parse_csv_writer.writerow([device, inventory_part, 
                                                    description, product_id, 
                                                    product_version, serial_number
                                                    ])
                                                    
        # open csv log file
        device_profiler_csv = open(self.device_filename, 'w', newline='')
        
        # initialize csv writer
        device_profiler_csv_writer = csv.writer(device_profiler_csv)
        
        # write header for csv file
        device_profiler_csv_writer.writerow(['Device', 'Vendor', 
                                             'Model', 'OS Version',
                                             'Serial Number', 'Uptime (s)',
                                             'Temperature', 'Used RAM (b)',
                                             'Available RAM (b)', 'CPU'
                                            ])
        
        # iterate over dictionary that stores get environment information
        for device, get_environment_parameters in self.get_environment.items():
        
            # store values in readable names for output from get_facts output from napalm
            os_version = self.get_facts[device]['os_version']
            uptime = self.get_facts[device]['uptime']
            vendor = self.get_facts[device]['vendor']
            serial_number = self.get_facts[device]['serial_number']
            model = self.get_facts[device]['model']
            
            # store values in readable names for output from get_environment output from napalm
            cpu = get_environment_parameters['cpu']
            temperature = get_environment_parameters['temperature']
            used_ram = get_environment_parameters['memory']['used_ram']
            available_ram = get_environment_parameters['memory']['available_ram']
            power = get_environment_parameters['power']
            
            # write device profile information to csv file
            device_profiler_csv_writer.writerow([device, vendor, 
                                     model, os_version,
                                     serial_number, uptime,
                                     temperature, used_ram,
                                     available_ram, cpu
                                    ])
                                    
    def _parse_inventory(self, inventory_raw):
        """ _parse_inventory
        parses the inventory output into a sorted dictionary
        
        returns
        --------------
        inventory_dict_all
        dictionary representing the parsed data of the inventory
        contains dictionaries
        
        example output:
        ----------------
        {'3725 chassis': {'name': '3725 chassis', 'pid': 'NM-16ESW=', 
         'vid': '1.0', 'sn': '00000000000'}, '16 Port 10BaseT/100BaseTX EtherSwitch': 
         {'pid': 'NM-16ESW=', 'vid': '1.0', 'sn': '00000000000'}}
        """
        ## Example raw format from show inventory
        # NAME: "3725 chassis", DESCR: "3725 chassis"
        # PID:                   , VID: 0.1, SN: FTX0945W0MY
        
        # initialize dictionaries
        inventory_dict_single = {}
        inventory_dict_all = {}

        # iterate over each line from show inventory output
        for line in inventory_raw.splitlines():
        
            # strip white trailing white space
            line = line.strip()
                
            # remove quotations in the description of devices
            inventory_segments = line.replace('"','')
            
            # split on comma, which separates the different inventory parameters
            inventory_segments = inventory_segments.split(',')
                    
            # If line is blank, continue as it doesn't contain any interesting info
            if line == '':
                continue
                
            # iterate over each inventory parameter and separate the field name and value
            for inventory_segment in inventory_segments:
                
                # Format of inventory output is always Field name: Field value
                field_name, field_value = inventory_segment.split(':')
                
                # make field_name lower case and remove trailing white space
                field_name = field_name.strip()
                field_name = field_name.lower()
                
                # remove trailing white space from field_value
                field_value = field_value.strip()
                
                # if this is a new part, create a new dictionary
                if line.lower().startswith('name'):
                    
                    # store the dictionary key for this inventory part
                    inventory_name = field_value
                
                # store part parameters into a dictionary
                inventory_dict_single[field_name] = field_value
            
            # flag to know when last piece of information for this part is complete
            if line.lower().startswith('pid'):
            
                # store dictionary of one inventory part into a larger dictionary
                inventory_dict_all[inventory_name] = inventory_dict_single
                
                # reset dictionary
                inventory_dict_single = {}

        return inventory_dict_all      
 
def main():
    # message to the user about the quick deploy script
    usr_msg = "# Device Profiler - Napalm Edition"
    usr_msg += "\n# Creates a profile of the specified switches "
    usr_msg += "and outputs it to csv files!\n"
    print(colorama.Fore.YELLOW + usr_msg)

    # initialize the map network advance class
    device_profiler = DeviceProfiler()

    # run the commands via the napalm interface
    device_profiler.device_profiler()

    # message to the user about the quick deploy ending
    usr_msg = "\nThe Device Profiler script has completed running!\n"  
    print(colorama.Fore.MAGENTA + usr_msg)
    
if __name__ == '__main__':
    main()