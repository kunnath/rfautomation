 
#!/bin/bash -x
set -xv   # this line will enable debug
lsof -i:4723
kill $(lsof -t -i:4723)