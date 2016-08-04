

// Register every of the result page component for click actions
var metexplore_init = false;

function set_click_actions(staticUrl, metexploreInfoUrl){

	$('#enlarge').click(function() {
		if (fullScreen){
			$('#main-pimp-navbar').show();
			$('#subheader').css('padding-top',40);
			$('#serch-banner').show();
			$('#main-container').css('top',155);
			$('.metabolites-table_wrapper_toolbar').css('top',155);
			$('.pathway-table_wrapper_toolbar').css('top',155);
			$('.comparison-table_wrapper_toolbar').css('top',155);
			$('.peak-table_wrapper_toolbar').css('top',155);
			$('#search2').hide();
			$('#tool_menu_bar').css('top',115);
			$('#polyomics_logo').hide();
			$('#tool_button').css('left',20);
			$('#tool_button_text').show();
			fullScreen = false;
		}
		else{
			$('#main-pimp-navbar').hide();
			$('#subheader').css('padding-top',0);
			$('#serch-banner').hide();
			$('#main-container').css('top',41);
			$('.metabolites-table_wrapper_toolbar').css('top',41);
			$('.pathway-table_wrapper_toolbar').css('top',41);
			$('.comparison-table_wrapper_toolbar').css('top',41);
			$('.peak-table_wrapper_toolbar').css('top',41);
			$('#search2').show();
			$('#tool_menu_bar').css('top',0);
			$('#polyomics_logo').show();
			$('#tool_button').css('left',54);
			$('#tool_button_text').hide();
			fullScreen = true;
		}
	});

	$('#close-right-summary-panel').click(function(){
		$("#first-pathway").css("margin-top",25);
		$('#right-summary-panel').css('display','block');
		$('#right-summary-panel').css('margin-right','-55%');
		$('#right-summary-panel').css('display','none');
		$('#right-summary-panel-arrow').css('display','none');
	});

	$('#tabnav a').click(function (e) {
		e.preventDefault();
		$(this).tab('show');
		if ($(this).parent().attr('id') == "metabolites-li" ){
			//console.log("clicked on id tab");
			$('#metabolites_table_super_pathway_selector_div').show();
			$('#metabolites_table_pathway_selector_div').show();
		}
		else {
			$('#metabolites_table_super_pathway_selector_div').hide();
			$('#metabolites_table_pathway_selector_div').hide();
		}
		$("#first-pathway").css("margin-top",25);
		$('#right-summary-panel').css('display','block');
		$('#right-summary-panel').css('margin-right','-55%');
		$('#right-summary-panel').css('display','none');
		$('#right-summary-panel-arrow').css('display','none');
		ttInstances = TableTools.fnGetMasters();
	        for (i in ttInstances) {
	            if (ttInstances[i].fnResizeRequired()) ttInstances[i].fnResizeButtons();
	        }
	});

	$('#right-side-button').click(function (e) {
		if (right_panel) {
			$('.myspan3').width('0%');
			$('.myspan9').width('100%');
			$('.metabolites-table_wrapper_toolbar').width('100%');
			$('.peak-table_wrapper_toolbar').width('100%');
			$('.comparison-table_wrapper_toolbar').width('100%');
			$('.pathway-table_wrapper_toolbar').width('100%');
			$('.dataTables_paginate').width('100%');
			$('#right-arrow').removeClass('show-right').addClass('show-left');
			right_panel = false;
		}
		else {
			$('.myspan3').width('20%');
			$('.myspan9').width('80%');
			$('.metabolites-table_wrapper_toolbar').width('80%');
			$('.peak-table_wrapper_toolbar').width('80%');
			$('.comparison-table_wrapper_toolbar').width('80%');
			$('.pathway-table_wrapper_toolbar').width('80%');
			$('.dataTables_paginate').width('80%');
			$('#right-arrow').removeClass('show-left').addClass('show-right');
			right_panel = true;
		}
	});

	// $('#home_button').click(function (e) {
	// 	e.preventDefault();
	// 	$("#first-pathway").css("margin-top",25);
	// 	$('#right-summary-panel').css('display','block');
	// 	$('#right-summary-panel').css('margin-right','-55%');
	// 	$('#right-summary-panel').css('display','none');
	// 	$('#right-summary-panel-arrow').css('display','none');
	// 	$('#tabnav').find('.active').removeClass('active');
	// 	$('#general-tab-content').find('.active').removeClass('active');
	// 	$('#home').addClass('active');
	// });

	$('#preferences').click(function (e) {
		var $modal = $("#full-width");
		var modalBody = $modal.find('.modal-body');
		var modalHeader = $modal.find('.modal-header');
		var modalFooter = $modal.find('.modal-footer');

		// Empty modal window

		$(modalBody).empty();
		$(modalFooter).empty();
		$(modalHeader).empty();

		// Set general wndow buttons

		$('<button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>').appendTo($(modalFooter));
		$('<button class="btn btn-primary" data-dismiss="modal" id="save_preference">Save changes</button>').appendTo($(modalFooter));

		$('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/preference_icon.png" alt="tools" style="margin-bottom: 3px;"> Preferences</h3>').appendTo($(modalHeader));

		// Section divs creation

		var rightPanelPreferencesContent = $('<h3 style="margin-left:10px;">Right panel</h3><h4 style="margin-left:10px;">Default display</h4><div class="row" style="margin-left:0px;margin-bottom: 15px;"><div class="span6" style="margin-left:10px;"><input id="rightPanelSummaryCheck" type="radio" name="right_panel_preference" value="summary" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Summary</span></div><div class="span6" style="margin-left:10px;"><input id="rightPanelDetailsCheck" type="radio" name="right_panel_preference" value="details" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Details</span></div></div><h4 style="margin-left:10px;">Intensity comparison chart export</h4><div class="row" style="margin-left:0px;margin-bottom: 15px;"><div class="span6" style="margin-left:10px;"><input id="enableIntensityExport" type="radio" name="intensity_export_preference" value="true" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Enable</span></div><div class="span6" style="margin-left:10px;"><input id="disableIntensityExport" type="radio" name="intensity_export_preference" value="false" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Disable</span></div></div><h4 style="margin-bottom: 20px;margin-left:10px;">Peak chromatograms graph display:</h4><div class="row" style="margin-left:0px;margin-bottom: 15px;"><div class="span6" style="margin-left:10px;"><input id="peakChromatogramEnabled" type="radio" name="peak_chrom_display" value="true" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Enable</span></div><div class="span6" style="margin-left:10px;"><input id="peakChromatogramDisabled" type="radio" name="peak_chrom_display" value="false" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Disable</span></div></div>');

		var peakChromatogramsContent = $('<h3 style="margin-left:10px;">Peak chromatograms</h3><div class="row" style="margin-left:0px;"><div class="span6" style="margin-left:10px;"><h4 style="margin-bottom: 20px;">Retention time window (s): <span id="rtwindow_span">'+rtwindow+'</span></h4><span style="font-weight:bold;margin-right:12px;">15</span><input id="rt_window_slider" type="text" class="span2" value="" data-slider-min="15" data-slider-max="180" data-slider-step="5" data-slider-value="'+rtwindow+'" data-slider-selection="before"><span style="font-weight: bold;margin-left: 12px;">180</span></div><div class="span6" style="margin-left:10px;"><h4 style="margin-bottom: 20px;">Mass window (ppm): <span id="ppm_span">'+ppm+'</span></h4><span style="font-weight: bold;margin-right: 12px;">1</span><input id="ppm_slider" type="text" class="span2" value="" data-slider-min="1" data-slider-max="5" data-slider-step="1" data-slider-value="'+ppm+'" data-slider-selection="before"><span style="font-weight: bold;margin-left: 12px;">5</span></div>');

		var columnChartPreferenceTitle = $('<h3 style="margin-left:10px;">Intensity comparison chart</h3>');

		var columnChartPreferenceRow = $('<div class="row" style="margin-left:0px;"></div>');

		var columnChartPreferenceDiv = $('<div class="span12" style="margin-left:10px;"></div>');

		var columnChartPreferenceContent = '<h4 style="margin-bottom: 20px;margin-left:10px;">Point index:</h4>';

		var chartTypePreferenceContent = $('<div class="row" style="margin-left:10px;"><h4 style="margin-bottom: 20px;">Chart type:</h4><div class="row" style="margin-left:0px;margin-bottom: 15px;"><div class="span6" style="margin-left:10px;"><input id="columnTypeChart" type="radio" name="type_chart_preference" value="column" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Column</span></div><div class="span6" style="margin-left:10px;"><input id="lineTypeChart" type="radio" name="type_chart_preference" value="line" style="margin-bottom: 3px;margin-top:0px;"><span style="font-weight: bold;margin-left:12px;margin-right:12px;">Line</span></div></div></div>');

		var counter = 0;

		$.each(memberColumnIndex, function( index, value ){
			// if (counter%2 == 1){
			columnChartPreferenceContent += '<div class="span6"><label for="'+ index +'_index" style="font-weight:bold;margin-right:12px;">'+ index +'</label><select name="'+ index +'" class="column_index" style="width:140px" id='+ index +'_index>';
			j = 0;
			for (var i=0;i<memberList.length;i++){
				j = i+1;
				columnChartPreferenceContent += '<option value="'+ i +'">'+ j +'</option>';
			}
			columnChartPreferenceContent += '</select></div>'
		});

		$(columnChartPreferenceContent).appendTo($(columnChartPreferenceDiv));

		$(columnChartPreferenceContent).appendTo($(columnChartPreferenceRow));


		// Add right panel preference section to window's body

		$(rightPanelPreferencesContent).appendTo($(modalBody));

		// Set values

		if (rightPanelPreference == "summary"){
			$('#rightPanelSummaryCheck').prop('checked', true);
		}
		else {
			$('#rightPanelDetailsCheck').prop('checked', true);
		}

		if (averageExport == true){
			$('#enableIntensityExport').prop('checked', true);
		}
		else {
			$('#disableIntensityExport').prop('checked', true);
		}

		if (peakChromatogramsGraph == true){
			$('#peakChromatogramEnabled').prop('checked', true);
		}
		else {
			$('#peakChromatogramDisabled').prop('checked', true);
		}

		// Add peak chromatograms preference section to window's body

		$(peakChromatogramsContent).appendTo($(modalBody));

		// Set slider and values

		$('#rt_window_slider').slider().on('slide', function(ev){
			$('#rtwindow_span').empty().text($('#rt_window_slider').data('slider').getValue());
		});
		$('#ppm_slider').slider().on('slide', function(ev){
			$('#ppm_span').empty().text($('#ppm_slider').data('slider').getValue());
		});

		// if (peakChromatogramsGraph == true){
		// 	$('#rt_window_slider').slider('enable');
		// 	$('#ppm_slider').slider('enable');
		// }
		// else {
		// 	$('#rt_window_slider').slider('disable');
		// 	$('#ppm_slider').slider('disable');
		// }

		// Add chart preference sections to window's body

		$(columnChartPreferenceTitle).appendTo($(modalBody));

		$(columnChartPreferenceRow).appendTo($(modalBody));

		$(chartTypePreferenceContent).appendTo($(modalBody));

		// Set column chart select values

		$('.column_index').each(function(){
			$(this).val(memberColumnIndex[$(this).attr('name')].toString());
		});

		// Set column chart select click behaviour

		$('.column_index').click(function () {
        	// Store the current value on focus and on change
        	previous = this.value;
        	console.log('previous '+previous);
    	}).change(function() {
        	// Do something with the previous value after the change
        	element = $(this).attr('id');
        	newValue = this.value;
        	console.log('new value '+newValue);
        	console.log($('.column_index option:selected[value="'+ newValue +'"]'));
   //      	$('.column_index').each(function(){
			// $(this).val(newValue.toString());
			// });
        	$('.column_index option:selected[value="'+ newValue +'"]').each(function(){
        	// // 	console.log(this);
        		if ($(this).parent().attr('id') != element) {
        			$(this).parent().val(previous);
        		}
        	});
        	// alert(previous);

        	// Make sure the previous value is updated
        	// previous = this.value;
    	});

    	if (rightPanelPreference == "summary"){
			$('#rightPanelSummaryCheck').prop('checked', true);
		}
		else {
			$('#rightPanelDetailsCheck').prop('checked', true);
		}

		if (averageChartType == "column"){
			$('#columnTypeChart').prop('checked', true);
		}
		else {
			$('#lineTypeChart').prop('checked', true);
		}

		// Display modal window

		$modal.modal();

		// Set save button click action

		$('#save_preference').click(function (e) {
			ppm = $('#ppm_slider').data('slider').getValue();
			rtwindow = $('#rt_window_slider').data('slider').getValue();
			peakChromatogramsGraph = ($('input:radio[name=peak_chrom_display]:checked').val() === "true");
			rightPanelPreference = $('input:radio[name=right_panel_preference]:checked').val();
			averageExport = ($('input:radio[name=intensity_export_preference]:checked').val() === "true");
			$('.column_index').each(function() {
				memberColumnIndex[$(this).attr('name')] = $(this).val();
			});
			averageChartType = $('input:radio[name=type_chart_preference]:checked').val();
		});

	});

	$('#metexplore').click(function (e) {
        var list_identified_metabolites = [];
        var $modal = $("#full-width");
        var modalBody = $modal.find('.modal-body');
        var modalHeader = $modal.find('.modal-header');
        var modalFooter = $modal.find('.modal-footer');

        $(modalBody).empty();
        $(modalFooter).empty();
        $(modalHeader).empty();

        // var url = metexploreInfoUrl;

        var biosourceUrl = metexploreBiosourceUrl;

        // ****************************************************************************
        // ****************************************************************************
        // ****************************************************************************
        $.ajax({
            type: "GET",
            traditional : true,
            url: biosourceUrl,
            success: function(response){
                // var mydatastring = "";
                // for (var i=0;i<response.length;i++){
                //  var stringName = response[i]["name"]+"\t";
                //  mydatastring = mydatastring + stringName;
                //  for (var j=0;j<response[i]["conditions"].length;j++){
                //      var stringCondition = response[i]["conditions"][j]+(j==response[i]["conditions"].length-1 ? '': '\t');
                //      mydatastring = mydatastring + stringCondition;
                //  }
                //  mydatastring = mydatastring+ "\n";
                // }
                $('<button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>').appendTo($(modalFooter));
                $('<button class="btn btn-primary" id="launch_metexplore">Launch</button>').appendTo($(modalFooter));

                $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/Logo_Metexplore_40px.png" alt="tools" style="margin-bottom: 3px;"> Network analysis with MetExplore Viz</h3>').appendTo($(modalHeader));

                var rightPanelPreferencesContent = $('<div class="row" style="margin-left:0px;margin-bottom: 15px;"><div class="span6"><h3 style="margin-left:10px;margin-bottom: 0px;">MetExplore Viz parameters</h3><div id="biosource-info" style="height:27px"></div><select name="Select MetExplore Biosource" id="biosource_selector"><option disabled>Select MetExplore Biosource</option></select><div id="pathway-info" style="height:27px"></div><select name="Select MetExplore Pathway" multiple="multiple" id="met_pathway_selector"><option disabled>Select MetExplore Pathway</option></select></div><div class="span6"><h3 style="margin-left:10px;">What is MetExplore</h3><p style="margin-left:10px;">Met­Ex­plore is a web server ded­i­cated to the analy­sis of genome scale meta­bolic networks</p><p style="margin-left:10px;">For more information, please visit <a href="http://metexplore.toulouse.inra.fr/joomla3/"  target="_blank">MetExplore website</a></div></div></div>');

                for (var i=0;i<response.length;i++){
                    $('<option value="'+response[i]['id']+'">'+response[i]['displayName']+'</option>').appendTo($(rightPanelPreferencesContent).find('#biosource_selector'));
                }

                $(rightPanelPreferencesContent).appendTo($(modalBody));

                $modal.modal();

                $('#biosource_selector').select2({
                    placeholder: "Select MetExplore biosource",
                    allowClear: false,
                });

                $('#met_pathway_selector').select2({
                    placeholder: "Select MetExplore pathway",
                    allowClear: false,
                });

                var $eventSelectBiosource = $("#biosource_selector");

                var $eventSelectPathway = $("#met_pathway_selector");

                $eventSelectPathway.on("select2:select", function (e) { handle_error("select2:select", e); });
                $eventSelectPathway.on("select2:unselect", function (e) { handle_unselect("select2:unselect", e); });

                function handle_error (name, evt) {
                    $('#pathway-info').html("");
                }

                function handle_unselect (name, evt) {
                    if (!evt) {
                    var args = "{}";
                  } else {
                    // console.log(evt.params);
                    var id = evt.params['data']['id']
                    console.log(id);
                  }
                  var idsPathway = $('#met_pathway_selector').val();

                  console.log(idsPathway);

                  if (!idsPathway){
                    $('#pathway-info').html("<p style='font-size:12px;padding-top:3px;'>Please select a minimum of one pathway</p>").css('color','red');
                  }
                }

                $eventSelectBiosource.on("select2:select", function (e) { get_pathway("select2:select", e); });

                function get_pathway (name, evt) {
                  if (!evt) {
                    var args = "{}";
                  } else {
                    // console.log(evt.params);
                    var id = evt.params['data']['id']
                    console.log(id)
                  }
                  $('#biosource-info').html('');
                  // var $e = $("<li>" + name + " -> " + args + "</li>");
                  console.log("selected biousource");
                  var ajax_data = {"id": id};
                  $.ajax({
                        type: "GET",
                        traditional : true,
                        url: metPathwayUrl,
                        data: ajax_data,
                        success: function(response){
                            console.log(response);
                            if (response == "empty"){
                                // Change this to display message to user
                                console.log("No pathway");
                                var $selectPathway = $("#met_pathway_selector");
                                // save current config. options
                                var options = $selectPathway.data('select2').options.options;
                                // delete all items of the native select element
                                $selectPathway.html('');

                                // add new items
                                $selectPathway.select2(options);
                            }
                            else{
                                var $selectPathway = $("#met_pathway_selector");
                                // save current config. options
                                var options = $selectPathway.data('select2').options.options;
                                // delete all items of the native select element
                                $selectPathway.html('');

                                // build new options
                                for (var i=0;i<response.length;i++) {
                                    $selectPathway.append('<option value="'+response[i]['id']+'">'+response[i]['text']+'</option>');
                                }
                                // add new items
                                options.data = response;
                                $selectPathway.select2(options);
                            }

                        },
                        error: function(){
                            console.log("error");
                        }
                    });

                }

                $('#launch_metexplore').click(function (e) {

                    var idBioSource = $('#biosource_selector').val();
                    var idsPathway = $('#met_pathway_selector').val();

                    if (!idsPathway){
                        console.log(idsPathway);
                        console.log("ya pas de pathway selectionné!");
                        console.log(idBioSource);
                        $('#pathway-info').html("<p style='font-size:12px;padding-top:3px;'>Please select a minimum of one pathway</p>").css('color','red');
                        if (idBioSource == "Select MetExplore Biosource"){
                            $('#biosource-info').html("<p style='font-size:12px;padding-top:3px;'>Please select a biosource</p>").css('color','red');
                        }
                    }
                    else{
                        $modal.modal('hide');

                        var ajax_data = {"biousourceid": idBioSource, "pathwayids": idsPathway };

                        // var url = networkUrl + "?id='" + idBioSource + "'";
                        // console.log(url);
                        $.ajax({
                            type: "GET",
                            traditional : true,
                            url: networkUrl,
                            data: ajax_data,
                            success: function(response){
                                if (response == "error"){
                                    console.log("ERROR returned");
                                    var $modal = $("#small-window");
                                    var modalBody = $modal.find('.modal-body');
                                    var modalHeader = $modal.find('.modal-header');
                                    var modalFooter = $modal.find('.modal-footer');
                                    $(modalBody).empty();
                                    $(modalFooter).empty();
                                    $(modalHeader).empty();


                                    $('<button class="btn" data-dismiss="modal" aria-hidden="true">Ok</button>').appendTo($(modalFooter));
                                    $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/Logo_Metexplore_40px.png" alt="tools" style="margin-bottom: 3px;"> Network analysis</h3>').appendTo($(modalHeader));
                                    $('<p style="margin-top: 20px;margin-bottom: 20px;text-align:center;">The server is temporarily unavailable, please try again later.</p>').appendTo($(modalBody));

                                    $modal.modal();
                                }
                                else if (response == "empty"){
                                    console.log("No pathway returned returned");
                                    var $modal = $("#small-window");
                                    var modalBody = $modal.find('.modal-body');
                                    var modalHeader = $modal.find('.modal-header');
                                    var modalFooter = $modal.find('.modal-footer');
                                    $(modalBody).empty();
                                    $(modalFooter).empty();
                                    $(modalHeader).empty();
                                    $('<button class="btn" data-dismiss="modal" aria-hidden="true">Ok</button>').appendTo($(modalFooter));
                                    $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/Logo_Metexplore_40px.png" alt="tools" style="margin-bottom: 3px;"> Network analysis</h3>').appendTo($(modalHeader));
                                    $('<p style="margin-top: 20px;margin-bottom: 20px;text-align:center;">No metabolite could be mapped on the selected biosource</p>').appendTo($(modalBody));

                                    $modal.modal();
                                }
                                else {
                                    $('.tab-pane.active').removeClass('active');
                                    $('#tabnav').find('.active').removeClass('active');
                                    $('#metexplore-li').removeClass('hidden-tab').addClass('active');
                                    $('#metexplore-viz').removeClass('hidden-tab').addClass('active');
                                    if (!metexplore_init) {
                                        MetExploreViz.initFrame("metexplore-container");
                                        metexplore_init = true;
                                        console.log("Initialisation MetExplore viz");
                                    }
                                    MetExploreViz.onloadMetExploreViz(function(){
                                        //Set mapping style
                                        // metExploreViz.GraphMapping.onloadMapping("Global Mapping", function(){
                                        //     metExploreViz.GraphMapping.removeMappingData({"title": "Global Mapping"});
                                        // });

                                        // Extract mapping info only and stringify 
                                        var mappingJSON = response['mappingdata'];
                                        var mapping=JSON.stringify(mappingJSON[0]);

                                        if(typeof response != 'string')
                                            var mapJSON=JSON.stringify(response);


                                        var generalStyle = metExploreViz.getGeneralStyle();
                                        var colorMax = generalStyle.getColorMaxMappingContinuous();
                                        metExploreViz.getGeneralStyle().setMaxColorMappingContinuous('red');
                                        metExploreViz.getGeneralStyle().setMinColorMappingContinuous('blue');
                                        
                                        //Run graph
                                        metExploreViz.GraphPanel.refreshPanel(mapJSON, function(){
                                            metExploreViz.onloadSession(function(){



                                                // var mapping = metExploreViz.GraphUtils.parseWebServiceMapping(mapJSON);

                                                //Load mapping
                                                metExploreViz.GraphMapping.loadDataFromJSON(mapping);
                                                //Highlight
                                                metExploreViz.GraphMapping.mapNodes("Global Mapping");
                                                //Color nodes
                                                // metExploreViz.GraphMapping.graphMappingContinuousData("mapping1", "conditionName1");
                                            }); 
                                        }); 
                                    });
                                }
                            },
                            error: function(){
                                $(modalBody).empty();
                                $(modalFooter).empty();
                                $(modalHeader).empty();

                                $('<button class="btn" data-dismiss="modal" aria-hidden="true">Ok</button>').appendTo($(modalFooter));
                                $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/Logo_Metexplore_40px.png" alt="tools" style="margin-bottom: 3px;"> Network analysis with MetExplore Viz</h3>').appendTo($(modalHeader));
                                $('<p style="margin-top: 20px;margin-bottom: 20px;text-align:center;">The server is temporarily unavailable, please try again later.</p>').appendTo($(modalBody));

                                $modal.modal();
                            }
                        });
                    }
                });
            },
            error: function(){
                $('<button class="btn" data-dismiss="modal" aria-hidden="true">Ok</button>').appendTo($(modalFooter));
                $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="myModalLabel"><img src="'+staticUrl+'img/Logo_Metexplore_40px.png" alt="tools" style="margin-bottom: 3px;"> Network analysis with MetExplore Viz</h3>').appendTo($(modalHeader));
                $('<p style="margin-top: 20px;margin-bottom: 20px;text-align:center;">The server is temporarily unavailable, please try again later.</p>').appendTo($(modalBody));

                $modal.modal();
            }
        });

    });

    $(".summary_table_expand_button").click(function() {
        if ($(this).hasClass("active")){
            var summary_table_id_clicked = "#summary_table_container-" + $(this).attr("id").split("-")[1];
            $(this).removeClass("active");
            $(this).text("Show more");
            $(summary_table_id_clicked).removeClass("active");
        }
        else {
            var summary_table_id_clicked = "#summary_table_container-" + $(this).attr("id").split("-")[1];
            $(this).addClass("active");
            $(this).text("Show less");
            $(summary_table_id_clicked).addClass("active");
        }
    });

}

