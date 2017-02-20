

$(document).ready(function() {
	$('.cspider_info_btn').click(function(e){
		console.log("here in js");
 		e.preventDefault();

    	var compound_id = $(this).attr("compound_id");
    	console.log("compound_id: "+ compound_id);
    	var url = cs_url.replace('1234567', compound_id); 
    	var show_cs = $('.show_cs');

    	console.log("the length of the cs_show is "+ show_cs.length); 

    $.ajax({
        type: "GET",
        url: url,
        data: compound_id,
        success: function(response){
        	image_url = response['image_url']
        	csid = response['csid']
        	url = response['cs_url']

        	console.log("The image url is "+image_url);
        	console.log("The CSID returned is "+ response);
        	if (response['csid'] != "None") {
        		$('.cspider_info_btn.'+compound_id).replaceWith('<p>ChemSpider ID: '+ csid + '</p>');
        		$('.cs_image.'+compound_id).append('<img src ="'+ image_url + '"  height="900" >'); 
				$('.cs_url.'+compound_id).append('<a href ="'+ url + '" > ChemSpider </a>');
           }}});
});
});
