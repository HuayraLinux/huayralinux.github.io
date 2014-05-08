#!/bin/bash

# Settings
GKSU=`which gksu`;
WGET=`which wget`;
PYTHON=`which python`;

HUAYRA_UPDATE_PY="huayra-update.py";
URL_HUAYRA_UPDATE_PY="http://huayralinux.github.io/$HUAYRA_UPDATE_PY";
FILE_HUAYRA_UPDATE_PY="/tmp/$HUAYRA_UPDATE_PY";

MSG_ACTUALIZANDO="Actualizando Huayra"
MSG_CONTINUAR="Esta aplicacion se encargara de actualizar la version de Huayra que"
MSG_CONTINUAR="${MSG_CONTINUAR} se encuentra instalada.\n\nClick en 'Si' para continuar."

# Descargamos el script en Python que hace el trabajo fino.
$WGET $URL_HUAYRA_UPDATE_PY -O $FILE_HUAYRA_UPDATE_PY | zenity --progress --pulsate --title="$MSG_ACTUALIZANDO" --auto-kill --auto-close

# Si todo finalizo como deberia:
if [ $? -eq 0 ];
then
        # Preguntamos si realmente desea continuar:
        zenity --question --text="$MSG_CONTINUAR";
        if [ $? -eq 0 ];
        then
                # Aparentemente esta seguro de hacerlo.
                # Damos permisos de ejecucion al actualizador:
                chmod +x $FILE_HUAYRA_UPDATE_PY;
                # Preguntamos por su clave para proceder con la instalacion:
                $GKSU $PYTHON $FILE_HUAYRA_UPDATE_PY;
        fi
fi
