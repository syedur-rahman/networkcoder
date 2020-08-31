""" netmiko bgp_neighbor_adv
parses the bgp neighbor table into one table and outputs results to csv """

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

#import ipaddress for network calculations
import ipaddress

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
        
def _parse_bgp_neighbor(raw_bgp_neighbor):
    """ _parse_bgp_neighbor
    parses the show ip bgp neighbor output and writes to the command prompt
    
    example:
    Neighbor 172.31.6.2 in state Established, has 3 routes has description  Router 3
    in New York, is in AS 65500, has a router ID of 10.2.0.1, and has been up for 0
    6:01:43
    """
    
    # initalize dictionary that will contain the bgp routing table information
    # of each device
    bgp_neighbor_dict = {}
    
    # description will not show up in show ip bgp neighbor unless it is set
    # so initialize variable so that it can be referenced in the event there
    # is no description
    description = ''
    bgp_neighbor_ip = ''
    
    # iterate over each line and check for interesting data
    for line in raw_bgp_neighbor.splitlines():
    
        # check if bgp_neighbor_ip has already been defined
        if bgp_neighbor_ip and 'bgp neighbor' in line.lower():
        
            # store information in dictionary
            #description will not show up in output if not set
            if not description:
                description = 'N/A'
                
            bgp_neighbor_dict[bgp_neighbor_ip] = {'bgp_neighbor': bgp_neighbor_ip,
                                        'bgp_state': bgp_state,
                                        'bgp_prefixes_received': bgp_prefixes_received,
                                        'description': description,
                                        'bgp_neighbor_as': bgp_neighbor_as,
                                        'router_id': router_id,
                                        'neighbor_uptime': neighbor_uptime
                                       }
            
            # Reset description parameter, as if this is user not set, the output
            # for description will not be shown
            description = ''
        
        # strip white space
        line = line.strip()
        
        # example line: Description: Router 2 in Las Vegas
        # obtain description from output
        if 'description' in line.lower():
            description = line.split(':')[1]
            continue
        
        # example line: BGP state = Established, up for 01:28:36
        # obtain bgp state from output
        elif 'bgp state' in line.lower():
            new_line = line.split(',')[0]
            bgp_state = new_line.split('=')[1].strip()
        
        # example line: Prefixes Total:     3       4
        # obtain advertised prefixes inbound and outbound from output
        elif 'prefixes total' in line.lower():
            parameters = line.split(':')
            parameters = parameters[1].split()
            bgp_prefixes_sent = parameters[0]
            bgp_prefixes_received = parameters[1]
            continue
        
        # example line: For address family: IPv4 Unicast
        # get address family from output
        elif 'address family' in line.lower():
            address_family = line.split(':')[1]
            continue
            
        # split based on white space
        parameters = line.split()
            
        # iterate over each parameter
        for parameter in parameters:
           
            # example line: BGP version 4, remote router ID 10.2.0.1
            if 'router id' in line.lower():
            
                if parameter.count('.') == 3:
                    router_id = parameter
                else:
                    continue
            
            # example line: BGP state = Established, up for 01:28:36
                
            elif 'bgp state' in line.lower() and parameter.count(':') >= 2:
                neighbor_uptime = parameter.replace(',','')
                continue
            # example line: BGP neighbor is 172.31.6.2,  remote AS 65500, external link
            elif 'bgp neighbor' in line.lower():
                
                if parameter.count('.') == 3:
                    bgp_neighbor_ip = parameter.replace(',','')
                    continue
                    
                elif parameter.replace(',','').isdecimal():
                    bgp_neighbor_as = parameter.replace(',','')
                    continue
    
    # store information in dictionary
    if not description:
        description = 'N/A'
        
    bgp_neighbor_dict[bgp_neighbor_ip] = {'bgp_state': bgp_state,
                                          'bgp_prefixes_received': bgp_prefixes_received,
                                          'description': description,
                                          'bgp_neighbor_as': bgp_neighbor_as,
                                          'router_id': router_id,
                                          'neighbor_uptime': neighbor_uptime
                                         }
    
    return bgp_neighbor_dict
                    