function set_navbar(){
	$('.dropdown-comparison-menu-a').width($('#dropdown-comparison-menu').width());

	$('.dropdown-toggle').dropdown();

	$('#tool_button').hover(function() {
		$('#tool_menu_bar').css('margin-left',0);
		$('#tool_menu_bar').css('box-shadow','4px 4px 10px 0px rgba(0,0,0,.15)');
	});
	$( '#tool_menu_bar').mouseleave(function() {
		$('#tool_menu_bar').css('margin-left',-230);
		$('#tool_menu_bar').css('box-shadow','');
	});
}

// Sort function for the comparison logFC in the metabolites table.
// This forces rows with NA in the comparison logFC to the bottom of the sorted table, regardless
// of whether sorted ascending or descending.
jQuery.fn.dataTableExt.oSort['numeric-ignore-NA-asc'] = function(a, b) {
    if (isNaN(a) && isNaN(b)) { // If a and b are both strings e.g. both NA
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }

    if (isNaN(a)) {
        return 1;
    } else if (isNaN(b)) {
        return -1;
    }

    return ((a < b) ? -1 : ((a > b) ? 1 : 0));

};

jQuery.fn.dataTableExt.oSort['numeric-ignore-NA-desc'] = function(a, b) {
    if (isNaN(a) && isNaN(b)) { // If a and b are both strings e.g. both NA
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    }

    if (isNaN(a)) {
        return 1;
    } else if (isNaN(b)) {
        return -1;
    }

    return ((a < b) ? 1 : ((a > b) ? -1 : 0));

};

