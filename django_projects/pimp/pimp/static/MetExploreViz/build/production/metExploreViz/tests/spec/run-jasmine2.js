/* 
This file is part of MetExploreViz 
 
Copyright (c) 2016 INRA 
 
Contact: http://metexplore.toulouse.inra.fr/metexploreViz/doc/contact 
 
GNU General Public License Usage 
This file may be used under the terms of the GNU General Public License version 3.0 as 
published by the Free Software Foundation and appearing in the file LICENSE included in the 
packaging of this file. 
 
Please review the following information to ensure the GNU General Public License version 3.0 
requirements will be met: http://www.gnu.org/copyleft/gpl.html. 
 
If you are unsure which license is appropriate for your use, please contact us 
at http://metexplore.toulouse.inra.fr/metexploreViz/doc/contact 
 
Version: 1 Build date: 2016-04-13 9:34:37 
*/ 
"use strict";var system=require("system");function waitFor(testFx,onReady,timeOutMillis){var maxtimeOutMillis=timeOutMillis?timeOutMillis:3001,start=new Date().getTime(),condition=false,interval=setInterval(function(){if((new Date().getTime()-start<maxtimeOutMillis)&&!condition){condition=(typeof(testFx)==="string"?eval(testFx):testFx())}else{if(!condition){console.log("'waitFor()' timeout");phantom.exit(1)}else{console.log("'waitFor()' finished in "+(new Date().getTime()-start)+"ms.");typeof(onReady)==="string"?eval(onReady):onReady();clearInterval(interval)}}},100)}if(system.args.length!==2){console.log("Usage: run-jasmine2.js URL");phantom.exit(1)}var page=require("webpage").create();page.onConsoleMessage=function(a){console.log(a)};page.open(system.args[1],function(a){if(a!=="success"){console.log("Unable to access network");phantom.exit()}else{waitFor(function(){return page.evaluate(function(){return(document.body.querySelector(".jasmine-symbol-summary .pending")===null&&document.body.querySelector(".jasmine-duration")!==null)})},function(){var b=page.evaluate(function(){var k="Jasmine";var d=document.body.querySelector(".jasmine-version").innerText;var g=document.body.querySelector(".jasmine-duration").innerText;var c=k+" "+d+" "+g;console.log(c);var f=document.body.querySelectorAll(".jasmine-results > .jasmine-failures > .jasmine-spec-detail.jasmine-failed");if(f&&f.length>0){console.log("");console.log(f.length+" test(s) FAILED:");for(i=0;i<f.length;++i){var e=f[i],j=e.querySelector(".jasmine-description"),h=e.querySelector(".jasmine-messages > .jasmine-result-message");console.log("");console.log(j.innerText);console.log(h.innerText);console.log("")}return 1}else{console.log(document.body.querySelector(".jasmine-alert > .jasmine-bar.jasmine-passed,.jasmine-alert > .jasmine-bar.jasmine-skipped").innerText);return 0}});phantom.exit(b)},30000)}});