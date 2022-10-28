import subprocess

result = subprocess.run(["/home/pi/.local/bin/brother_ql",
                    "--backend","pyusb",
                    "discover"])
print(result.stdout) 
