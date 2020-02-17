""" network filter
custom filter to parse through the hostvars datastructure """

class FilterModule:

    def filters(self):
        """ filters
        this is how ansible references filters
        more than one filter can be built if desired

        returns
        -------
        filters
            dictionary variable representing each filter
            where key is name of filter and value is the method

         """

         # initialize filters
        filters = {
            'network_filter': self.network_filter
         }

        return filters

    def _filter_data(self, data):
        """ filter data
        helper method to filter hostvars switch data

        parameters
        ----------
        data : dict
            the dictionary of the facts of a device

        returns
        -------
        log_data
            str representing the output for the log file
            should there have been show command output

        """

        # initialize log data
        log_data = ''

        # if capture fact was not registered
        # exit out of method early with empty log data
        if 'capture' not in data:
            return log_data

        # if failed parameter does not exist
        # exit out of the method early with empty log data
        # side note - note sure if this condition is even possible!
        if 'failed' not in data['capture']:
            return log_data

        # check if the paramater of failed was set to false
        # double negative meaning the commands executed without issue
        if data['capture']['failed'] == False:
            # enumerate through the captured data output
            for i, command_output in enumerate(data['capture']['stdout_lines']):
                # grab the executed command of the captured data in question
                # this is the reason enumerate was used as the index of the 
                # executed command is the same index as the executed command's output
                command = data['device_commands'][i]

                # initialize the device's hostname
                ansible_host = data['ansible_host']

                # check length of the command output
                if len(command_output) == 1:
                    # if there is no data in the executed command's output
                    # skip writing the empty output to the log
                    if not command_output[0]:
                        continue

                # skip the command that starts with conf as well
                if command.strip().startswith('conf'):
                    continue

                # write to the log data with the header format
                line_to_write = '~' * len(ansible_host + " - " + command)
                log_data += line_to_write + '\n'
                line_to_write = ansible_host + " - " + command
                log_data += line_to_write + '\n'
                line_to_write = '~' * len(ansible_host + " - " + command)
                log_data += line_to_write + '\n'

                # iterate through the command output
                # and write the output to the log data
                for line in command_output:
                    line_to_write = line
                    log_data += line_to_write + '\n'

        return log_data

    def network_filter(self, hostvars, groups):
        """ network filter
        parses through the hostvars datastructure

        parameters
        ----------
        hostvars : dict
            the dictionary of the facts of all devices
            key is switch and value is a dictionary of facts for that switch

        groups : dict
            the dictionary of all groups based on the devices.yml file
            key is group name and value is a list of switches

        returns
        -------
        log_data
            str representing the output for the log file
            should there have been show command output

        """

        # initialize log data
        log_data = ''

        # group nxos data together
        for switch in groups['nxos']:
            data = hostvars[switch]
            log_data += self._filter_data(data)

        # group eos data together
        for switch in groups['eos']:
            data = hostvars[switch]
            log_data += self._filter_data(data)

        # group ios data together
        for switch in groups['ios']:
            data = hostvars[switch]
            log_data += self._filter_data(data)

        return log_data