""" netmiko host trace
Traces hosts to their interfaces using netmiko and cdp """

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
        usr_msg = "\nPlease provide your credentials."
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
            print(colorama.Fore.WHITE + usr_msg)

            # set secret and password sa the same
            secret = password

        # return the username and password
        return username, password, secret

class HostTrace:
    """ HostTrace
    logs into specified switches and tracks down a mac address to an interface
    Note: assumes CDP is running """

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

            usr_msg = "\nAuthentication Failure - Exiting Quick Deploy.\n"
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
                arp_parse_dict[mac_address] = {'ip_address': ip_address}
                
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
            for mac_address, arp_parse_values in arp_table_dict.items():
                if host not in arp_parse_values['ip_address']:
                    continue
                    
                #check if mac address from arp table is in mac address table
                if mac_address in mac_address_dict:
                
                    interface = mac_address_dict[mac_address]['interface']
                    ip_address = arp_parse_values['ip_address']
                    host_dict = {'mac_address': mac_address, 'interface': interface}
                    break
                    
        # if interface wasn't matched, exit script as it's impossible
        # to track down the host
        if not interface:
            usr_msg = 'Host not found in ARP or MAC table.'
            usr_msg += ' Please double check the host'
            print(colorama.Fore.RED + usr_msg)
            self.switch_logout()
            sys.exit()
            
        return host_dict
    
    def cdp_neighbors(self, interface):
        """cdp neighbors
        gets cdp neighbor information based on interface
        
        returns
        -------
        cdp_output
        string that contains show cdp neighbors detail output for
        a specific interface
        
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
        
        return cdp_output
        
    def host_trace(self, device, device_type, host):
        """ host_trace
        main function in HostTrace class that is the catalyst 
        of the script by executing all other functions
        
        """
        #log into switch
        self.switch_login(device=device, device_type=device_type)
            
        # enter enable mode if required
        if self.net_connect.find_prompt().endswith('>'):
            self.net_connect.enable()
            
        # check if switch is in enable mode
        if self.net_connect.find_prompt().endswith('#'):
        
            # message to user to show arp table information is being collected
            usr_msg = "Collecting ARP Table Information"
            print(colorama.Fore.WHITE + usr_msg)
            
            #send command to device to get arp table information
            raw_arp_table = self.net_connect.send_command('show ip arp')
            
            # message to user to show mac table information is being collected
            usr_msg = "Collecting MAC Table Information"
            print(colorama.Fore.WHITE + usr_msg)
            
            #send command to device to get mac address table information
            raw_mac_table = self.net_connect.send_command('show mac-address-table')
        
        #check if command syntax is wrong for mac address table
        #(command differs on IOS and IOS-XE/NXOS)
        if 'invalid input' in raw_mac_table.lower():
        
            #try different syntax for mac address table
            raw_mac_table = self.net_connect.send_command('show mac address-table')
        
        #initiate mac_arp_compare function
        host_dict = self.mac_arp_compare(raw_mac_table=raw_mac_table, 
                             raw_arp_table=raw_arp_table,
                             host = host
                             )
        #initiate cdp_neighbors function
        cdp_output = self.cdp_neighbors(interface = host_dict['interface'])
        ip_address = ''
        
        if not cdp_output:
            usr_msg = "MAC address is connected to interface " + host_dict['interface']
            usr_msg += ' on switch ' + device
            print(colorama.Fore.GREEN + usr_msg)
            self.switch_logout()
            return
        
        for line in cdp_output.splitlines():

            # split based on white space
            line_parameters = line.split()
            
            #iterate over parameters and check for device type and ip address
            for parameter in line_parameters:
            
            # check for ip address
                if parameter.count('.') == 3:
                    ip_address = parameter
                    
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
            usr_msg = "Next hop is interface " + host_dict['interface']
            usr_msg += ' on switch ' + ip_address
            print(colorama.Fore.WHITE + usr_msg)
            self.host_trace(device=ip_address, device_type=device_type, host=host)
        
    def switch_logout(self):
        """switch_logout
        uses netmiko to log out of a switch"""
        
        # disconnect from the device
        self.net_connect.disconnect()
                
def main():
    """ main
    initial function that is executed if this file is run and initiates
    host_trace function in HostTrace class
        
    """
    # message to the user about the Host Trace script
    usr_msg = "# Host Trace - Netmiko Edition"
    usr_msg += "\n# Trace hosts to their interfaces easily!\n"
    print(colorama.Fore.YELLOW + usr_msg)
    
    # ask user for host input
    # Example MAC Address format: 0050.7966.6800
    usr_msg = '\nPlease provide host trace details.'
    print(usr_msg)
    host = input('IP Address or MAC Address to trace:')
    
    # ask user for a switch IP or hostname
    device = input('Switch IP address or Hostname: ')
    
    #ask user for device_type
    device_type = input('L3 Network Device Type (default: cisco_ios):')

    # initialize the Mac Arp Parse class
    host_trace = HostTrace()
    
    if not device_type:
        # initialize device type
        # by default set to cisco ios to play it safe
        device_type = 'cisco_ios'

    host_trace.host_trace(device=device, device_type=device_type, host=host)
      
    # message to the user about the Host Trace script ending
    usr_msg = "\nThe Host Trace script has completed running!\n"
        
    print(usr_msg)

if __name__ == '__main__':
    main()