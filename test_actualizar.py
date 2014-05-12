import unittest
import os

from actualizar import HuayraUpdate

RUTAS_TESTING = {
    'source.list': './tests/sources.list',
    'source.list_backup': './tests/sources.list.%s',
    'huayra_repo_url': 'http://repo.huayra.conectarigualdad.gob.ar/huayra',
    'huayra_version': './tests/huayra_version'
}

HUAYRA_VERSION_LIST = {
    '1.0': 'brisa',
    '2.0': 'pampero'
}

HUAYRA_1_REPOS = """
#

# deb cdrom:[Debian GNU/Linux 7.0.0 _Wheezy_ - Official Snapshot i386 LIVE/INSTALL Binary 20130614-19:09]/ wheezy contrib main non-free

## Repositorio oficial de Debian GNU/Linux
deb http://ftp.debian.org/debian/ wheezy main contrib non-free

## Repositorio de Huayra GNU/Linux
deb http://repo.huayra.conectarigualdad.gob.ar/huayra/ brisa main contrib non-free

## Repositorio de Huayra GNU/Linux (updates)
deb http://repo.huayra.conectarigualdad.gob.ar/huayra/ brisa-updates main contrib non-free

## Repositorio de Mate Desktop
deb http://repo.huayra.conectarigualdad.gob.ar/huayra/ mate-brisa main

deb http://security.debian.org/ wheezy/updates main contrib non-free
deb-src http://security.debian.org/ wheezy/updates main contrib non-free
"""


class Test(unittest.TestCase):
    def test_reescribir_rutas(self):
        a = HuayraUpdate()
        b = HuayraUpdate(rutas=RUTAS_TESTING)

        self.assertNotEqual(a.rutas, b.rutas)

    def test_version_brisa(self):
        open(RUTAS_TESTING['huayra_version'], 'w').write('')
        os.unlink(RUTAS_TESTING['huayra_version'])

        a = HuayraUpdate(rutas=RUTAS_TESTING)
        self.assertEqual(a.version_actual, '1.0')

    def test_version_pampero(self):
        with open(RUTAS_TESTING['huayra_version'], 'w') as fd:
            fd.write('2.0RC1')

        a = HuayraUpdate(rutas=RUTAS_TESTING)
        self.assertEqual(a.version_actual, '2.0')

    def test_resguardar(self):
        open(RUTAS_TESTING['huayra_version'], 'w').write('')
        os.unlink(RUTAS_TESTING['huayra_version'])

        with open(RUTAS_TESTING['source.list'], 'w') as fd:
            fd.write(HUAYRA_1_REPOS)

        a = HuayraUpdate(rutas=RUTAS_TESTING)
        a.resguardar_repos()

        with open(RUTAS_TESTING['source.list'], 'r') as fd:
            archivo_original = fd.read()

        with open(RUTAS_TESTING['source.list_backup'] % HUAYRA_VERSION_LIST[a.version_actual], 'r') as fd:
            archivo_resguardo = fd.read()

        self.assertEqual(archivo_original, archivo_resguardo)

        ### ------

        with open(RUTAS_TESTING['source.list'], 'w') as fd:
            fd.write('TEST')

        a = HuayraUpdate(rutas=RUTAS_TESTING)
        a.resguardar_repos()

        with open(RUTAS_TESTING['source.list'], 'r') as fd:
            archivo_original = fd.read()

        with open(RUTAS_TESTING['source.list_backup'] % HUAYRA_VERSION_LIST[a.version_actual], 'r') as fd:
            archivo_resguardo = fd.read()

        self.assertNotEqual(archivo_original, archivo_resguardo)

    def test_modificar_repos(self):
        pass

    def test_hay_actualizaciones_pendientes(self):
        pass


if __name__ == '__main__':
    unittest.main()
