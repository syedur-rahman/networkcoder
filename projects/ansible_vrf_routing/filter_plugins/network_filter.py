""" network filter
custom filters to parse through hostvars and vrf data """

import json

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
            'vrf_filter': self.vrf_filter,
            'network_filter': self.network_filter,
         }

        return filters

    def vrf_filter(self, data):
        """ vrf filter
        method to extract vrf information from device output """

        # initialize vrfs
        vrfs = []

        # iterate through the raw output
        for line in data['stdout_lines'][0][1:]:
            vrf = line.split()[0].strip()
            if vrf == 'default':
                continue
            vrfs.append(vrf)

        return vrfs

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
        if 'capture' in data:
            for output in data['capture']['results']:
                command_output = output['stdout_lines'][0]
                command = output['invocation']['module_args']['commands'][0]

                # write to the log data with the header format
                line_to_write = '~' * len(command)
                log_data += line_to_write + '\n'
                line_to_write = command
                log_data += line_to_write + '\n'
                line_to_write = '~' * len(command)
                log_data += line_to_write + '\n'

                # iterate through the command output
                # and write the output to the log data
                for line in command_output:
                    line_to_write = line
                    log_data += line_to_write + '\n'
        if 'non_vrf_capture' in data:
            output = data['non_vrf_capture']
            command_output = output['stdout_lines'][0]
            command = 'show ip route'

            # write to the log data with the header format
            line_to_write = '~' * len(command)
            log_data += line_to_write + '\n'
            line_to_write = command
            log_data += line_to_write + '\n'
            line_to_write = '~' * len(command)
            log_data += line_to_write + '\n'

            # iterate through the command output
            # and write the output to the log data
            for line in command_output:
                line_to_write = line
                log_data += line_to_write + '\n'

        return log_data

    def network_filter(self, data):
        """ network filter
        parses through the hostvars datastructure

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
        
        log_data = self._filter_data(data)

        return log_data