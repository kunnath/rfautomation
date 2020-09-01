#!/bin/bash -x
report_dir=/opt/robotframework/reports
report_file_output_xml=${report_dir}/output.xml
run-tests-in-virtual-screen.sh && \
robotmetrics -M "${report_dir}"/metrics.html --inputpath "${report_dir}" --logo "https://www.ust-global.com/sites/default/files/ust-logo_dark-blue.png"
chmod -f -R 777 "${report_dir}"
chmod -f -R 777 /opt/robotframework/artifact_store

if [[ -f ${report_file_output_xml} ]]; then
    exit $(python3 -c "from robot.api import ExecutionResult;result = ExecutionResult('"${report_file_output_xml}"');print(result.return_code)")
else
    echo "error: xml report was not generated" >&2
    exit 138
fi
