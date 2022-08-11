#!/bin/bash

#
# This script facilates easy add and remove of environment variables used for
# ROSSUM TEST_ENV.
#
# DO NOT MODIFY THE SCRIPT
#

EULA_LOCAL="EULA.txt"
SCRIPT_DIR=`dirname $0`
PWD=`pwd`
ROSSUM_TEST_ENV=$(realpath "$PWD/$SCRIPT_DIR")
echo $ROSSUM_TEST_ENV

usage() {
	echo "`basename $0` <install|uninstall>"
  echo "install   - Adds environment variables in bashrc"
  echo "uninstall - Removes environment variables from bashrc"

	exit 1
}

if [ $# -ne 1 ]; then
	usage
fi

argument=$1

if [ "$argument" != "install" -a "$argument" != "uninstall" ]; then
	usage
fi


if [ "$argument" = "install" ]; then

if [ -e $EULA_LOCAL ] ; then
   more $EULA_LOCAL
   echo
   while :
   do
		  echo "Do you want to accept this End User License Agreement?"
		  echo "Please answer yes or no.."
			read ans
			#ans=${ans,,}
			if [ -z "$ans" ] ; then
			echo ""
			else
			if  [ $ans == "yes" ] ; then
				clear
				echo "EULA $EULA accepted"
				echo
				echo -n press any key to continue ..
				read any
				break
			elif  [ $ans == "Yes" ] ; then
				clear
				echo "EULA $EULA accepted"
				echo
				echo -n press any key to continue ..
				read any
				break
			elif [ $ans == "no" ] ; then
				echo "licence was not accepted !"
				echo "Cannot continue with the installation.."
				exit 1
			elif [ $ans == "No" ] ; then
				echo "licence was not accepted !"
				echo "Cannot continue with the installation.."
				exit 1
			fi
			fi
		done
fi


grep "ROSSUM_TEST_ENV" ~/.bashrc  > /dev/null
if [ $? -eq 0 ]; then
  pip3 install Flask==0.10.1 Flask-HTTPAuth==2.3.0 Flask-RESTful==0.3.1
  pip3 install loguru==0.4.1 openpyxl==2.6.4 oyaml==1.0 pluggy==0.13.1
  pip3 install pyexcel==0.5.15 pyexcel-io==0.5.20 pyexcel-xlsx==0.5.7 xmltodict==0.12.0
  pip3 install openpyxl==2.6.4 distro==1.4.0 xlrd==2.0.1 paramiko==2.6.0 paramiko-expect==0.3.2 

  echo "The environment variables are already added in bashrc. Please do source ~/.bashrc"
  echo ""
  echo ""
  echo "NOTE: Environment Variables are checked for in bashrc assuimng Shell to be bash."
  echo "      In case of other Shell, Please add environment variables manually."
  exit 1
else
  pip3 install Flask==0.10.1 Flask-HTTPAuth==2.3.0 Flask-RESTful==0.3.1
  pip3 install loguru==0.4.1 openpyxl==2.6.4 oyaml==1.0 pluggy==0.13.1
  pip3 install pyexcel==0.5.15 pyexcel-io==0.5.20 pyexcel-xlsx==0.5.7 xmltodict==0.12.0
  pip3 install openpyxl==2.6.4 distro==1.4.0 xlrd==2.0.1 paramiko==2.6.0 paramiko-expect==0.3.2

  echo "The environment variables are added in bashrc. Please do source ~/.bashrc"
  echo "                                                "   >> ~/.bashrc
  echo "                                                "   >> ~/.bashrc
  echo "export ROSSUM_TEST_ENV=$ROSSUM_TEST_ENV"                   >> ~/.bashrc
  echo "export PATH=\$ROSSUM_TEST_ENV:\$PATH"                 >> ~/.bashrc
  echo ""
  echo ""
  echo "NOTE: Environment Variables are added to bashrc assuimng Shell to be bash."
  echo "      In case of other Shell, Please add environment variables manually."
fi
elif [ "$argument" = "uninstall" ]; then
  grep "ROSSUM_TEST_ENV" ~/.bashrc > /dev/null
  if [ $? -eq 0 ]; then
    echo "Removing the environment variables from bashrc. Please do source ~/.bashrc "
    echo ""
    echo ""
    echo "NOTE: Environment Variables are removed from bashrc assuimng Shell to be bash."
    echo "      In case of other Shell, Please remove environment variables manually."
    cat ~/.bashrc | sed "/ROSSUM_TEST_ENV/d" > temp
    cp temp ~/.bashrc && rm temp
  else
    echo "The environment variables are not added"
    echo ""
    echo ""
    echo "NOTE: Environment Variables are checked for in bashrc assuimng Shell to be bash."
    echo "      In case of other Shell, Please remove environment variables manually."
  fi
fi