function set_metabolitestable(url, samplesGroupsNum){
    // Function to create the metabolites table using dataTables

    // samplesGroupsNum is an array, where index [0] is the number of samples, [1] is the number of groups, and [2] is
    // the number of comparisons
    // These variables are needed to allow DataTables to show/hide the samples intensities or group average intensities.

    // SampleIdxArray and GroupIdxArray are used to make groups for hiding/showing through the ColVis addon for
    // DataTables

    // Compute the indices of the sample intensities in the table
    // There are ALWAYS 5 columns that precede the sample intensities (see experiments.views.get_metabolites_table)
    var numSamples = samplesGroupsNum[0];
    var sampleIdxArray = [];
    for (var n=0; n<numSamples; n++) {
        sampleIdxArray.push(6 + n);
    }

    //// Compute the indices of the group averages and comparisons in the table
    //var numGroups = samplesGroupsNum[1];
    //var groupIdxArray = [];
    //for (var n=0; n<numGroups; n++) {
    //    groupIdxArray.push(sampleIdxArray[sampleIdxArray.length - 1] + 1 + n);
    //}

    // Compute the indices of the comparison logfc columns in the table
    var numComparisons = samplesGroupsNum[1];
    var comparisonIdxArray = [];
    for (var n=0; n<numComparisons; n++) {
        //comparisonIdxArray.push(groupIdxArray[groupIdxArray.length -1] + 1 + n);
        comparisonIdxArray.push(sampleIdxArray[sampleIdxArray.length - 1] + 1 + n);
    }

    // Compute the index of the final column (which is ALWAYS there, irrespective of the number of samples or groups and comparisons)
    //var identifiedColIdx = 5 + numSamples + numGroups + numComparisons + 1;
    var identifiedColIdx = 5 + numSamples + numComparisons + 1;

    // Combine the indices into a single array, exludeColIdx (exclude col indices), to exclude
    var excludeColIdx = [0, 1, 2, 3, 4, 5];
    excludeColIdx.push.apply(excludeColIdx, sampleIdxArray);
    //excludeColIdx.push.apply(excludeColIdx, groupIdxArray);
    excludeColIdx.push.apply(excludeColIdx, comparisonIdxArray);
    excludeColIdx.push(identifiedColIdx);

    // Prepare variables for creating coloured logfc values
    var up_colours = ["#FF6666", "#FF9999", "#FFCCCC"];
    var down_colours = ["#6666FF", "#9999FF", "#CCCCFF"];
    var fold_change_bins = [2, 1, 0.5849625];

    // Get the indices of the initially visible columns, which are Name, Formula, groups, comparisons, Identification
    // This is required since the index of a visible column does not necessarily equal the index of the same column
    // in the whole table, including both hidden and visible rows.
    // Explanation: The data variable in the createdRow anonymous function in the datatable initialisation
    // (idTable below) contains every single column, irrespective of whether they are initially visible or not,
    // whereas access to the data and rows using the jQuery select e.g. $('td', row) contains only the visible
    // elements and their columns.
    var initialCols = [0, 1];

    //// Add indices for the group columns
    //var initialGroupIdx = [];
    //for (var idx in groupIdxArray) {
    //    var groupIdx = initialCols[initialCols.length - 1] + 1;
    //    initialCols.push(groupIdx);
    //    initialGroupIdx.push(groupIdx);
    //}
    //console.log('Indices for initial groups = ' + initialGroupIdx);

    // Add indices for the comparison columns
    var initialComparisonIdx = [];
    for (var idx in comparisonIdxArray) {
        var comparisonIdx = initialCols[initialCols.length - 1] + 1;
        initialCols.push(comparisonIdx);
        initialComparisonIdx.push(comparisonIdx);
    }
    //console.log('Indices for initial comparisons = ' + initialComparisonIdx);

	var metabolitesTable = $('#metabolites-table').DataTable( {
        "sAjaxSource": url,
        "sDom": '<"metabolites-table_wrapper_toolbar"CilT>rtp',
        "oColVis": {
            "sButtonText": "Switch display",
            "aiExclude": excludeColIdx,
            "aoGroups": [
                {
                    "sTitle": "Samples",
                    "aiColumns": sampleIdxArray
                },
                {
                    "sTitle": "Conditions",
                    //"aiColumns": groupIdxArray.concat(comparisonIdxArray)
                    "aiColumns": comparisonIdxArray
                }
            ]
        },
        "createdRow": function (row, data, index) {
            // Set the background-color of the comparison logfc columns to match their values
            // Adapted from data.models.PeakDtComparison.get_fold_change_colour
            //console.log(data);

            // Choose the colour based on the logfc and apply it to the cell
            for (var idx in comparisonIdxArray) {

                var colours = [];

                //console.log(parseFloat(data[comparisonIdxArray[idx]]));

                if (parseFloat(data[comparisonIdxArray[idx]]) > 0) {
                    colours = up_colours;
                    //console.log("LogFC was > 0! " + parseFloat(data[comparisonIdxArray[idx]]));
                } else {
                    colours = down_colours;
                    //console.log("LogFC was < 0! " + parseFloat(data[comparisonIdxArray[idx]]));
                }

                var logFc = Math.abs(parseFloat(data[comparisonIdxArray[idx]]));


                var colour = null;
                for (var i in fold_change_bins) {
                    if (logFc > fold_change_bins[i]) {
                        colour = colours[i];
                        //console.log("The colour will be changed to " + colour);

                        //console.log($('td', row).eq(initialComparisonIdx[idx]).val());
                        $('td', row).eq(initialComparisonIdx[idx]).css('background-color', colour);

                        //console.log("The colour is now ", $('td', row).eq(initialComparisonIdx[idx]).css('background-color'));

                        break;
                    }
                }

            }

        },
        "tableTools": {
            "sSwfPath": "/static/swf/copy_csv_xls.swf",
            "aButtons": [
                {
                    "sExtends": "copy",
                    "sButtonText": "Copy",
                    "mColumns": "visible",
                    "sToolTip": "Copy to clipboard"
                },
                {
                    "sExtends": "collection",
                    "sButtonText": "Export",
                    "aButtons": [
                        {
                            "sExtends": "csv",
                            "sButtonText": "csv",
                            "mColumns": "visible",
                            "sFileName": "compounds.csv",
                            "sToolTip": "Save as CSV"
                        },
                        {
                            "sExtends": "xls",
                            "sButtonText": "xls",
                            "mColumns": "visible",
                            "sFileName": "compounds.xls",
                            "sToolTip": "Save as XLS"
                        }
                    ]
                }
            ]
        },
        "bPaginate": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength": 100,
        "aLengthMenu": [100, 250, 500, 1000],
        "aoColumnDefs": [
            { // compound ID, peak ID
                "aTargets": [0, 1],
                "bSearchable": false,
                "bVisible": false
            },
            { // superpathways pathways
                "aTargets": [4, 5],
                "bSearchable": true,
                "bVisible": false
            },
            { // samples
                "aTargets": sampleIdxArray,
                "bSearchable": false,
                "bVisible": false
            },
            { // comparisons
                "aTargets": comparisonIdxArray,
                "sType": 'numeric-ignore-NA'
            }
        ]
        //"fnDrawCallback": function (oSettings) {
        //    console.log("data finished loaded");
        //    table_received = this;
        //    callback && callback.call(this, table_received);
        //}
    });


	// $("div.metabolites-table_wrapper_toolbar").append('<div id="id_table_pathway_selector_div" style="margin-top: -3px;margin-right: 15px;float: right;width: 200px;"><select id="id_table_pathway_selector"><option></option></select></div><div id="id_table_super_pathway_selector_div" style="margin-top: -3px;margin-right: 15px;float: right;width: 200px;"><select id="id_table_super_pathway_selector"><option></option></select></div>');
    // console.log(excludeColIdx);

	// callback && callback(idTable);

	return metabolitesTable;
}


