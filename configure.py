"""
Configuration wizard for gpgchat.
"""

import gpgio
import subprocess

def configure():
    """
    Guides the user through creating a config.py file.
    """
    print("Welcome to gpgchat configuration!")

    # Get config filename
    config_filename = input("Enter a filename for this configuration (default: config.py): ") or "config.py"

    # Get server info
    server_hostname = input("Enter the server hostname (default: localhost): ") or "localhost"
    server_port = input("Enter the server port (default: 8387): ") or "8387"

    # Ask to create or use existing key
    signer_fingerprint = None
    create_new_key = input("\nDo you want to create a new GPG key? (y/n): ").lower() == 'y'

    if create_new_key:
        name = input("Enter your name: ")
        email = input("Enter your email address: ")
        batch_input = f"""
        %echo Generating a basic OpenPGP key
        Key-Type: RSA
        Key-Length: 2048
        Subkey-Type: RSA
        Subkey-Length: 2048
        Name-Real: {name}
        Name-Email: {email}
        Expire-Date: 0
        Passphrase: ""
        %commit
        %echo done
        """
        print("\nGenerating GPG key... This may take a moment.")
        result = subprocess.run(
            ['gpg', '--batch', '--gen-key'],
            input=batch_input,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("GPG key created successfully!")
            keys = gpgio.gpg.list_keys()
            for key in keys:
                if email in key['uids'][0]:
                    signer_fingerprint = key['fingerprint']
                    break
        else:
            print(f"Error generating GPG key: {result.stderr}")
            return
    else:
        keys = gpgio.gpg.list_keys()
        if not keys:
            print("No GPG keys found. Please create a key first.")
            return
            
        print("\nAvailable GPG keys:")
        for i, key in enumerate(keys):
            print(f"  {i+1}: {key['uids'][0]}")
        
        signer_index = -1
        while signer_index < 0 or signer_index >= len(keys):
            try:
                signer_index = int(input(f"Select a key for signing (1-{len(keys)}): ")) - 1
            except ValueError:
                pass
        
        signer_fingerprint = keys[signer_index]['fingerprint']

    # Get recipients
    recipients = []
    print("\nEnter recipient email addresses (one per line, press Enter on an empty line to finish):")
    while True:
        recipient = input("> ")
        if not recipient:
            break
        recipients.append(recipient)

    # Write config file
    with open(config_filename, "w") as f:
        f.write('"""\n')
        f.write("Client and server configuration.\n")
        f.write('"""\n\n')
        f.write(f'SERVER_HOSTNAME = "{server_hostname}"\n')
        f.write(f'SERVER_PORT = {server_port}\n\n')
        f.write('RECIPIENTS = [\n')
        for recipient in recipients:
            f.write(f'  "{recipient}",\n')
        f.write(']\n\n')
        f.write(f'SIGNER_FINGERPRINT = "{signer_fingerprint}"\n')

    print(f"\nConfiguration saved to {config_filename}!")

if __name__ == "__main__":
    configure()
