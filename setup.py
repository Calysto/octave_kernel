from distutils.command.install import install
from distutils.core import setup
import sys

kernel_json = {
    "argv": [sys.executable,
             "-m", "octave_kernel",
             "-f", "{connection_file}"],
    "display_name": "Octave",
    "language": "octave",
    "name": "octave_kernel",
}


class install_with_kernelspec(install):

    def run(self):
        install.run(self)
        from metakernel.utils import install_spec
        install_spec(kernel_json)


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

with open('octave_kernel.py', 'rb') as fid:
    for line in fid:
        line = line.decode('utf-8')
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

setup(name='octave_kernel',
      version=version,
      description='An Octave kernel for Jupyter/IPython',
      long_description=open('README.rst', 'r').read(),
      url="https://github.com/calysto/octave_kernel",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      license='MIT',
      py_modules=['octave_kernel'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=["metakernel >= 0.10.5", "IPython >= 3.0"],
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
      )
