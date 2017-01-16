
#!/bin/sh
# Go to MetExploreViz folder

if [ $# -ne 1 ] # s'il n'y a pas 1 paramètres 
then
         echo 'Parameter is required : \n\t1: sencha cmd path'
else
	arg=$1
        
	cd ../
	# Build ExtJS
	$arg app build  

	cd ./scripts/
	# Link to the file which contain metExploreViz version 
	appJS="../build/production/metExploreViz/app.json"

	# Parse JSON to get version
	sub='\["version"]'
	lineversion=$(./JSON.sh -l < $appJS| egrep $sub)
	version=${lineversion#$sub}
	newversion=$(echo $version | sed s/\"//g)
	echo $newversion
	unixOS=$(uname)
	echo $unixOS 
	# ../licenses/compil\&licence.sh => add licenses
	# ../build/production/metExploreViz/  => MetExploreViz production folder
	if [ $unixOS != "Linux" ] && [ $unixOS != "Darwin" ]
	then
		echo "This feature is not provided in your operating system" 
	else
		echo ../licenses/compil\&licence$unixOS.sh
		../licenses/compil\&licence$unixOS.sh ../build/production/metExploreViz/ $newversion
	fi
 
fi

