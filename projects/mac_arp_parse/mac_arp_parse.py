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
                                 
def arp_parse(raw_arp_table):
    """ arp parse
    parses the arp table output into a sorted dictionary 

    returns
    -------
    mac_parse_dict
    dict representing the parsed data of arp table
    will contain the mac address as key and ip address as values

    example format listed below:
    {'0050.7966.6800' : {'ip_address': '192.168.160.129'} }

    """
        
    # initalize dictionary that will contain the arp information
    # of each device
    arp_parse_dict = {}
    
    # iterate over output of show arp 
    for line in raw_arp_table.splitlines():
        ip_address = ''
        mac_address = ''

        # split based on white space
        line_parameters = line.split()
        
        # iterate over parameters and check for mac address and ip address
        for parameter in line_parameters:
            # check for mac address
            if parameter.count('.') == 2:
                mac_address = parameter
                
            # check for ip address
            if parameter.count('.') == 3:
                ip_address = parameter
        
        # store information into a dictionary for easy access
        if mac_address and ip_address:
            arp_parse_dict[mac_address] = {'ip_address': ip_address}
            
    return arp_parse_dict
        
def mac_parse(raw_mac_table):
    """ mac parse
    parses the mac table output into a sorted dictionary

    returns
    -------
    mac_parse_dict
    dict representing the parsed data of mac address table
    will contain the mac address as key and interface as values

    example format listed below:
    {'0050.7966.6800' : {'interface': 'FastEthernet1/0'} }

    """
    
    # initalize dictionary that will contain the mac table information
    # of each device
    mac_parse_dict = {}
    
    for line in raw_mac_table.splitlines():
        # define variables so that dictionary doesn't error out
        interface = ''
        mac_address = ''
        
        # split based on white space
        line_parameters = line.split()
        
        # iterate over parameters and check for mac address and interface
        for parameter in line_parameters:
        
            # check for mac address
            if parameter.count('.') == 2:
                mac_address = parameter
            
            # check for interface
            if '/' in parameter.lower() or 'vlan' in parameter.lower():
                interface = parameter
                
        # store information into a dictionary for easy access
        if interface and mac_address:
            mac_parse_dict[mac_address] = {'interface': interface}
            
    return mac_parse_dict
            
def mac_arp_parse():
    """ main
    main function that is the catalyst of the script by executing all
    other functions """
    
    # message to the user about the mac arp parse script
    usr_msg = "# MAC ARP Parse - Netmiko Edition"
    usr_msg += "\n# Generates a CSV of all devices in the MAC "
    usr_msg += "and ARP table on a network device!\n"
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
    mac_arp_csv = open(log_filename, 'w', newline='')
        
    # initialize csv writer
    mac_arp_csv_writer = csv.writer(mac_arp_csv)
    
    # write header for csv file
    mac_arp_csv_writer.writerow(['Device', 'Mac Address', 'IP address', 'Interface'])
    
    # iterate through the devices
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

            usr_msg = "\nAuthentication Failure - Exiting MAC ARP Parse.\n"
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
            usr_msg += " Does Not Exist - Exiting Mac ARP Parse.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit program
            return
            
        # enter enable mode if required
        if net_connect.find_prompt().endswith('>'):
            net_connect.enable()
        
        # message to user to show arp table information is being collected
        usr_msg = "Collecting ARP Table Information"
        print(colorama.Fore.CYAN + usr_msg)
                
        # collect arp table information
        raw_arp_table = net_connect.send_command('show ip arp')
        
        # parse raw output of arp table
        parsed_arp_table = arp_parse(raw_arp_table)
        
        # message to user to show mac table information is being collected
        usr_msg = "Collecting MAC Table Information"
        print(colorama.Fore.CYAN + usr_msg)
        
        #collect arp table information
        raw_mac_table = net_connect.send_command('show mac address-table')
        
        # check if command syntax is wrong for mac address table
        # command differs on IOS and IOS-XE/NXOS
        if 'invalid input' in raw_mac_table.lower():
            # try different syntax for mac address table
            raw_mac_table = net_connect.send_command('show mac-address-table')
            
        # parse raw output of mac address table
        parsed_mac_table = mac_parse(raw_mac_table)
        
        # message to user to show mac table information is being collected
        usr_msg = "Comparing MAC and ARP tables and outputting results to csv"
        print(colorama.Fore.CYAN + usr_msg)   
        
        # iterate over arp_parse_dict dictionary items
        for mac_address, arp_parse_values in parsed_arp_table.items():
            
            # check if mac address from arp table is in mac address table
            if mac_address in parsed_mac_table:
            
                interface = parsed_mac_table[mac_address]['interface']
                ip_address = arp_parse_values['ip_address']
                
                # write information to csv log file
                mac_arp_csv_writer.writerow([device, mac_address, ip_address,
                                            interface])
        # disconnect from the device            
        net_connect.disconnect()
        
    # close csv log file
    mac_arp_csv.close()
        
    # message to the user about the mac arp parse ending
    usr_msg = "\nThe MAC ARP Parse script has completed running!\n"
        
    print(colorama.Fore.MAGENTA + usr_msg)

if __name__ == '__main__':
    mac_arp_parse()