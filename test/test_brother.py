import subprocess

result = subprocess.run(["sudo", "/home/pi/.local/bin/brother_ql",
                    "--backend","pyusb",
                    "discover"])
print(result.stdout) 
