#!/bin/sh

year=$(date +%Y) 
dateProd=$(LC_ALL="en_DK.utf-8" date)

version=$2
	
execScript(){
	if [ ! -d "$1" ];then
	echo "Any repertory named \"$1\"!";
	else
		cd $1	
		app="$(pwd)"
		echo $app
		copyrightJSandCSS(){

			t="\/*\n"
			t="$t This file is part of MetExploreViz \n\n"
			t="$t Copyright © $year INRA \n"
			t="$t Contact: http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact \n"
			t="$t GNU General Public License Usage \n"
			t="$t This file may be used under the terms of the GNU General Public License version 3.0 as \n"
			t="$t published by the Free Software Foundation and appearing in the file LICENSE included in the \n"
			t="$t packaging of this file. \n"
			t="$t Please review the following information to ensure the GNU General Public License version 3.0 \n"
			t="$t requirements will be met: http:\/\/www.gnu.org\/copyleft\/gpl.html. \n"
			t="$t If you are unsure which license is appropriate for your use, please contact us \n"
			t="$t at http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact\n"
			t="$t Version: $version \n"
			t="$t Build Date: $dateProd \n"
			t="$t *\/\n"

			$(sed -i "1s/^/$t/" $1) 
		}

		copyrightHTMLandXMLandPHP(){

			t="<!-- \n"
			t="$t This file is part of MetExploreViz \n\n"
			t="$t Copyright © $year INRA \n"
			t="$t Contact: http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact \n"
			t="$t GNU General Public License Usage \n"
			t="$t This file may be used under the terms of the GNU General Public License version 3.0 as \n"
			t="$t published by the Free Software Foundation and appearing in the file LICENSE included in the \n"
			t="$t packaging of this file. \n"
			t="$t Please review the following information to ensure the GNU General Public License version 3.0 \n"
			t="$t requirements will be met: http:\/\/www.gnu.org\/copyleft\/gpl.html. \n"
			t="$t If you are unsure which license is appropriate for your use, please contact us \n"
			t="$t at http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact\n"
			t="$t Version: $version \n"
			t="$t Build Date: $dateProd \n"
			t="$t --> \n"
			
			$(sed -i "1s/^/$t/" $1) 
		}

		copyrightLib(){
			t="\n"
			t="$t MetExploreViz - JavaScript Library\n"
			t="$t Copyright (c) 2016, INRA\n"
			t="$t All rights reserved.\n"
			t="$t metexplore@toulouse.inra.fr \n"
			t="$t \n"
			t="$t http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/license\n"
			t="$t \n"
			t="$t Open Source License\n"
			t="$t ------------------------------------------------------------------------------------------\n"
			t="$t This version of MetExploreViz is licensed under the terms of the Open Source GPL 3.0 license.\n" 
			t="$t \n"
			t="$t http:\/\/www.gnu.org\/licenses\/gpl.html\n"
			t="$t \n"
			t="$t Third Party Content\n"
			t="$t ------------------------------------------------------------------------------------------\n"
			t="$t The following third party software is distributed with MetExploreViz and is \n"
			t="$t provided under other licenses and\/or has source available from other locations. \n"
			t="$t \n"
			t="$t Library: Ext JS\n"
			t="$t License: GPL v3 License\n"
			t="$t Location: https:\/\/www.sencha.com\/\n"
			t="$t \n"
			t="$t Library: D3.js\n"
			t="$t License: The BSD 3-Clause License\n"
			t="$t Location: http:\/\/d3js.org\/\n"
			t="$t \n"
			t="$t Library: Graph Dracula JavaScript Framework\n"
			t="$t License: MIT License\n"
			t="$t Location: http:\/\/graphdracula.net\/\n"
			t="$t \n"
			t="$t Library: jQuery JavaScript Library v1.5.2\n"
			t="$t License: MIT, BSD, and GPL Licenses\n"
			t="$t Location: http:\/\/jquery.com\/\n"
			t="$t \n"
			t="$t Library: JavaScript Color Picker 1.4.4\n"
			t="$t License: GNU Lesser General Public License\n"
			t="$t Location: http:\/\/jscolor.com\/\n"
			t="$t \n"
			t="$t Library: Tulip\n"
			t="$t License: GNU Lesser General Public License\n"
			t="$t Location: http:\/\/tulip.labri.fr\/\n"
			t="$t \n"
			t="$t \n"
			t="$t --\n"
			t="$t \n"
			t="$t THIS SOFTWARE IS DISTRIBUTED 'AS-IS' WITHOUT ANY WARRANTIES, CONDITIONS AND REPRESENTATIONS WHETHER EXPRESS OR IMPLIED,\n"
			t="$t INCLUDING WITHOUT LIMITATION THE IMPLIED WARRANTIES AND CONDITIONS OF MERCHANTABILITY, MERCHANTABLE QUALITY, FITNESS FOR A\n"
			t="$t PARTICULAR PURPOSE, DURABILITY, NON-INFRINGEMENT, PERFORMANCE AND THOSE ARISING BY STATUTE OR FROM CUSTOM OR USAGE OF TRADE\n"
			t="$t OR COURSE OF DEALING.\n"
			t="$t \n"
			
			echo "$t" > licences.txt
		}

		copyrightTXT(){
			t="\n"
			t="$t This file is part of MetExploreViz \n\n"
			t="$t Copyright © $year INRA \n"
			t="$t Contact: http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact \n"
			t="$t GNU General Public License Usage \n"
			t="$t This file may be used under the terms of the GNU General Public License version 3.0 as \n"
			t="$t published by the Free Software Foundation and appearing in the file LICENSE included in the \n"
			t="$t packaging of this file. \n"
			t="$t Please review the following information to ensure the GNU General Public License version 3.0 \n"
			t="$t requirements will be met: http:\/\/www.gnu.org\/copyleft\/gpl.html. \n"
			t="$t If you are unsure which license is appropriate for your use, please contact us \n"
			t="$t at http:\/\/metexplore.toulouse.inra.fr\/metexploreViz\/doc\/contact\n"
			t="$t Version: $version \n"
			t="$t Build Date: $dateProd \n"
			
			echo "$t" > licences.txt
		}

		addCopyright(){
			cd $1 
			echo $1

			
			for i in *.js ;do # or whatever other pattern... 
				if [ ! -d "$i" ] && [ "$i" != "*.js" ];then
					copyrightJSandCSS $i
				fi
			done
	
	
			for i in *.css ;do # or whatever other pattern... 
				if [ ! -d "$i" ] && [ "$i" != "*.css" ];then
					copyrightJSandCSS $i
				fi
			done
			for i in *.php ;do # or whatever other pattern... 
				if [ ! -d "$i" ] && [ "$i" != "*.php" ];then
					copyrightHTMLandXMLandPHP $i
				fi
			done
					
			for i in *.html ;do # or whatever other pattern... 
				if [ ! -d "$i" ] && [ "$i" != "*.html" ];then
					copyrightHTMLandXMLandPHP $i
				fi
			done
			for i in *.xml ;do # or whatever other pattern... 
				if [ ! -d "$i" ] && [ "$i" != "*.xml" ];then
					copyrightHTMLandXMLandPHP $i
				fi
			done

			cd $app
		}
		
		copyrightTXT ./

		copyrightLib ./

		addCopyright ./

		addCopyright ./resources/css

		addCopyright ./resources/lib
		addCopyright ./resources/lib/functions
		addCopyright ./resources/lib/model
	fi
}
if [ $# -ne 2 ] # s'il n'y a pas 2 paramètres 
then
         echo 'Parameter is required : \n\t1: a repertory \n\t2: a version number'
else
	arg=$1
        execScript $arg 
fi



