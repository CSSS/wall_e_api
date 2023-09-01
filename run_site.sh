#!/bin/bash

set -e

echo -e "\n[y/N] indicates a yes/no question. the default is the letter in CAPS. If answer is not understood, will revert to default\n"

if [ "${1}" == "--env_file" ];
then
	export run_through_setup="y";
	read_from_env_file="true";
	. ./CI/set_env.sh
	if [[ "${basic_config__DOCKERIZED}" == "y" ]];
	then
		export basic_config__DOCKERIZED='1'
	else
		export basic_config__DOCKERIZED='0'
	fi
	if [[ "${database_config__postgresSQL}" == "1" ]];
	then
		export dockerized_database='y'
		export sqlite3_database='n'
	else
		export dockerized_database='n'
		export sqlite3_database='y'
	fi
else
	echo "Do you need to run through the setup? [y/N]"
	read run_through_setup
fi

if [ "${run_through_setup}" == "y" ];
then
	if [ -z "${basic_config__TOKEN}" ];
	then
		echo "What is your discord bot's token? [see https://discord.com/developers/docs/getting-started if you are not sure how to get it]"
		read basic_config__TOKEN
	fi

	if [ -z "${basic_config__GUILD_ID}" ];
	then
		echo "What is your discord guild's ID? [see https://discord.com/developers/docs/game-sdk/store and https://github.com/CSSS/wall_e/blob/master/documentation/Working_on_Bot/pictures/get_guild_id.png to see where to get it]"
		read basic_config__GUILD_ID
	fi

	use_defaults="false";

	if [ "${1}" == "--default" ];
	then
		use_defaults="true";
		sqlite3_database="y";
		launch_wall_e="y";
		dockerized_database="n";
	fi

	if [ -z "${basic_config__DOCKERIZED}" ];
	then
		echo "Do you want to use a dockerized wall_e? [y/N] a dockerized wall_e is harder to debug but you might run into OS compatibility issues with some of the python modules"
		read basic_config__DOCKERIZED
		if [[ "${basic_config__DOCKERIZED}" == "y" ]];
		then
			export basic_config__DOCKERIZED='1'
		else
			expport basic_config__DOCKERIZED='0'
		fi
	fi

	if [[ "$OSTYPE" == "linux-gnu"* ]];
	then
		supported_os="true"
	else
		supported_os="false"
	fi


	if [ "${use_defaults}" != "true" ];
	then
		echo "Do you you want this script to launch wall_e? [Yn] [the alternative is to use PyCharm]"
		read launch_wall_e
	fi

	echo 'basic_config__TOKEN='"'"${basic_config__TOKEN}"'" > CI/wall_e_website.env
	echo 'basic_config__ENVIRONMENT='"'"'LOCALHOST'"'" >> CI/wall_e_website.env
	echo 'basic_config__COMPOSE_PROJECT_NAME='"'"'discord_bot'"'" >> CI/wall_e_website.env
	echo 'basic_config__GUILD_ID='"'"${basic_config__GUILD_ID}"'" >> CI/wall_e_website.env
	if [[ "${basic_config__DOCKERIZED}" == "y" ]];
	then
		if [[ "${supported_os}" == "false" ]];
		then
			echo "sorry, script is not currently setup to use anything other than a dockerized posgtres database on non-linux system :-("
			echo "Please feel free to add that feature in"
		exit 1
		fi
		echo -e 'basic_config__DOCKERIZED='"'1'\n\n" >> CI/wall_e_website.env
	else
		echo -e 'basic_config__DOCKERIZED='"'0'\n\n" >> CI/wall_e_website.env
	fi

	export POSTGRES_PASSWORD='postgres_passwd'
	echo 'database_config__WALL_E_DB_DBNAME='"'"'csss_discord_db'"'" >> CI/wall_e_website.env
	echo 'database_config__WALL_E_DB_USER='"'"'wall_e'"'" >> CI/wall_e_website.env
	echo 'database_config__WALL_E_DB_PASSWORD='"'"'wallEPassword'"'" >> CI/wall_e_website.env
	echo 'database_config__ENABLED='"'"'1'"'" >> CI/wall_e_website.env

	if [[ "${basic_config__DOCKERIZED}" == "y" ]];
	then
		export COMPOSE_PROJECT_NAME="discord_bot"

		echo 'database_config__postgresSQL='"'"'1'"'" >> CI/wall_e_website.env
		echo -e 'database_config__HOST='"'"${COMPOSE_PROJECT_NAME}_wall_e_db"'\n\n" >> CI/wall_e_website.env
		echo 'ORIGIN_IMAGE='"'"'sfucsssorg/wall_e'"'" >>  CI/wall_e_website.env
		echo 'POSTGRES_PASSWORD='"'"${POSTGRES_PASSWORD}"'" >> CI/wall_e_website.env
		cd wall_e
		. ../CI/user_scripts/set_env.sh
		../CI/user_scripts/setup-dev-env.sh
		docker logs -f "${COMPOSE_PROJECT_NAME}_wall_e"
	else
		if [[ "${use_defaults}" != "true" && -z "${sqlite3_database}" ]];
		then
			echo "Do you want to use db.sqlite3 for the database? [alternative is a separate service, dockerized or not] [Y/n]"
			read sqlite3_database
		fi


		if [[ "${sqlite3_database}" != "y" && -z "${dockerized_database}" ]];
		then
			echo "Do you intended to use dockerized postgres? [Y/n]"
			read dockerized_database
		fi

		if [[ "${dockerized_database}" == "y" && "${supported_os}" == "false" ]];
		then
			echo "sorry, script is not currently setup to use anything other than a dockerized posgtres database on non-linux system :-("
			echo "Please feel free to add that feature in"
		exit 1
		fi

		if [ "${sqlite3_database}" != "y" ];
		then
			echo 'database_config__postgresSQL='"'"'1'"'" >> CI/wall_e_website.env
			echo 'database_config__HOST='"'"'127.0.0.1'"'" >> CI/wall_e_website.env
			echo 'database_config__DB_PORT='"'"'5432'"'" >> CI/wall_e_website.env
		else
			echo 'database_config__postgresSQL='"'"'0'"'" >> CI/wall_e_website.env
			echo 'database_config__HOST='"'"'discord_bot_wall_e_db'"'" >> CI/wall_e_website.env
		fi

		cd wall_e_leveling_website

		python3 -m pip install -r requirements.txt

		. ../CI/set_env.sh

		if [[ "${sqlite3_database}" == "y" ]];
		then
			rm ../db.sqlite3 || true
		else
			sudo apt-get install postgresql-contrib
			docker rm -f "${basic_config__COMPOSE_PROJECT_NAME}_wall_e_db"
			sleep 4
			docker run -d --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} -p \
			"${database_config__DB_PORT}":5432 --name "${basic_config__COMPOSE_PROJECT_NAME}_wall_e_db" \
			postgres:alpine
			sleep 4
			PGPASSWORD=$POSTGRES_PASSWORD psql --set=WALL_E_DB_USER="${database_config__WALL_E_DB_USER}" \
			--set=WALL_E_DB_PASSWORD="${database_config__WALL_E_DB_PASSWORD}"  \
			--set=WALL_E_DB_DBNAME="${database_config__WALL_E_DB_DBNAME}" \
			-h "${database_config__HOST}" -p "${database_config__DB_PORT}"  -U "postgres" \
			-f ../CI/create-database.ddl
		fi

		python3 manage.py migrate
		rm wall_e.json* || true
		wget https://dev.sfucsss.org/wall_e/fixtures/wall_e.json
		python3 manage.py loaddata wall_e.json
		rm wall_e.json* || true

		if [ "${launch_wall_e}" == "n" ];
		then
			echo -e "\n\nSeems you are going to use something else to launch the bot. If you are going to use PyCharm, I HIGHLY recommend using https://github.com/ashald/EnvFile"
		fi
	fi
else
	launch_wall_e="y"
fi

if [ "${launch_wall_e}" != "n" ];
then
	echo "Launching the website."
	sleep 3
	python3 manage.py runserver 127.0.0.1:8000
fi