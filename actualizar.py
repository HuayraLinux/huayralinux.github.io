# -*- coding: utf-8 -*-

import os
import shutil
import re

import apt
import apt.progress

HUAYRA_VERSION_LIST = {
    '1.0': 'brisa',
    '2.0': 'pampero'
}


class HuayraUpdate(object):
    rutas = {
        'source.list': '/etc/apt/sources.list',
        'source.list_backup': '/etc/apt/sources.list.%s',
        'huayra_repo_url': 'http://repo.huayra.conectarigualdad.gob.ar/huayra',
        'huayra_version': '/etc/huayra_version'
    }

    def __init__(self, *args, **kwargs):
        if kwargs.get('rutas'):
            self.rutas = kwargs['rutas']

        self._source_list_backup = self.rutas['source.list_backup'] % (HUAYRA_VERSION_LIST[self.version_actual])
        self._version_destino = '2.0'


    @property
    def version_actual(self):
        if not hasattr(self, '_version_actual'):
            try:
                fd = open(self.rutas['huayra_version'], 'r')

            except IOError:
                self._version_actual = '1.0'

            else:
                with fd:
                    version = fd.readline()
                    m = re.match(r'(\d+\.\d*)', version)

                    self._version_actual = m.group(1)

        return self._version_actual

    def resguardar_repos(self):
        if not os.path.isfile(self._source_list_backup):
            shutil.copy2(self.rutas['source.list'], self._source_list_backup)

    def modificar_repos(self):
        with open(SOURCE_LIST, 'r') as fd:
            renglones = fd.readlines()

        for index, data in enumerate(renglones):
            if HUAYRA_VERSION_LIST['1.0'] in data and HUAYRA_REPO in data:
                renglones[index] = data.replace(HUAYRA_VERSION_LIST['1.0'], HUAYRA_VERSION_LIST['2.0'])

        with open(SOURCE_LIST, 'w') as fd:
            fd.write('\n'.join(renglones))



def actualizar_huayra():
    if not es_brisa():
        print('Ya estás usando la última versión disponible de Huayra!')

    else:
        if not os.path.isfile(SOURCE_LIST_BACKUP):
            shutil.copy2(SOURCE_LIST, SOURCE_LIST_BACKUP)

        actualizar_distro()
        print 'Brisa Update'

        cambiar_repo()
        print('cambia repo')

        actualizar_distro()
        print('listo')


def actualizar_distro():
    try:
        cache = apt.Cache()
        cache.update(apt.progress.text.AcquireProgress())
        cache.open(None)

        cache.upgrade(True)

        cache.commit(apt.progress.text.AcquireProgress(),
                     apt.progress.base.InstallProgress())
    except Exception, e:
        print e
        print dir(e)
        raise ''


if __name__ == '__main__':
    print('+----')
    print('| Bienvenido al actualizador de Huayra!')
    print('+----\n')

    if not os.access(SOURCE_LIST, os.W_OK):
        print(' El actualizador debe ser ejecutado como root.')
        print(' Ej.: $ sudo huayra-update\n')

    else:
        respuesta = raw_input('¿Desea continuar? (S)í/(N)o: ')
        if respuesta == 's':
            print('')
            actualizar_huayra()
