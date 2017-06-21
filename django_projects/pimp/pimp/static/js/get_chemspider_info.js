

$(document).ready(function() {
    $('.cspider_info_btn').click(function(e){
        console.log("here in js");
        e.preventDefault();

        var compound_id = $(this).attr("compound_id");
        var url = cs_url.replace('1234567', compound_id);
        var show_cs = $('.show_cs');

    $.ajax({
        type: "GET",
        url: url,
        data: compound_id,
        success: function(response){
            //Data fron the response
            image_url = response['image_url']
            csid = response['csid']
            url = response['cs_url']
            name = response['cs_name']

            console.log("The image url is "+image_url);
            console.log("Returned form the view is: "+ response);
            //If the CSID has been returned successfully from the server
            if (response['csid'] != null) {
                $('.cspider_info_btn.'+compound_id).replaceWith('<p>ChemSpider ID: '+ csid + '</p>');
                $('.cs_image.'+compound_id).replaceWith('<img src ="'+ image_url + '"  height="900" >');
                $('.cs_url.'+compound_id).replaceWith('<a href ="'+ url + '" > ChemSpider </a>');
                $('.cs_name.'+compound_id).replaceWith(name);
            }
            else {
                $('.cspider_info_btn.'+compound_id).replaceWith('<p>No ChemSpider info for '+ name + ' </p>');
            }

           }});
});
});
