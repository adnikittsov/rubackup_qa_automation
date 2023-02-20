#!/usr/bin/env python3

import os
import sys
import subprocess

def main_func(comm):
    try:
        subprocess.run([comm], shell=True, check=True)
    except subprocess.CalledProcessError as error:
        sys.stderr.write(str(error))
        sys.exit(1)

def pre_update(update_type):
    services = ['server', 'client']
    try:
        if update_type == 'client':
            main_func('systemctl stop rubackup_' + services[1])
        elif update_type == 'server':
            for i in services:
                 main_func('systemctl stop rubackup_' + i)
    finally:
        main_func(f'apt remove -y rubackup-common')
        os.system('rm -f rub*')
def get_pkg_list(update_type):
    pkgs = ['rubackup-common', 'rubackup-client', 'rubackup-server', 'rubackup-rbm']
    if update_type == 'server':
        return pkgs
    elif update_type == 'client':
        pkgs = pkgs[:2]
        return pkgs

def create_wget_list(pkgs, os_type):
    pkg_list = []
    for pkg in pkgs:
        if os_type == 'ubuntu_20.04' or 'ubuntu_18.04':
            pkg_list.append(f"{pkg}.deb")
        elif os_type == 'astra_1.7' or 'astra_1.6':
            pkg_list.append(f"{pkg}_signed.deb")
    return pkg_list

def wget_and_install(os_type, pkgs_list):
    for pkg in pkgs_list:
        main_func(f'wget 10.177.32.37:8080/latest/deb/{os_type}/{pkg}')
        main_func(f'dpkg -i {pkg}')

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


def post_update(update_type):
    services = ['client', 'server']
    os.system('systemctl daemon-reload')
    if update_type == 'client':
        main_func('systemctl start rubackup_' + services[0])
    elif update_type == 'server':
        for i in services:
            main_func('systemctl start rubackup_' + i)

    print('Stand has been updated')



os_type = input('Chose OS type (ubuntu_20.04/ubuntu_18.04/astra_1.7/astra_1.6): ')
update_type = input('Chose node type (server/client): ')
pre_update(update_type)
wget_and_install(os_type, create_wget_list(get_pkg_list(update_type), os_type))
rb_init(update_type)
post_update(update_type)








