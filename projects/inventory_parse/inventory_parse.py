""" netmiko mac arp parse
parses the mac and arp tables into one table and outputs results to csv """

# import connection library
import netmiko

# import cli coloring library
import colorama

# import input library for passwords
import getpass

# import collections for ordered dictionary
import collections

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
    
def inventory_parse():
    """ main
    main function that is the catalyst of the script by executing all
    other functions """
    
       # message to the user about the mac arp parse script
    usr_msg = "# Inventory Parse"
    usr_msg += "\n# Generates a CSV of all inventory components of network devices!\n"
    print(colorama.Fore.YELLOW + usr_msg)
    
    # get user credentials
    username, password, secret = _get_user_credentials()
    
    # get log filename
    log_filename = input('\nPlease provide an output filename: ').strip()
    
    # build devices list
    devices = _read_file('devices.txt')
        
    # check if log file name ends with csv
    if not log_filename.endswith('.csv'):
        log_filename = log_filename + '.csv'
        
    # open csv log file
    inventory_parse_csv = open(log_filename, 'w', newline='')
    
    # initialize csv writer
    inventory_parse_csv_writer = csv.writer(inventory_parse_csv)
    
    # write header for csv file
    inventory_parse_csv_writer.writerow(['Device', 'Inventory Name', 
                                         'Description', 'Product ID',
                                         'Product Version', 'Serial Number'
                                        ])
    
    for device in devices:
        # if the user has provided the device type
        if ',' in device:
            # re-initialize device and device type
            device_type = device.split(',')[-1].strip().lower()
            device = device.split(',')[0].strip()
        else:
            # initialize device type
            # by default set to cisco ios to play it safe
            device_type = 'cisco_ios'
            
        # provide context for user
        usr_msg = "\nConnecting to " + device.upper()
        print(colorama.Fore.MAGENTA + usr_msg)

        # build netmiko device profile
        network_device_profile = {
            'device_type': device_type,
            'ip': device,
            'username': username,
            'password': password,
            'secret': secret,
        }

        # initialize the connection handler of netmiko
        try:
            net_connect = netmiko.ConnectHandler(**network_device_profile)
            
        # in case of authentication failure
        # user will be informed and the program will exit
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            # in case there were any successfully collected
            # data in the previous network devices
            # write to the log file to successfully save

            usr_msg = "\nAuthentication Failure - Exiting Route Parse.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit program
            return

        # in case of device type value error
        # user will be informed and the program will exit
        except ValueError:
            # in case there were any successfully collected
            # data in the previous network devices
            # write to the log file to successfully save

            usr_msg = "\nDevice Type Failure. Device Type " + device_type
            usr_msg += " Does Not Exist - Exiting Route Parse.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit program
            return
            
        # enter enable mode if required
        if net_connect.find_prompt().endswith('>'):
            net_connect.enable()
            
        # message to user to show inventory information is being collected
        usr_msg = "Collecting Inventory...."
        print(colorama.Fore.CYAN + usr_msg)
                
        # collect unformatted inventory information
        inventory_output = net_connect.send_command('show inventory')
        
        # parse raw output of routing table
        parsed_inventory = _parse_inventory(inventory_output)
        
        # iterate over parsed_routing_table dictionary items
        for inventory_part, inventory_values in parsed_inventory.items():
        
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
                                           
        # disconnect from the device            
        net_connect.disconnect()
        
        # message to user to show mac table information is done being collected
        usr_msg = "Done!"
        print(colorama.Fore.CYAN + usr_msg)
        
    # close csv log file
    inventory_parse_csv.close()
    
    # message to the user about the mac arp parse ending
    usr_msg = "\nThe Inventory Parse script has completed running!\n"
        
    print(colorama.Fore.MAGENTA + usr_msg)

    
def _parse_inventory(inventory_output):
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
    for line in inventory_output.splitlines():
    
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
            
if __name__ == '__main__':
    inventory_parse()