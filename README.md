# rfautomation
# RobotSuite

## Running the tests
From the terminal, you can run the included script
Before start to run testscript ,unset ROBOT_OPTIONS
'> unset ROBOT_OPTIONS

# Step:To run WebUI testcase in test
 
#add envirnoment variable 
' > export ROBOT_OPTIONS="-i practice -v env:test"

#run rfdocker in test 
'> ./rf_docker automation

# Step:To run WebUI testcase in dev

#add envirnoment variable
' > export ROBOT_OPTIONS="-i practice -v env:dev -v BROWSER:ch"

#run rfdocker in dev
'> ./rf_docker automation


From Visual Studio Code, you can run one of the following tasks

| Visual Studio Code tasks           | Description                                                       |
|------------------------------------|-------------------------------------------------------------------|
| Build and run RobotFramework tests | Builds the docker image and runs the tests in the default browser |
| Run RobotFramework tests           | Runs the tests in the default browser                             |
| Run RobotFramework tests (firefox) | runs the tests in Firefox                                         |
| Run RobotFramework tests (chrome)  | runs the tests in Chrome                                          |

## Docker options
| Docker environment variable | Description                                              |  Default |
|-----------------------------|----------------------------------------------------------|----------|
| BROWSER                     | Set the browser used to run the tests. (chrome, firefox) | 'chrome' |
| SCREEN_COLOUR_DEPTH         | Set the framebuffer color depth                          | 24       |
| SCREEN_HEIGHT               | Set the framebuffer screen height                        | 1080     |
| SCREEN_WIDTH                | Set the framebuffer screen width                         | 1920     |

