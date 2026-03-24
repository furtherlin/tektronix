import usbtmc
import sys

# Replace these with your actual Vendor ID and Product ID (in hexadecimal)
VID = 0xF4EC  # Example VID 
PID = 0xEE38  # Example PID

try:
    # 1. Initialize the connection
    scope = usbtmc.Instrument(VID, PID)
    
    # Optional: Increase timeout for large data transfers (in milliseconds)
    scope.timeout = 5000 

    # 2. Verify connection by asking for the Identification string
    idn = scope.ask("*IDN?")
    print(f"Connected successfully to:\n{idn}\n")

    # 3. Ask the scope for a measurement on Channel 1
    # 'C1:PAVA? VPP' asks for the Peak-to-Peak voltage on Channel 1
    scope.write("C1:PAVA? VPP")
    vpp_response = scope.read()
    print(f"Channel 1 Measurement: {vpp_response}")

    # 4. (Optional) Requesting raw waveform data
    # scope.write("C1:WF? DAT2")
    # raw_waveform_data = scope.read_raw()
    # print(f"Received {len(raw_waveform_data)} bytes of waveform data.")

except usbtmc.usbtmc.UsbtmcException as e:
    print(f"USBTMC Error: Could not connect to the device. Check VID/PID and USB permissions.\nDetails: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
