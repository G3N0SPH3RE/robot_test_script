from . import mir_interface

if '__name__' == '__main__':
    mir = MiR(configuration_file_name='mir200_config.yaml')

# base64.encodestring(b'Distributor:'+hashlib.sha256(b'distributor').hexdigest().encode())