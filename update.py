#!/usr/bin/env python3

import os
import sys
import subprocess

def get_pkg_names_from_args():
    names = []
    for arg in arg_list[1:]:
        names.append(arg)
    return names

def write_pkg_names_to_file(names):
    with open(path, "w") as file:
        for i in range(len(names)):
            file.write(names[i] + '\n')

def check_config_file(path):
    if os.path.exists(path):
        read_pkg_names_from_file()
        print("Config file exists. Prepare to update.")
        return 0
    else:
        print("File " + path + " not exist. Exit.")
        sys.exit(1)

def read_pkg_names_from_file():
    with open(path, "r") as file:
        pkg_names = file.readlines()
    return pkg_names

def main_func(comm):
    try:
        subprocess.run([comm], shell=True, check=True)
    except subprocess.CalledProcessError as error:
        sys.stderr.write(str(error))

def pre_update(update_type, remove):
    services = ['server', 'client']
    if update_type == 'client':
        main_func('systemctl stop rubackup_' + services[1])
    elif update_type == 'server':
        for i in services:
            main_func('systemctl stop rubackup_' + i)
    main_func(f'{remove} remove -y rubackup-common')
    os.system('rm -rf rub*')
    print("Environment is ready to update stand")

def wget_and_install(pkg_type, os_type, install, pkgs_list):
    for pkg in pkgs_list:
        main_func(f'wget 10.177.32.37:8080/latest/{pkg_type}/{os_type}/{pkg}')
        main_func(f'{install} -i {pkg}')

def rb_init(update_type):
    iface = input("Enter iface: ")
    if update_type == 'client':
        node_type = input('Choose type of client (client-server[c] / autonomous[a]): ')
        if node_type == 'c':
            primary_server = input("Enter hostname of primary server: ")
            main_func(f'rb_init -y -n client -c {primary_server} -i {iface} -l /rubackup-tmp')
        elif node_type == 'a':
            main_func(f'rb_init -y -n client -a /default')
    elif update_type == 'server':
        node_type = input("Choose type of server (primary[p] / media[m]): ")
        if node_type == 'p':
            main_func(f'rb_init -y -n primary-server -H localhost -X 12345 -Y 12345 -i {iface} -f /default_pool -l /rubackup-tmp')
        elif node_type == 'm':
            primary_server = input("Enter hostname of primary server: ")
            main_func(f'rb_init -y -n media-server -c {primary_server} -H {primary_server} -Y 12345 -i {iface} -l /rubackup-tmp')
    print('rb_init complete successfull')

def post_update(update_type):
    services = ['client', 'server']
    os.system('systemctl daemon-reload')
    if update_type == 'client':
        main_func('systemctl start rubackup_' + services[0])
    elif update_type == 'server':
        for i in services:
            main_func('systemctl start rubackup_' + i)

    print('Stand has been updated')

pkg_type, install, remove = 'deb', 'dpkg', 'apt'
arg_list = sys.argv
path = "/etc/qa_update_stand.conf"
os_type = input('Chose OS type (ubuntu_20.04/astra_1.7/astra_1.6): ')
update_type = input('Chose node type (server/client): ')

if len(arg_list) != 1:
    write_pkg_names_to_file(get_pkg_names_from_args())
    print("Packages names was write into qa_update_stand successfully")
else:
    check_config_file(path)
pre_update(update_type, remove)
wget_and_install(pkg_type, os_type, install, read_pkg_names_from_file())
rb_init(update_type)
post_update(update_type)








