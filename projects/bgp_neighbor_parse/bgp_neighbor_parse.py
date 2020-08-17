""" netmiko bgp_neighbor_parse
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
    bgp_neighbor_parse_dict = {}
    
    # description will not show up in show ip bgp neighbor unless it is set
    # so initialize variable so that it can be referenced in the event there
    # is no description
    description = ''
    bgp_neighbor_ip = ''
    
    # iterate over each line and check for interesting data
    for line in raw_bgp_neighbor.splitlines():
    
        # check if bgp_neighbor_ip has already been defined
        if bgp_neighbor_ip and 'bgp neighbor' in line.lower():
        
            # display information to user about bgp neighbors if there are more than one bgp neighbors
            display_msg = '\nNeighbor ' + bgp_neighbor_ip + ' in state ' + bgp_state
            display_msg += ', has ' + bgp_prefixes_received + ' routes'
            if description:
                display_msg += ', has description' + description + 'N/A'
            display_msg += ', is in AS ' + bgp_neighbor_as
            display_msg += ' has a router ID of ' + router_id
            display_msg += ', and has been up for ' + neighbor_uptime + '\n'
            
            # print output to command line
            print(colorama.Fore.CYAN + display_msg)
            
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
                    bgp_neighbor_as = parameter
                    continue
    
    # display information to user about bgp neighbor information
    display_msg = '\nNeighbor ' + bgp_neighbor_ip + ' in state ' + bgp_state
    display_msg += ', has ' + bgp_prefixes_sent + ' routes'
    
    # check if description is defined
    if description:
        display_msg += ' has description ' + description
    display_msg += ', is in AS ' + bgp_neighbor_as
    display_msg += ' has a router ID of ' + router_id
    display_msg += ', and has been up for ' + neighbor_uptime + '\n'
    
    # print output to command line
    print(colorama.Fore.CYAN + display_msg)
                    
                
            
            
def bgp_neighbor_parse():
    """ main
    main function that is the catalyst of the script by executing all
    other functions """
    
    # message to the user about the mac arp parse script
    usr_msg = "# BGP Neighbor Parse - Netmiko Edition"
    usr_msg += "\n# Logs into a set of devices and outputs bgp neighbor information\n"
    print(colorama.Fore.YELLOW + usr_msg)
    
    # get user credentials
    username, password, secret = _get_user_credentials()
    
    # build devices list
    devices = _read_file('devices.txt')
    
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
            usr_msg += " Does Not Exist - Exiting BGP Parse.\n"
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
        parsed_bgp_table = _parse_bgp_neighbor(raw_bgp_neighbor)
                
        # message to user to show bgp neighbor information is done being collected
        usr_msg = "Done!"
        print(colorama.Fore.CYAN + usr_msg)
                
        # disconnect from the device            
        net_connect.disconnect()
        
    # message to the user about the mac arp parse ending
    usr_msg = "\nThe BGP Neighbor Parse script has completed running!\n"
        
    print(colorama.Fore.MAGENTA + usr_msg)

if __name__ == '__main__':
    bgp_neighbor_parse()