def arp_parse(raw_arp_table):
    """ arp parse
    parses the arp table output into a sorted dictionary 

    returns
    -------
    arp_parse_dict
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
        
        #iterate over parameters and check for mac address and ip address
        for parameter in line_parameters:
            # check for mac address
            if parameter.count('.') == 2:
                mac_address = parameter
                
            # check for ip address
            if parameter.count('.') == 3:
                ip_address = parameter
        
        # store information into a dictionary for easy access
        if mac_address and ip_address:
            arp_parse_dict[ip_address] = {'mac_address': mac_address}
            
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
    
    # initalize dictionary that will contain the arp information
    # of each device
    mac_parse_dict = {}
    
    for line in raw_mac_table.splitlines():
        #define variables so that dictionary doesn't error out
        interface = ''
        mac_address = ''
        
        # split based on white space
        line_parameters = line.split()
        
        #iterate over parameters and check for mac address and interface
        for parameter in line_parameters:
        
            # check for mac address
            if parameter.count('.') == 2:
                mac_address = parameter
            
            #check for interface
            if '/' in parameter.lower() or 'vlan' in parameter.lower():
                interface = parameter
                
        #store information into a dictionary for easy access
        if interface and mac_address:
            mac_parse_dict[mac_address] = {'interface': interface}
            
    return mac_parse_dict
        
def mac_arp_compare(raw_mac_table, host, raw_arp_table=''):
    """mac_arp_compare
    compares mac table and arp table to trace down a host
    
    returns
    -------
    host_dict
    dict representing the data of the traced host
    contains the keys and values for the interface and mac address

    example format listed below:
    {'interface': 'FastEthernet1/0', 'mac_address': '0050.7966.6800'}
    """
    
    interface = ''
    host_dict = {}
    
    # message to user to show mac and arp table are being compared
    # to get the interface the host mac address is appearing on
    usr_msg = "Retrieving interface for neighbor " + host + "...."
    print(colorama.Fore.CYAN + usr_msg)
    
    # initiate mac parse function to get formatted version 
    # of mac address table
    mac_address_dict = mac_parse(raw_mac_table=raw_mac_table)
    
    # check if host address format is a MAC address
    if host.count('.') == 2:
    
        #check if traced mac address is in mac address table
        if host in mac_address_dict:
            interface = mac_address_dict[host]['interface']
            host_dict = {'mac_address':  host, 
                         'interface': interface
                        }
    
    # check if host address format is an IP address         
    elif host.count('.') == 3:
        
        #initiate arp parse function to get formatted version of arp table
        arp_table_dict = arp_parse(raw_arp_table=raw_arp_table)
        
        #iterate over arp_parse_dict dictionary items
        for ip_address, arp_parse_values in arp_table_dict.items():
            mac_address = arp_parse_values['mac_address']
        
            if host not in ip_address:
                continue
                
            #check if mac address from arp table is in mac address table
            if mac_address in mac_address_dict:
            
                interface = mac_address_dict[mac_address]['interface']
                host_dict = {'mac_address': mac_address, 'interface': interface}
                break
                
    # if interface wasn't matched, exit script as it's impossible
    # to track down the host
    if not interface:
        usr_msg = 'Host not found in ARP or MAC table.'
        usr_msg += ' Please double check the host'
        print(colorama.Fore.RED + usr_msg)
    
    # Return empty values if mac address is not found for a bgp neighbor ip,
    # as it's possible the neighbor currently isn't up
    if not host_dict:
        host_dict = {'interface': 'N/A', 'mac_address': 'N/A'}
        
    return host_dict          
        
            
def bgp_neighbor_adv():
    """ main
    main function that is the catalyst of the script by executing all
    other functions """
    
    # message to the user about the mac arp parse script
    usr_msg = "# BGP Neighbor Advanced - Netmiko Edition"
    usr_msg += "\n# Logs into a set of devices and outputs bgp neighbor and interface information\n"
    print(colorama.Fore.YELLOW + usr_msg)
    
    # get user credentials
    username, password, secret = _get_user_credentials()
    
    # build devices list
    devices = _read_file('devices.txt')
    
    # get log filename
    log_filename = input('\nPlease provide an output filename: ').strip()
        
    # check if log file name ends with csv
    if not log_filename.endswith('.csv'):
        log_filename = log_filename + '.csv'
        
    # open csv log file
    bgp_neighbor_csv = open(log_filename, 'w', newline='')
        
    # initialize csv writer
    bgp_neighbor_csv_writer = csv.writer(bgp_neighbor_csv)
    
    # write header for csv file
    bgp_neighbor_csv_writer.writerow(['Device', 'BGP Neighbor IP', 'Interface',
                                      'Router ID', 'State', 'Prefixes Received',
                                      'Neighbor AS', 'Uptime', 'Description'])
                                      
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

            usr_msg = "\nAuthentication Failure - Exiting BGP Parse.\n"
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
            usr_msg += " Does Not Exist - Exiting BGP Neighbor Adv.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit program
            return
            
        # enter enable mode if required
        if net_connect.find_prompt().endswith('>'):
            net_connect.enable()
            
        # message to user to show bgp route information is being collected
        usr_msg = "Collecting BGP Neighbor Information...."
        print(colorama.Fore.CYAN + usr_msg)
                
        # collect unformatted bgp neighbor information using netmiko
        raw_bgp_neighbor = net_connect.send_command('show ip bgp neighbor')
        
        # parse raw output of bgp neighbor table
        bgp_neighbor_dict = _parse_bgp_neighbor(raw_bgp_neighbor)
        
        # Retrieve ARP table
        raw_arp_table = net_connect.send_command('show ip arp')
            
        # Retrieve CAM Table
        raw_mac_table = net_connect.send_command('show mac-address-table')
            
        #check if command syntax is wrong for mac address table
        #(command differs on IOS and IOS-XE/NXOS)
        if 'invalid input' in raw_mac_table.lower():
            
            #try different syntax for mac address table
            raw_mac_table = net_connect.send_command('show mac address-table')
        
        for bgp_neighbor_ip, bgp_neighbor_info in bgp_neighbor_dict.items():
        
            #initiate mac_arp_compare function to retrieve
            host_dict = mac_arp_compare(raw_mac_table = raw_mac_table,
                                             raw_arp_table = raw_arp_table,
                                             host = bgp_neighbor_ip
                                            )
            
            # write retrieved information to csv file
            bgp_neighbor_csv_writer.writerow([device, bgp_neighbor_ip, host_dict['interface'],
                                              bgp_neighbor_info['router_id'],
                                              bgp_neighbor_info['bgp_state'],
                                              bgp_neighbor_info['bgp_prefixes_received'],
                                              bgp_neighbor_info['bgp_neighbor_as'],
                                              bgp_neighbor_info['neighbor_uptime'], 
                                              bgp_neighbor_info['description']
                                             ])
                
        # message to user to show bgp neighbor information is done being collected
        usr_msg = "Done!"
        print(colorama.Fore.CYAN + usr_msg)
                
        # disconnect from the device            
        net_connect.disconnect()
        
    # message to the user about the mac arp parse ending
    usr_msg = "\nThe BGP Neighbor Advanced script has completed running!\n"
        
    print(colorama.Fore.MAGENTA + usr_msg)

if __name__ == '__main__':
    bgp_neighbor_adv()