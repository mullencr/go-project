#First, we need to remove go.obo.
rm ./go.obo
# Next, download the new one from their permanent link list.
wget "http://purl.obolibrary.org/obo/go.obo"
# Lastly, re-run our read_in_go script with the new go.obo file
# Output the output to an go.log file.
perl read_in_go.pl go.obo > go.log