function set_pathwaytable(){
	var pathwayTable = $('#pathway-table').DataTable( {
					"sDom": '<"pathway-table_wrapper_toolbar"liT>rtp',
					"tableTools": {
			            "sSwfPath": "/static/swf/copy_csv_xls.swf",
			            "aButtons": [
			                {
                    			"sExtends": "copy",
                    			"sButtonText": "Copy",
                    			"mColumns": "visible",
                    			"sToolTip": "Copy to clipboard"
                			},
			                {
			                    "sExtends":    "collection",
			                    "sButtonText": "Export",
			                    "aButtons":    [
			                    	{
					                    "sExtends": "csv",
					                    "sButtonText": "csv",
					                    "mColumns": "visible",
					                    "sFileName": "metabolic_maps.csv",
					                    "sToolTip": "Save as CSV"
                					},
                					{
                    					"sExtends": "xls",
                    					"sButtonText": "xls",
                    					"mColumns": "visible",
                    					"sFileName": "metabolic_maps.xls",
                    					"sToolTip": "Save as XLS"
                					}
                				]
			                }
			            ]
			        },
					"bPaginate": true,
					"sPaginationType": "full_numbers",
					"iDisplayLength": 100,
					"aLengthMenu": [ 100, 250, 500, 1000 ],
					"aoColumns": [
			/* Name */   null,
			/* ID */  { "bSearchable": false,
						"bVisible":    false },
			/* Number compounds */	null,
			/* Annotated */	null,
			/* Identified */	null,
			/* Coverage */	null,
					]
	});

	return pathwayTable;
}

