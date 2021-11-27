"""Setup script for octave_kernel package.
"""
import setuptools

setup_args = {}

data_files_spec = [
    ('share/jupyter/kernels/octave', 'octave_kernel', 'kernel.json'),
    ('share/jupyter/kernels/octave', 'octave_kernel/images', '*.png')
]

try:
    from jupyter_packaging import get_data_files
    setup_args['data_files'] = get_data_files(data_files_spec)

except ImportError:
    pass

setuptools.setup(**setup_args)
