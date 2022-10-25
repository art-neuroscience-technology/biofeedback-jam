import subprocess

result = subprocess.run(["brother_ql",
                    "--backend","pyusb",
                    "discover"])
print(result.stdout) 
