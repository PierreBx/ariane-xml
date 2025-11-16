"""
Entry point for running the Ariane-XML kernel
"""

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    from .kernel import ArianeXMLKernel

    IPKernelApp.launch_instance(kernel_class=ArianeXMLKernel)
