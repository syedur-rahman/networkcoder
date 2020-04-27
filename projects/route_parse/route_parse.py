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
        
def _parse_routing_table(raw_routing_table):
    """ _parse_routing_table
    parses the routing table output into a sorted dictionary

    returns
    -------
    route_parse_dict
    dict representing the parsed data of routing table
    will contain the mac address as key and interface as values

    example format listed below:
    {'192.168.10.0/24' : {'dst_interface': ['FastEthernet1/0']} }

    """
    
    # initalize dictionary that will contain the routing table information
    # of each device
    route_parse_dict = {}
    
    for line in raw_routing_table.splitlines():
        # define variables so that dictionary doesn't error out
        src_network = ''
        dst_interface = ''
        
        #dictionary for routing protocols consisting
        # of cisco codes to increase readability
        routing_protocols_dict = {'C': 'Connected', 'S': 'static', 'R': 'RIP',
                                  'M': 'mobile', 'B': 'BGP', 'D': 'EIGRP', 
                                  'O': 'OSPF', 'IA': 'OSPF inter area',
                                  'N1': 'OSPF NSSA external type 1',
                                  'N2': 'OSPF NSSA external type 2',
                                  'E1': 'OSPF external type 1',
                                  'E2': 'OSPF external type 2',
                                  'i': 'IS-IS', 'su': 'IS-IS summary',
                                  'L1': 'IS-IS level-1', 'L2': 'IS-IS level-2',
                                  'ia': 'IS-IS inter area'
                                  }
        
        # split based on white space
        line_parameters = line.split()
        
        # iterate over parameters and check for network 
        for parameter in line_parameters:
        
            # check if routing protocol matches any of the keys in
            # routing_protocol_dict
            if parameter in routing_protocols_dict.keys():
                routing_protocol = routing_protocols_dict[parameter]
        
            #check for a condition in dynamic routing protocols where
            # network isn't defined if advertised by multiple peers
            # ex: O 10.2.0.1/32 [110/2] via 172.31.6.2, 04:44:06, Vlan6
            #                   [110/2] via 172.31.3.2, 04:44:06, Vlan3
            if 'via' in parameter.lower() and not src_network:
                src_network = dynamic_src_network
                routing_protocol = dynamic_routing_protocol
        
            # check for ip address syntax
            if parameter.count('.') == 3 and not src_network:
                src_network = parameter.replace(',','')
                
                # check for cisco syntax that specifies all the routes 
                # underneath are of the same mask so that the mask can 
                # be appended
                if '/' in parameter:
                
                    # store mask or entire network if there is certain verbiage
                    # in the routing table that denotes the mask or IP address
                    # is the same
                    if 'is subnetted' in line.lower() or 'via' in line.lower():
                        dynamic_src_network = src_network
                        dynamic_routing_protocol = routing_protocol
                        mask = parameter.split('/')[1]
                        
                # check if mask is defined along with ip address
                # if subnets are in the same classful network and have 
                # the same mask, mask might be omitted from routing table
                # ex: 172.31.0.0/24 is subnetted, 4 subnets
                #       C  172.31.3.0 is directly connected, Vlan3
                #       C  172.31.2.0 is directly connected, Vlan2

                elif '/' not in parameter:
                    src_network = src_network + '/' + mask
            
            # if src_network is already defined, parameter must be 
            # destination ip address
            elif parameter.count('.') == 3 and src_network and not dst_interface:
                #strip comma out of output in the event that it's there
                # ex: D 172.31.0.0/16 [90/284160] via 172.31.6.1, 03:53:03, Vlan6
                dst_interface = parameter.replace(',','')
                
            # check for interface if it's not an ip address 
            if '/' in parameter or 'vlan' in parameter.lower() and not dst_interface:
            
                # check to make sure this parameter is an interface and not
                # AD/cost parameter if it contains a slash
                if parameter.lower().islower():
                    dst_interface = parameter.replace(',','')
                
        # store information into a dictionary for easy access
        if dst_interface and src_network:
        
            # check if key already exists in the dictionary so that
            # a new array can be created or the existing array is appended
            if src_network not in route_parse_dict.keys():
                route_parse_dict[src_network] = {'dst_interface': [dst_interface],
                                                 'routing_protocol': routing_protocol}
                
            else:
                route_parse_dict[src_network]['dst_interface'].append(dst_interface)
                
    return route_parse_dict
            
def route_parse():
    """ main
    main function that is the catalyst of the script by executing all
    other functions """
    
    # message to the user about the mac arp parse script
    usr_msg = "# Route Parse - Netmiko Edition"
    usr_msg += "\n# Generates a CSV of all routes in the routing table!\n"
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
    route_parse_csv = open(log_filename, 'w', newline='')
        
    # initialize csv writer
    route_parse_csv_writer = csv.writer(route_parse_csv)
    
    # write header for csv file
    route_parse_csv_writer.writerow(['Device', 'Network', 'Destination',
                                     'Routing Protocol'])
    
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
            
        # message to user to show mac table information is being collected
        usr_msg = "Collecting Routing Table Information...."
        print(colorama.Fore.CYAN + usr_msg)
                
        # collect unformatted routing table information
        raw_routing_table = net_connect.send_command('show ip route')
        
        # parse raw output of routing table
        parsed_routing_table = _parse_routing_table(raw_routing_table)
        
        # iterate over parsed_routing_table dictionary items
        for network, value in parsed_routing_table.items():
            
            # iterate over destination interfaces, in case there are multiple routes
            # to the same network in the routing table
            for dst_interface in value['dst_interface']:
            
                routing_protocol = value['routing_protocol']
                
                # write information to csv log file
                route_parse_csv_writer.writerow([device, network, dst_interface, 
                                                 routing_protocol])
                
        # message to user to show mac table information is done being collected
        usr_msg = "Done!"
        print(colorama.Fore.CYAN + usr_msg)
                
        # disconnect from the device            
        net_connect.disconnect()
        
    # close csv log file
    route_parse_csv.close()
        
    # message to the user about the mac arp parse ending
    usr_msg = "\nThe Route Parse script has completed running!\n"
        
    print(colorama.Fore.MAGENTA + usr_msg)

if __name__ == '__main__':
    route_parse()