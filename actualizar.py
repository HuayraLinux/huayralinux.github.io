# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys
import time

import apt
import apt.progress


HUAYRA_VERSION_LIST = {
    '1.0': 'brisa',
    '2.1': 'pampero'
}

RUTAS = {
    'source.list': '/etc/apt/sources.list',
    'source.list_backup': '/etc/apt/sources.list.%s',
    'huayra_repo_url': 'http://repo.huayra.conectarigualdad.gob.ar/huayra',
    'huayra_version': '/etc/huayra_version',
    'dpkg_preferences': '/etc/dpkg/dpkg.cfg.d/99_paloma',
    'mdm_preferences': '/etc/mdm/mdm.conf',
}

ACCESOS_ESCRITORIO = [
    '/home/%s/Escritorio/ayuda-mate.desktop',
    '/home/%s/Escritorio/huayra-bullets.desktop',
    '/home/%s/Escritorio/huayra-chat.desktop',
    '/home/%s/Escritorio/huayra-flash-install.desktop',
    '/home/%s/Escritorio/huayra-tda.desktop',
    '/home/%s/Escritorio/www-browser.desktop',
]


class HuayraUpdate(object):
    rutas = RUTAS

    def __init__(self, *args, **kwargs):
        if kwargs.get('rutas'):
            self.rutas = kwargs['rutas']

        self._cache = None

        self._source_list_backup = self.rutas['source.list_backup'] % (HUAYRA_VERSION_LIST[self.version_actual])
        self._version_destino = '2.1'


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

    @property
    def cache(self):
        if not self._cache:
            self._cache = apt.Cache()
            self._cache.update(apt.progress.text.AcquireProgress())
            self._cache.open(None)

        return self._cache

    def configuracion_apt(self, accion):
        if accion == 'crear':
            with open(RUTAS['dpkg_preferences'], 'w') as fd:
                fd.write('''force-confdef
force-confold
''')

        elif accion == 'borrar':
            os.unlink(RUTAS['dpkg_preferences'])

    def configuracion_mdm(self):
        with open(RUTAS['mdm_preferences'], 'w') as fd:
            fd.write('''[daemon]

Greeter=/usr/lib/mdm/mdmwebkit

[security]

[xdmcp]

[gui]

[greeter]

HTMLTheme=huayra_limbo

[chooser]

[debug]

[servers]
''')

    def resguardar_repos(self):
        if not os.path.isfile(self._source_list_backup):
            shutil.copy2(self.rutas['source.list'], self._source_list_backup)

    def modificar_repos(self):
        with open(self.rutas['source.list'], 'r') as fd:
            renglones = fd.readlines()

        for index, data in enumerate(renglones):
            if HUAYRA_VERSION_LIST['1.0'] in data and self.rutas['huayra_repo_url'] in data:
                renglones[index] = data.replace(HUAYRA_VERSION_LIST['1.0'], HUAYRA_VERSION_LIST['2.1'])

        with open(self.rutas['source.list'], 'w') as fd:
            fd.write(''.join(renglones))

    def hay_actualizaciones_pendientes(self):
        self.cache.upgrade()
        if len(self.cache.get_changes()) > 0:
            return True

        return False

    def actualizar_paquetes(self):
        self.cache.upgrade(True)
        self.cache.commit(
            apt.progress.text.AcquireProgress(),
            apt.progress.base.InstallProgress()
        )

        self._cache = None

    def instalar_paquete(self, nombre):
        paquete = self.cache[nombre]

        if not paquete.is_installed:
            paquete.mark_install()
            self.cache.commit(
                apt.progress.text.AcquireProgress(),
                apt.progress.base.InstallProgress()
            )

    def eliminar_accesos_escritorio(self):
        for carpeta in os.listdir('/home'):
            for acceso in ACCESOS_ESCRITORIO:
                try:
                    os.unlink(acceso % carpeta)
                except OSError:
                    pass

    def cebar_mate(self):
        for carpeta in os.listdir('/home'):
            with open('/home/%s/.dmrc' % carpeta, 'w') as fd:
                fd.write('''[Desktop]
Session=mate
''')


if __name__ == '__main__':
    print('+----')
    print('| Bienvenido al actualizador de Huayra!')
    print('+----\n')

    if not os.access(RUTAS['source.list'], os.W_OK):
        print(' El actualizador debe ser ejecutado como root.')
        print(' Ej.: $ sudo huayra-update\n')

    else:
        sys.stdout.write('Actualizando a Huayra 2.1, presione "Ctrl + C" para cancelar: ')
        for i in xrange(5, 0, -1):
            sys.stdout.write('%d ' % i)
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write('\n')

        paloma = HuayraUpdate()

        paloma.configuracion_apt('crear')

        if paloma.version_actual == '2.1':
            if paloma.hay_actualizaciones_pendientes():
                paloma.actualizar_paquetes()

        elif paloma.version_actual == '1.0':
            if paloma.hay_actualizaciones_pendientes():
                paloma.actualizar_paquetes()

            paloma.resguardar_repos()
            paloma.modificar_repos()

            if paloma.hay_actualizaciones_pendientes():
                paloma.actualizar_paquetes()

            paloma.instalar_paquete('huayra-libreoffice')
            paloma.eliminar_accesos_escritorio()
            paloma.configuracion_mdm()
            paloma.cebar_mate()

        paloma.configuracion_apt('borrar')
