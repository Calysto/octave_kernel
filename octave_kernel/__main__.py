from ipykernel.kernelapp import IPKernelApp
from .kernel import OctaveKernel
IPKernelApp.launch_instance(kernel_class=OctaveKernel)
