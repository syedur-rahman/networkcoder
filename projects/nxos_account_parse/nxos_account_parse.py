""" nxos account parse
generates a csv for the 'show accounting log' output
specifically for the cisco nexus switches """

# import connection library
import netmiko

# import cli coloring library
import colorama

# import input library for passwords
import getpass

# import the csv library
import csv

# import datetime
import datetime

# initialize colorama globally
# required for windows and optional for other systems
# additionally have colorama reset per print
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

def _parse_show_accounting_log(device_output):
    """ parse show accounting log
    helper function with the parsing logic for the show accounting log command

    returns
    -------
    parsed_data
        dict representing the parsed data of show accounting log
        will contain the date as key and user config data as values

        example format listed below:

        { '2019-01-01': { 'admin': [ config_line_1, config_line_2] } }
    """

    # initialize parsed data
    parsed_data = {}

    # iterate through the device output
    for line in device_output.splitlines():
        # skip if this was not a configuration update
        if 'configure' not in line:
            continue
        # skip if the configuration is not defined as success
        elif not line.strip().endswith('(SUCCESS)'):
            continue

        # remove the success tag of the line
        line = line.replace('(SUCCESS)', '')

        # cisco date format
        # this is the way cisco format's their date in the command
        cisco_date_format = '%a %b %d %H:%M:%S %Y:'

        # date of change date format
        date_of_change_date_format = '%Y-%m-%d'

        # determine date of change
        raw_date_from_line = line.split('type')[0]

        # convert raw date from show command to a datetime object
        date_object = datetime.datetime.strptime(raw_date_from_line, cisco_date_format)

        # convert datetime object to a string in the date of change date format
        date_of_change = date_object.strftime(date_of_change_date_format)

        # grab user from the line
        user = line.split(':')[-2].split('=')[-1]

        # grab change from the line
        change = line.split(';')[-1].strip()

        # for formatting, add spaces to command based off ';' in line
        number_of_spaces = line.count(';') - 1
        change = number_of_spaces*' ' + change

        # initialize parsed data with date of change
        if date_of_change not in parsed_data:
            parsed_data[date_of_change] = {}
        # initialize date of change with user
        if user not in parsed_data[date_of_change]:
            parsed_data[date_of_change][user] = []

        # add change the user did that day to the parsed data
        parsed_data[date_of_change][user].append(change)

    return parsed_data

def _save_parsed_data_to_csv(device, parsed_data):
    """ save parsed data to csv
    save the parsed data to csv which will be named after the device """

    # initialize csv headers
    headers = ['DATE', 'USER', 'CHANGE']

    # initialize filename
    filename = device + '.csv'

    with open(filename, 'w') as csv_file:
        # initialize csv writer
        csv_writer = csv.writer(csv_file)

        # write csv headers
        csv_writer.writerow(headers)

        # iterate through the parsed data where latest date goes on top
        for date_of_change, user_changes in reversed(sorted(parsed_data.items())):
            # iterate through the user changes
            for user, changes in user_changes.items():
                # build a full change string
                full_change = ''
                for change in changes:
                    full_change += change + '\n'
                full_change = full_change.strip()

                # initialize row
                row = [date_of_change, user, full_change]

                # write csv row
                csv_writer.writerow(row)

def nxos_account_parse():
    """ nxos account parse
    parses the accounting information on cisco nexus switches
    and generates a csv based off the parsed data for the user """

    usr_msg = "# NXOS Account Parse Script\n"
    usr_msg += "# Generate a CSV of all changes on a Cisco Nexus device!\n"
    print(colorama.Fore.YELLOW + usr_msg)

    # get credentials from the user
    try:
        username, password, secret = _get_user_credentials()

    # exit the script upon user keyboard interrupt
    except KeyboardInterrupt:
        usr_msg = "\n\nExiting Parse Script.\n"
        print(colorama.Fore.MAGENTA + usr_msg)

        return

    # keep running till user decides to exit out
    while True:
        # ask user for a nexus switch dns or ip
        usr_msg = "\nPlease provide nexus switch (type 'q' to quit): "
        usr_inp = input(usr_msg).strip().lower()
        
        # quit loop if conditions are met
        if usr_inp == 'q':
            break

        # assume user's input is device
        device = usr_inp

        # build netmiko device profile
        network_device_profile = {
            'device_type': 'cisco_nxos',
            'ip': device,
            'username': username,
            'password': password,
            'secret': secret,
        }

        # initialize the connection handler of netmiko
        usr_msg = "\nConnecting to " + device.lower()
        print(colorama.Fore.CYAN + usr_msg)
        try:
            net_connect = netmiko.ConnectHandler(**network_device_profile)

        # in case of authentication failure
        # user will be informed and the program will exit
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            usr_msg = "\nAuthentication Failure - Exiting Quick Deploy.\n"
            print(colorama.Fore.RED + usr_msg)

            # exit out of loop
            break

        # initialize show account log command
        command = 'show accounting log all'

        # capture device output from show command
        usr_msg = "\nRunning 'show accounting log all'"
        print(colorama.Fore.CYAN + usr_msg)
        device_output = net_connect.send_command(command)

        # disconnect from the nexus switch
        net_connect.disconnect()

        # parse the device output
        usr_msg = "\nParsing 'show accounting log all'"
        print(colorama.Fore.CYAN + usr_msg)
        parsed_data = _parse_show_accounting_log(device_output)

        # write parsed data to csv
        usr_msg = f"\nSaving parsed data to '{device.lower()}.csv'"
        print(colorama.Fore.CYAN + usr_msg)
        _save_parsed_data_to_csv(device, parsed_data)

    usr_msg = "\nExiting Parse Script.\n"
    print(colorama.Fore.MAGENTA + usr_msg)

if __name__ == '__main__':
    nxos_account_parse()