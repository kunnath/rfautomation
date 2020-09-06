#!/bin/bash -x
_env_file=default_env.sh
this_dir=$(cd $(dirname ${BASH_SOURCE[0]})/ && pwd)
chmod -R 777 $(cd $(dirname ${BASH_SOURCE[0]})/ && pwd)
mock_data_dir=$(cd ${this_dir}/../ && pwd)/mock-data
chmod -R 777 $(cd ${this_dir}/../ && pwd)/mock-data
source ${this_dir}/${_env_file}
curl -vvvv -X POST -H "X-Api-Key: $GW_API_KEY" -H "Content-Type: application/json" --data @${mock_data_dir}/create-event.json "$GW_BASE_URL/videocloud/event"