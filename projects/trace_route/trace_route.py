""" netmiko mac arp parse
parses the mac and arp tables into one table and outputs results to csv """

# import connection library
import netmiko

# import cli coloring library
import colorama

# import input library for passwords
import getpass

#import ipaddress for network calculations
import ipaddress

#import sys library
import sys

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

            # set secret and password as the same
            secret = password

        # return the username and password
        return username, password, secret
        
class TraceRoute():
    """ TraceRoute
    logs into specified routers and tracks down a network to an interface
    Note: assumes CDP is running 
        
    """
        
    def __init__(self):
        """__init__
        initializing function to intiate the credentials and
        pass it to multiple functions within the script
        """
    
        # get user credentials
        self.username, self.password, self.secret = _get_user_credentials()

    def switch_login(self, device, device_type):
        """ switch_login
        logins into a given switch using netmiko 
        
        """
        
        # provide context for user
        usr_msg = "\nConnecting to " + device.upper()
        print(colorama.Fore.CYAN + usr_msg)
        
        # initialize device type
        # by default set to cisco ios to play it safe
        device_type = 'cisco_ios'
        
        # provide context for user
        usr_msg = "\n# Running Commands Against: " + device.upper()
        print(colorama.Fore.CYAN + usr_msg)

        # build netmiko device profile
        network_device_profile = {
            'device_type': device_type,
            'ip': device,
            'username': self.username,
            'password': self.password,
            'secret': self.secret,
        }

        # initialize the connection handler of netmiko
        try:
            self.net_connect = netmiko.ConnectHandler(**network_device_profile)
            
           # in case of authentication failure
        # user will be informed and the program will exit
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            # in case there were any successfully collected
            # data in the previous network devices
            # write to the log file to successfully save

            usr_msg = "\nAuthentication Failure - Exiting Trace Route.\n"
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
            usr_msg += " Does Not Exist - Exiting Trace Route.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit program
            return
            
        # enter enable mode if required
        if self.net_connect.find_prompt().endswith('>'):
            self.net_connect.enable()
            
    def arp_parse(self, raw_arp_table):
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
        
    def mac_parse(self, raw_mac_table):
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
            
    def mac_arp_compare(self, raw_mac_table, host, raw_arp_table=''):
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
        usr_msg = "Comparing MAC and ARP Table Information"
        print(colorama.Fore.WHITE + usr_msg)
        
        # initiate mac parse function to get formatted version 
        # of mac address table
        mac_address_dict = self.mac_parse(raw_mac_table=raw_mac_table)
        
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
            arp_table_dict = self.arp_parse(raw_arp_table=raw_arp_table)
            
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
            #self.switch_logout()
            sys.exit()
            
        return host_dict
        
    def _parse_routing_table(self, raw_routing_table):
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
        
        #dictionary for routing protocols consisting
        # of cisco codes to increase readability
        routing_protocols_dict = {'C': 'Connected', 'S': 'Static', 'R': 'RIP',
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
        
        for line in raw_routing_table.splitlines():
        
            # define variables so that dictionary doesn't error out
            src_network = ''
            dst_interface = ''
            
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
                        if 'gateway' not in line.lower():
                            src_network = src_network + '/' + mask
                
                # if src_network is already defined, parameter must be 
                # destination ip address
                elif parameter.count('.') == 3 and src_network:
                    if not dst_interface:
                        #strip comma out of output in the event that it's there
                        # ex: D 172.31.0.0/16 [90/284160] via 172.31.6.1, 03:53:03, Vlan6
                        dst_interface = parameter.replace(',','')
                    
                # check for interface if it's not an ip address 
                if '/' in parameter or 'vlan' in parameter.lower() or 'loopback' in parameter.lower():
                    if not dst_interface:
                
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
        
    def cdp_neighbors(self, interface):
        """cdp neighbors
        gets cdp neighbor information based on the interface
        
        returns
        -------
        ip_address
        string that contains the ip address from 
        show cdp neighbors detail output for a specific interface
        
        example:
        '192.168.1.1'
        
        device_type
        string that contains the device type from
        show cdp neighbors detial output for a specific interface
        
        example:
        'cisco_xe'
        
        """
        #message to user to show cdp neighbors info is being collected
        usr_msg = "Checking if interface is in cdp table"
        print(colorama.Fore.WHITE + usr_msg)
    
        #create syntax for command
        if interface:
            command = 'show cdp neighbors ' + interface + ' detail'
        else:
            command = 'show cdp neighbors'
        
        #send command and save output
        cdp_output = self.net_connect.send_command(command)
            
        if 'invalid input' in cdp_output.lower():
            #create syntax for command
            if interface:
                command = 'show cdp neighbors interface ' + interface
                command += ' detail'
            else:
                command = 'show cdp neighbors'
                
            #send command and save output
            cdp_output = self.net_connect.send_command(command)
        
        # Script relies on CDP, so if there is no cdp output for said interface
        # Exit out and indicate to user that network couldn't be traced past this
        # device
        if not cdp_output:
            usr_msg = "Network couldn't be traced past interface " + interface
            usr_msg += ' on router ' + self.device
            print(colorama.Fore.RED + usr_msg)
            sys.exit()
        
        for line in cdp_output.splitlines():

            # split based on white space
            line_parameters = line.split()
            
            #iterate over parameters and check for device type and ip address
            for parameter in line_parameters:
            
            # check for ip address
                if parameter.count('.') == 3:
                    ip_address = parameter
            
            # check for device type
                if 'NX-OS' in parameter:
                    device_type = 'cisco_nxos'
                
                elif 'IOS-XE' in parameter:
                    device_type = 'cisco_xe'
                
                elif 'IOS' in parameter:
                    device_type = 'cisco_ios'
                    
                else:
                    continue
                        
        # Check if CDP information contained an ip address and 
        # could be matched with a valid device type
        if ip_address and device_type:
            usr_msg = 'Next hop is interface ' + interface
            usr_msg += ' on switch ' + ip_address
            print(colorama.Fore.WHITE + usr_msg)
            return ip_address, device_type
            
    def _find_interface(self, parsed_routing_table, trace_network):
        """ _find_interface
        loops through parsed_routing_table dictionary to find
        an interface associated with the network, potentially
        performing several lookups
        
        returns
        ---------------
        interface
        string that contains the interface for the next hop of
        the network that is being traced
        
        """
        
        # transform user defined network that is being traced
        # into IPv4Interface in ipaddress module
        trace_subnet = ipaddress.IPv4Interface(trace_network)
        
        # initialize variable that will contain the best network match
        # with the smallest CIDR
        best_network_match = ''
        
        while True:
        
            # create supernet dictionary to store all potential supernets
            # for the network being traced
            supernet = {}
            
            for network, value in parsed_routing_table.items():
                
                #transform network into IPv4Interface in ipaddress module
                check_network = ipaddress.IPv4Interface(network)
                
                routing_protocol = value['routing_protocol']
                
                # iterate over dst_interface array and return first result
                # doesn't matter which one is chosen because if there's multiple
                # peers advertising the same network, they both should have paths
                # to the advertised network
                interface = value['dst_interface'][0]
                
                # check for an exact match of network
                
                if check_network.network == trace_subnet.network:
                
                    # check if network is a directly connected network
                    if 'connected' in routing_protocol.lower():
                        usr_msg = "Network " + str(trace_subnet.network)
                        usr_msg += " exists on router " + self.device
                        print(colorama.Fore.GREEN + usr_msg)
                        sys.exit()
                       
                    if interface.count('.') == 3 and '/' not in interface:
                    
                        trace_subnet = ipaddress.IPv4Interface(interface)
                        trace_network = interface
                
                # use ipaddress module to compare networks and see if
                # the network in the ip routing table is a supernet that contains
                # the network we're looking for
                elif trace_subnet in check_network.network:
                
                    if trace_network not in supernet.keys():
                        supernet[network] = {'routing_protocol': routing_protocol,
                                             'interface': interface}
            
            #check if supernet dictionary exists, otherwise
            # there are no routes for this network so consider
            # the network impossible to trace
            if supernet:
            
                # check if there is more than one supernet that this network
                # could be a part of in the routing table and then retrieve
                # smallest CIDR out of all of them (best match)
                if len(supernet.keys()) > 1:
                
                    for supernet_network in supernet.keys():
                    
                       supernet_network = ipaddress.IPv4Network(supernet_network)
                       
                       # if best_network_match isn't defined, set it equal to
                       # supernet_network since this is most likely
                       # the first value
                       if not best_network_match:
                           best_network_match = ipaddress.IPv4Network(supernet_network)
                           
                        
                       # compare prefix lengths - the largest prefix is stored
                       # this is so the smallest network mask is
                       if int(best_network_match.prefixlen) < int(supernet_network.prefixlen):
                            best_network_match = supernet_network
                            print(best_network_match)
                            
                    # store the recursive lookup values
                    trace_network = best_network_match
                    trace_subnet = ipaddress.IPv4Interface(best_network_match)
                
                # if there is only one supernet, can immediately determine
                # what the best network is since there's only one
                else:
                    # iterate through dictionary
                    for key, value in supernet.items():
                        best_network_match = key
                        
                        # if 'vlan' or '/' or 'loopback' are the interfaces,
                        # it means the interfaces are attached so we are done
                        # with the routing table on this router
                        if 'vlan' in value['interface'].lower() or '/' in value['interface'] \
                         or 'loopback' in value['interface'].lower():
                         
                            return trace_network, value['interface']
                        
                        # store recursive lookup values as new network to trace
                        # as it's not an attached device
                        trace_network = value['interface']
                        trace_subnet = ipaddress.IPv4Interface(interface)
                
            elif '/' not in trace_network or '/32' in trace_network:
                continue
            
            # Consider network to be impossible to trace
            else:
                print(colorama.Fore.RED + "Found no supernet for network " + trace_network)
                sys.exit()
                
        
    def trace_route(self, device, device_type, trace_network):
        """ trace_route
        main function in TraceRoute class that is the catalyst
        of the script by executing all other functions 
        
        """
        
        # store for later use
        self.device = device
        
        # store for later use
        self.trace_network = trace_network
        
        #log into switch
        self.switch_login(device=device, device_type=device_type)
                
        # message to user to show routing table information is being collected
        usr_msg = "Collecting Routing Table Information...."
        print(colorama.Fore.CYAN + usr_msg)
                
        # collect unformatted routing table information
        raw_routing_table = self.net_connect.send_command('show ip route')
        
        # parse raw output of routing table
        parsed_routing_table = self._parse_routing_table(raw_routing_table)
        
        trace_subnet, interface = self._find_interface(parsed_routing_table=parsed_routing_table,
                                                      trace_network = trace_network)
                                         
        if 'vlan' or 'loopback' in interface.lower():
            # convert host ip to not include CIDR
            # ex: 172.31.3.1/32 -> 172.31.3.1
            host = ipaddress.IPv4Network(trace_subnet)
            host = str(host[0])
            
            # log for user to know that it's checking MAC and ARP
            # table for the next hop since the destination interface
            # was a loopback or vlan and not a port
            print(f"Checking MAC and ARP Table for next hop {host}")
            
            # Retrieve ARP table
            raw_arp_table = self.net_connect.send_command('show ip arp')
            
            # Retrieve CAM Table
            raw_mac_table = self.net_connect.send_command('show mac-address-table')
            
            #check if command syntax is wrong for mac address table
            #(command differs on IOS and IOS-XE/NXOS)
            if 'invalid input' in raw_mac_table.lower():
            
                #try different syntax for mac address table
                raw_mac_table = self.net_connect.send_command('show mac address-table')
                
            #initiate mac_arp_compare function to retrieve 
            host_dict = self.mac_arp_compare(raw_mac_table = raw_mac_table,
                                             raw_arp_table = raw_arp_table,
                                             host = host
                                            )
                
        # retrieve ip address and device type from cdp output
        ip_address, device_type = self.cdp_neighbors(interface = host_dict['interface'])
        
        # log out of previous switch           
        self.net_connect.disconnect()
        
        # log into new router IP obtained from cdp output
        self.trace_route(device=ip_address, device_type=device_type,
                         trace_network=trace_network)
                
        # message to user to show routing table information is done being collected
        usr_msg = "Done!"
        print(colorama.Fore.CYAN + usr_msg)
            
        # message to the user about the route trace ending
        usr_msg = "\nThe Route Trace script has completed running!\n"
            
        print(colorama.Fore.MAGENTA + usr_msg)
    
def main():
    """ main
    initial function that is executed if this file is run and initiates
    trace_route function in TraceRoute class
        
    """
    # message to the user about the Host Trace script
    usr_msg = "# Trace Route"
    usr_msg += "\n# Trace networks to their native locations easily!\n"
    print(colorama.Fore.YELLOW + usr_msg)
    
    # ask user for network input
    # Example Network format: 172.31.0.0/16
    usr_msg = '\nPlease provide network trace details.'
    print(usr_msg)
    network = input('Network to trace (ex: 172.31.2.0/24): ')
    
    # ask user for a router IP or hostname
    device = input('Router IP address or Hostname: ')
    
    #ask user for device_type
    device_type = input('L3 Network Device Type (default: cisco_ios):')
    print('\n\n')

    # initialize the Route Parse class
    trace_route = TraceRoute()
    
    if not device_type:
        # initialize device type
        # by default set to cisco ios to play it safe
        device_type = 'cisco_ios'

    trace_route.trace_route(device=device, device_type=device_type, trace_network=network)
      
    # message to the user about the Trace Route script ending
    usr_msg = "\nThe Trace Route script has completed running!\n"
        
    print(usr_msg)

if __name__ == '__main__':
    main()