/*
  Name: gp_chart.js
  Description:
    Support functions for the Glasgow Polyomics web sites for creating dynamic charts.
  Author: Y Gloaguen, Glasgow Polyomics, University of Glasgow, UK
  Version: 0.1 (Draft)
  Date Created: 02 May 2014
  Date Released: Under Development
*/


// SECTION - Dependency definitions.

/*
	Dependencies:
		- Jquery
		- Highcharts.js v.4.0.1

*/

// SECTION - Class definitions. 
// TODO - transform to Class


/*
  Description:
    Functions to create different type of charts 
 
  Data:

  Functions:
    Cell_chart - parsing html dom to create charts within cells of tables.

*/



// ***********************************************************************************************
// ************************************* Cell Chart function *************************************
// ***********************************************************************************************


/*
the function cell_chart will parse the dom and create a chart within td that contain the attribute "data-sparkline"

	Parameters to set in the html (separated by ";"): 
		- list of values separated by coma
		- list of point name
		- type of chart (line by default, alternative option: "column")

	Example of use:
		To create a 2 column chart with mutant = 20 and wildtype = 16
		<td data-sparkline="20, 16 ; mutant ; wildtype ; column">
		
	Misc and warnig:
		- This can curently be used for 2 values only need to update do_chunk function to be more flexible
		- The function integrate a timeout to allow interaction with the browser if the process take to much time, a perfomance feedback is automatically printed in the log of the browser (to remove in production).
		- !IMPORTANT! Call this function when the page is loaded only
*/

function cell_chart() {
			    /**
			     * Create a constructor for sparklines that takes some sensible defaults and merges in the individual 
			     * chart options. This function is also available from the jQuery plugin as $(element).highcharts('SparkLine').
			     */
			    Highcharts.SparkLine = function (options, callback) {
			        var defaultOptions = {
			            chart: {
			                renderTo: (options.chart && options.chart.renderTo) || this,
			                backgroundColor: null,
			                borderWidth: 0,
			                type: 'area',
			                margin: [2, 0, 2, 0],
			                width: 120,
			                height: 20,
			                style: {
			                    overflow: 'visible'
			                },
			                skipClone: true
			            },
			            title: {
			                text: ''
			            },
			            exporting: {
			           		enabled: false,
			        	},
			            credits: {
			                enabled: false
			            },
			            xAxis: {
			                labels: {
			                    enabled: false
			                },
			                title: {
			                    text: null
			                },
			                startOnTick: false,
			                endOnTick: false,
			                tickPositions: []
			            },
			            yAxis: {
			                endOnTick: false,
			                startOnTick: false,
			                labels: {
			                    enabled: false
			                },
			                title: {
			                    text: null
			                },
			                tickPositions: [0]
			            },
			            legend: {
			                enabled: false
			            },
			            tooltip: {
			                // backgroundColor: null,
			                borderWidth: 0,
			                shadow: false,
			                useHTML: true,
			                hideDelay: 0,
			                shared: true,
			                padding: 0,
			                positioner: function (w, h, point) {
			                    return { x: point.plotX - w / 2, y: point.plotY - h};
			                },
			                style: {
			                	position: 'absolute',
			                	padding: '5px',
								backgroundColor: '#ffffff'
			                	// white-space: 'pre-wrap'
			                }
			            },
			            plotOptions: {
			                series: {
			                    animation: false,
			                    lineWidth: 1,
			                    shadow: false,
			                    states: {
			                        hover: {
			                            lineWidth: 1
			                        }
			                    },
			                    marker: {
			                        radius: 1,
			                        states: {
			                            hover: {
			                                radius: 2
			                            }
			                        }
			                    },
			                    fillOpacity: 0.25
			                },
			                column: {
			                    negativeColor: '#910000',
			                    borderColor: 'silver'
			                }
			            }
			        };
			        options = Highcharts.merge(defaultOptions, options);

			        return new Highcharts.Chart(options, callback);
			    };

			    var start = +new Date(),
			        $tds = $("td[data-sparkline]"),
			        fullLen = $tds.length,
			        n = 0;

			    // Creating sparkline charts is quite fast in modern browsers, but IE8 and mobile
			    // can take some seconds, so we split the input into chunks and apply them in timeouts
			    // in order avoid locking up the browser process and allow interaction.
			    function doChunk() {
			        var time = +new Date(),
			            i,
			            len = $tds.length;

			        for (i = 0; i < len; i++) {
			            var $td = $($tds[i]),
			                stringdata = $td.data('sparkline'),
			                arr = stringdata.split('; '),
			                intensities = $.map(arr[0].split(', '), parseFloat),
			                chart = {},
			                data = [{
			                	name: arr[1],
			                	y: parseFloat(arr[0].split(', ')[0])
			                }, {
			                	name: arr[2],
			                	y: parseFloat(arr[0].split(', ')[1])
			                }];
			            if (arr[3]) {
			                chart.type = arr[3];
			            }
			            $td.highcharts('SparkLine', {
			                series: [{
			                    data: data,
			                    pointStart: 1
			                }],
			                tooltip: {
			                    headerFormat: '<span style="font-size: 10px; color: #2f7ed8;"><b>{point.key}</b></span><br/>',
			                    pointFormat: '<span style="font-size: 10px">Intensity :</span><br/><b>{point.y}</b>',
			                    style: {
				                	position: 'absolute',
				                	padding: '5px',
									backgroundColor: '#ffffff'
				                	// white-space: 'pre-wrap'
			                	}
			                },
			                chart: chart
			            });

			            n++;
			            
			            // If the process takes too much time, run a timeout to allow interaction with the browser
			            if (new Date() - time > 500) {
			                $tds.splice(0, i + 1);
			                setTimeout(doChunk, 0);
			                break;
			            }

			            // Print a feedback on the performance
			            if (n === fullLen) {
			                console.log('Generated ' + fullLen + ' sparklines in ' + (new Date() - start) + ' ms');
			            }
			        }
			    }
			    doChunk();
			    
			}