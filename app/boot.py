# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc

"""Main function. Runs after board boot, before main.py
Connects to Wi-Fi and checks for latest git version.
"""
#gc.set_threshold(50000)
gc.collect()
gc.enable()





