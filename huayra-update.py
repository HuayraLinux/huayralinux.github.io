#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import shutil

import apt
import apt.progress
import apt_pkg


SOURCES_LIST_PATH = ['/etc/apt/', '/etc/apt/sources.list.d/']
HUAYRA_REPO = 'http://repo.huayra.conectarigualdad.gob.ar/huayra'


regex_respuesta = "(y|s)"
regex_sourceslist = "*.list"


def es_root():
    """
    verifica si tiene uid(0)
    return: bool
    """
    return os.getuid() == 0


def sources_list():
    """
    devuelve listado de archivos con urls de repositorios
    return: list
    """
    sources_list = []
    for path in SOURCES_LIST_PATH:
        sources_list += glob.glob(os.path.join(path, regex_sourceslist))

    return filter(lambda x: len(x) > 0, sources_list)


def leer_sources_list(sources_list_file=None):
    """
    Lee un archivo sources.list
    return: list
    """
    with open(sources_list_file, 'r') as fd:
        renglones = fd.readlines()

    return renglones


def es_huayra():
    """
    verifica si estamos en Huayra
    return: bool
    """
    s_list = sources_list()
    es_huayra = False

    for s_l in s_list:
        renglones = leer_sources_list(s_l)
        renglones_clean = filter(lambda l: l.strip().startswith('#') == False, renglones)

        if renglones_clean:
            renglones_huayra = filter(lambda l: re.findall(HUAYRA_REPO, l), renglones_clean)

            if renglones_huayra:
                es_huayra = True

    return es_huayra


def es_brisa():
    """
    Verifica si ya tenemos los repositorios cambiados a `pampero`.
    return: bool
    """

    s_list = sources_list()
    es_brisa = False

    for s_l in s_list:
        renglones = leer_sources_list(s_l)
        renglones_clean = filter(lambda l: l.strip().startswith('#') == False, renglones)

        if renglones_clean:
            renglones_brisa = filter(lambda l: re.findall("brisa", l), renglones_clean)

            if renglones_brisa:
                es_brisa = True

    return es_brisa


def cambiar_repo():
    """
    Reemplaza en los archivos sources.list `brisa` por `pampero`.
    return: nil
    """
    s_list = sources_list()

    for s_l in s_list:
        s_l_backup = "%s.brisa" % s_l
        if not os.path.isfile(s_l_backup):
            shutil.copy2(s_l, s_l_backup)

        with open(s_l, 'r') as fd:
            renglones = fd.readlines()

        for index, data in enumerate(renglones):
            if 'brisa' in data and HUAYRA_REPO in data:
                renglones[index] = data.replace('brisa', 'pampero')

        with open(s_l, 'w') as fd:
            fd.write('\n'.join(renglones))


def actualizar_distro():
    """
    apt-get update && apt-get dist-upgrade
    return: nil
    """
    cache = apt.Cache()
    cache.update(apt.progress.text.AcquireProgress())
    cache.open(None)

    cache.upgrade(True)

    cache.commit(apt.progress.text.AcquireProgress(),
                 apt.progress.base.InstallProgress())


def actualizar_huayra():
    """
    Realiza los cambios necesarios para actualizar
    Huayra Brisa (v1.x) por Huayra Pampero (v2)
    return: nil
    """

    if not es_huayra():
        print('No estás usando Huayra.\n')
        sys.exit(1)

    else:
        if es_brisa():
            actualizar_distro()
            print('Brisa Update')

            cambiar_repo()
            print('cambia repo')

            actualizar_distro()
            print('listo')

        else:
            print('No hace falta modificar los repositorios de Huayra!')


def main(bienvenido=0):
    if bienvenido:
        print('+%s' % ('-'*80))
        print('| Bienvenido al actualizador de Huayra!')
        print('+%s' % ('-'*80))

    respuesta = raw_input('¿Desea continuar? (S)í/(N)o: ')
    if respuesta:
        if re.findall(regex_respuesta, respuesta[0].lower()):
            print('')
            actualizar_huayra()
    else:
        main()

if __name__ == '__main__':
    if es_root():
        actualizar_huayra()
        #main(1)

    else:
        print('El actualizador debe ser ejecutado como root o utilizando `sudo`.')
        print('Ej.: \n\t$ sudo huayra-update\n')
        sys.exit(1)