// Sort function for retention times, since they have a custom format of
// "<rt in seconds as float> (<rt in minutes> min <rt in seconds> s)"

jQuery.fn.dataTableExt.oSort['formatted-rt-asc'] = function(a, b) {
	var a = parseFloat(a.match(/^[0-9]*\.?[0-9]+/)[0]);
	var b = parseFloat(b.match(/^[0-9]*\.?[0-9]+/)[0]);
	return a - b;
};

jQuery.fn.dataTableExt.oSort['formatted-rt-desc'] = function(a, b) {
	var a = parseFloat(a.match(/^[0-9]*\.?[0-9]+/)[0]);
	var b = parseFloat(b.match(/^[0-9]*\.?[0-9]+/)[0]);
	return b - a;
};

function set_peaktable(url, callback){
	var peakTable = $('#peak-table').DataTable( {
					// "sDom": '<"toolbar">frtip',
					// "sDom": 't',
					"sAjaxSource": url,
					"aoColumnDefs": [{
							"aTargets": [2],
							"sType": "formatted-rt",
							"mRender": function(rt, type, full) {
								var minutes = Math.floor(rt / 60);
								var seconds = Math.round(rt % 60); // Rounded to nearest second
								return rt + " ("+ minutes + " min "+ seconds + " s)";
							}
						}],
					"sDom": '<"peak-table_wrapper_toolbar"liT>rtp',
					"tableTools": {
			            "sSwfPath": "/static/swf/copy_csv_xls.swf",
			            "aButtons": [
			                {
                    			"sExtends": "copy",
                    			"sButtonText": "Copy",
                    			"mColumns": "visible",
                    			"sToolTip": "Copy to clipboard"
                			},
			                {
			                    "sExtends":    "collection",
			                    "sButtonText": "Export",
			                    "aButtons":    [
			                    	{
					                    "sExtends": "csv",
					                    "sButtonText": "csv",
					                    "mColumns": "visible",
					                    "sFileName": "peaks.csv",
					                    "sToolTip": "Save as CSV"
                					},
                					{
                    					"sExtends": "xls",
                    					"sButtonText": "xls",
                    					"mColumns": "visible",
                    					"sFileName": "peaks.xls",
                    					"sToolTip": "Save as XLS"
                					}
                				]
			                }
			            ]
			        },
					"bPaginate": true,
					"sPaginationType": "full_numbers",
					"iDisplayLength": 100,
					"aLengthMenu": [ 100, 250, 500, 1000 ],
					"fnDrawCallback":function (oSettings) {
						console.log("peak data finished loaded");
						peak_table_received = this;
						callback && callback.call(this, peak_table_received);
					},
	});

	return peakTable;
}

