#!/usr/bin/env python3

import os
import sys
import subprocess

def main_func(comm):
    try:
        subprocess.run([comm], shell=True, check=True)
    except subprocess.CalledProcessError as error:
        sys.stderr.write(str(error))

def pre_update(update_type):
    services = ['server', 'client']
    try:
        if update_type == 'client':
            main_func('systemctl stop rubackup_' + services[1])
        elif update_type == 'server':
            for i in services:
                 main_func('systemctl stop rubackup_' + i)
    finally:
        main_func(f'yum remove -y rubackup-common.x86_64')
        os.system('rm -f rub*')
        print("Environment is ready to update stand")

def get_build_num(os_num):

    main_func(f"wget 10.177.32.37:8080/latest/rpm/centos{os_num}")
    with open(f"centos{os_num}", "r") as file:
        for line in file.readlines():
            if 'rubackup' in line:
                build_num = ''
                line = line[28:]
                for elem in line:
                    if elem == '-':
                        break
                    else:
                        build_num += elem
                break
    main_func(f"rm -f centos{os_num}")
    return build_num

def get_pkg_list(update_type):
    if update_type == 'server':
        pkgs = ['rubackup-common', 'rubackup-client', 'rubackup-server', 'rubackup-rbm']
        return pkgs
    elif update_type == 'client':
        pkgs = ['rubackup-common', 'rubackup-client']
        return pkgs

def create_wget_list(pkgs, build_num, os_num):
    pkg_list = []
    for pkg in pkgs:
        pkg_list.append(f"{pkg}-{build_num}-1.el{os_num}.x86_64.rpm")
    return pkg_list

def wget_and_install(os_num, pkg_list):
    for pkg in pkg_list:
        main_func(f'wget 10.177.32.37:8080/latest/rpm/centos{os_num}/{pkg}')
        main_func(f'rpm -i {pkg}')

def rb_init(update_type):
    if update_type == 'client':
        node_type = input('Choose type of client (client-server[c] / autonomous[a]): ')
        if node_type == 'c':
            primary_server = input("Enter hostname of primary server: ")
            main_func(f'rb_init -y -n client -c {primary_server} -i ens18 -l /rubackup-tmp -r -R -g')
        elif node_type == 'a':
            main_func(f'rb_init -y -n client -a /default')
    elif update_type == 'server':
        node_type = input("Choose type of server (primary[p] / media[m]): ")
        if node_type == 'p':
            main_func(f'rb_init -y -n primary-server -H localhost -X 12345 -Y 12345 -i ens18 -f /default_pool -l /rubackup-tmp -r -R -g')
        elif node_type == 'm':
            primary_server = input("Enter hostname of primary server: ")
            main_func(f'rb_init -y -n media-server -c {primary_server} -H {primary_server} -Y 12345 -i ens18 -l /rubackup-tmp -r -R -g')

def post_update(update_type):
    services = ['client', 'server']
    os.system('systemctl daemon-reload')
    if update_type == 'client':
        main_func('systemctl start rubackup_' + services[0])
    elif update_type == 'server':
        for i in services:
            main_func('systemctl start rubackup_' + i)

os_num = input('Chose CentOS version [7 / 8]: ')
update_type = input('Chose node type (server/client): ')
pre_update(update_type)
wget_and_install(os_num, create_wget_list(get_pkg_list(update_type), get_build_num(os_num), os_num))
rb_init(update_type)
post_update(update_type)
