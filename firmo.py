#!/usr/bin/env python3.6

import os
import pexpect
import sys

# Put this script in the firmadyne path downloadable from
# https://github.com/firmadyne/firmadyne

#Configurations - change this according to your system
firmadyne_path = "/home/ec/firmadyne"
binwalk_path = "/usr/local/bin/binwalk"
firmwalker_path ="/usr/local/bin/firmwalker.sh"
root_pass = "root"
firmadyne_pass = "firmadyne"


def show_banner():
    print( """
                              
                            ###### # #####  #    #  ####  
                            #      # #    # ##  ## #    # 
                            #####  # #    # # ## # #    # 
                            #      # #####  #    # #    # 
                            #      # #   #  #    # #    # 
                            #      # #    # #    #  ####                    
                    
                Welcome to the Firmware Exploitation Tools Kit 
                            v1.0
                    http://husinul.github.io
                  By Husinul Sanub
    """)

def get_info():
    if len(sys.argv) == 2:
        firm_name = sys.argv[1]
        print("[?] Enter the name or absolute path of the firmware you want to analyse : " + firm_name)
    else:
        firm_name = input("[?] Enter the name or absolute path of the firmware you want to analyse : ")
    firm_brand = input("[?] Enter the brand of the firmware : ")
    return (firm_name, firm_brand)


def binwalk_extractor(firm_name):
    print("[+] Now going to extract the firmware. Hold on..")
    os.system("binwalk"+'\t'+firm_name)

def firmwalker():
        
        firm_extracted = input('Enter the Extracted firmware:')
        os.system("firmwalker.sh"+'\t'+firm_extracted )

def run_extractor(firm_name, firm_brand):
    print("[+] Now going to extract the firmware. Hold on..")
    print("[+] Firmware : " + firm_name)
    print("[+] Brand : " + firm_brand)       
    extractor_cmd = firmadyne_path + "/sources/extractor/extractor.py -b " + firm_brand + " -sql 127.0.0.1 -np -nk " + "\""+ firm_name + "\"" + " images "
    child = pexpect.spawn(extractor_cmd, timeout=None)
    child.expect("Database Image ID: ")
    image_id = child.readline().strip()
    print("[+] Database image ID : " + image_id)
    child.expect(pexpect.EOF)
    return image_id


def identify_arch(image_id):
    print("[+] Identifying architecture")
    identfy_arch_cmd = firmadyne_path + "/scripts/getArch.sh ./images/" + image_id + ".tar.gz"
    child = pexpect.spawn(identfy_arch_cmd)
    child.expect(":")
    arch = child.readline().strip()
    print("[+] Architecture : " + arch)
    child.expect("Password for user firmadyne: ")    
    child.sendline(firmadyne_pass)
    child.expect(pexpect.EOF)
    return arch


def tar2db(image_id):
    print("[+] Storing filesystem in database")
    tar2db_cmd = firmadyne_path + "/scripts/tar2db.py -i " + image_id + " -f " + firmadyne_path + "/images/" + image_id + ".tar.gz"
    output_tar2db = pexpect.run(tar2db_cmd)

    if "already exists" in output_tar2db:
        print("[!] Filesystem already exists")


def make_image(arch, image_id):
    print("[+] Building QEMU disk image")
    makeimage_cmd = "sudo " + firmadyne_path + "/scripts/makeImage.sh " + image_id + " " + arch
    child = pexpect.spawn(makeimage_cmd)
    child.sendline(root_pass)
    child.expect(pexpect.EOF)


def setup_network(arch, image_id):
    print("[+] Setting up the network connection, please standby")
    network_cmd = "sudo " + firmadyne_path + "/scripts/inferNetwork.sh " + image_id + " " + arch
    child = pexpect.spawn(network_cmd)
    child.sendline(root_pass)
    child.expect("Interfaces:", timeout=None)
    interfaces = child.readline().strip()
    print("[+] Network interfaces : " + interfaces)
    child.expect(pexpect.EOF)


def final_run(image_id):
    print("[+] Running the firmware finally")
    run_cmd = "sudo " + firmadyne_path + "/scratch/" + image_id + "/run.sh"
    print("[+] command line : " + run_cmd)
    input("[*] Press ENTER to run the firmware...")
    child = pexpect.spawn(run_cmd)
    child.sendline(root_pass)
    child.interact()    


def main():
    show_banner()
    
    #firm_name, firm_brand = get_info()
    while True:
        data = int(input("\n[?] which tool you want to use \n1.Binwalk\n2.Firmdyne\n3.Firmwalker\n4.Exit\n>>"))
        
        try:
            if data == 1:

                if not os.path.isfile(binwalk_path):
                    print("\n*******************\n" + binwalk_path + "\n" + "This Location does not exist or Module is not installed\n")
                else:
                    firm_name,firm_brand = get_info()    
                    binwalk_extractor(firm_name)
                    d=input('>> do u wanna use another tool ?')
                    
            
            elif data == 2:
                if not os.path.isfile(firmadyne_path):
                    print("\n*******************\n" + firmadyne_path + "\n" + "This Location does not exist or Module is not installed\n")
                else:
                    get_info()
                    image_id = run_extractor(firm_name, firm_brand)

                    if image_id == "":
                        print("[!] Something went wrong")
                    else:
                        arch = identify_arch(image_id)        
                        tar2db(image_id)
                        make_image(arch, image_id)        
                        setup_network(arch, image_id)        
                        final_run(image_id)
            
            elif data ==3:
                 if not os.path.isfile(firmwalker_path):
                    print("\n*******************\n" + firmwalker_path + "\n" + "This Location does not exist or Module is not installed\n")
                 else:   
                    firmwalker()
                    d =input('>> do u wanna use another tool ?')

            elif data ==4:
                print("\n\nThank you !!!") 
                break   
            else:
                raise  ValueError()       
        
        except ValueError:
            print("\nOops!  That was no valid number.  Try again...\n")
            
            

if __name__ == "__main__":
    main()
