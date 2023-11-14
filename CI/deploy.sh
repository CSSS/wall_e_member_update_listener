#!/bin/bash

# PURPOSE: used be jenkins to launch Wall_e to the CSSS PROD Discord Guild

set -e -o xtrace
# https://stackoverflow.com/a/5750463/7734535

rm ${DISCORD_NOTIFICATION_MESSAGE_FILE} || true


export prod_website_container_name="${COMPOSE_PROJECT_NAME}_member_update_listener"
export prod_website_image_name_lower_case=$(echo "${prod_website_container_name}" | awk '{print tolower($0)}')

docker rm -f ${prod_website_container_name} || true
docker image rm -f ${prod_website_image_name_lower_case} || true

export compose_project_name=$(echo "${COMPOSE_PROJECT_NAME}" | awk '{print tolower($0)}')
export docker_compose_file="CI/docker-compose.yml"
docker-compose -f "${docker_compose_file}" up -d
sleep 20

container_failed=$(docker ps -a -f name=${prod_website_container_name} --format "{{.Status}}" | head -1)

if [[ "${container_failed}" != *"Up"* ]]; then
    docker logs ${prod_website_container_name}
    docker logs ${prod_website_container_name} --tail 12 &> ${DISCORD_NOTIFICATION_MESSAGE_FILE}
    exit 1
fi