function set_comparisontable(){
	var comparisonTable = $('#comparison-table').dataTable( {
					"sDom": '<"comparison-table_wrapper_toolbar"liT>rtp',
					"tableTools": {
			            "sSwfPath": "/static/swf/copy_csv_xls.swf",
			            "aButtons": [
			                {
                    			"sExtends": "copy",
                    			"sButtonText": "Copy",
                    			"mColumns": "visible",
                    			"sToolTip": "Copy to clipboard"
                			},
			                {
			                    "sExtends":    "collection",
			                    "sButtonText": "Export",
			                    "aButtons":    [
			                    	{
					                    "sExtends": "csv",
					                    "sButtonText": "csv",
					                    "mColumns": "visible",
					                    "sFileName": "comparisons.csv",
					                    "sToolTip": "Save as CSV"
                					},
                					{
                    					"sExtends": "xls",
                    					"sButtonText": "xls",
                    					"mColumns": "visible",
                    					"sFileName": "comparisons.xls",
                    					"sToolTip": "Save as XLS"
                					}
                				]
			                }
			            ]
			        },
					"bPaginate": true,
					"sPaginationType": "full_numbers",
					"iDisplayLength": 100,
					"aLengthMenu": [ 100, 250, 500, 1000 ],
	});

	return comparisonTable;
}
