from setuptools import setup
from setuptools.command.install import install
import json
import os
import sys


kernel_json = {"argv": [sys.executable, "-m", "octave_kernel", "-f",
                        "{connection_file}"],
               "display_name": "Octave",
               "language": "octave",
               "codemirror_mode": "Octave"
               }


class install_with_kernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        from IPython.kernel.kernelspec import KernelSpecManager
        from IPython.utils.path import ensure_dir_exists
        destdir = os.path.join(KernelSpecManager().user_kernel_dir, 'octave')
        ensure_dir_exists(destdir)
        with open(os.path.join(destdir, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)


with open('README.rst') as f:
    readme = f.read()

# get the library version from the file
with open('octave_kernel.py') as f:
    lines = f.readlines()
for line in lines:
    if line.startswith('__version__'):
        version = line.split()[-1][1:-1]

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='octave_kernel',
      version=version,
      description='An Octave kernel for IPython',
      long_description=readme,
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      url='https://github.com/blink1073/octave_kernel',
      py_modules=['octave_kernel'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['oct2py >= 2.0', 'IPython >= 3.0'],
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Shells',
      ]
)
