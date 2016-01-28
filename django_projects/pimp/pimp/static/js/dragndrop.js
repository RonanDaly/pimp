$(document).ready(function() {
    $('.drag').draggable({
        revert: true
    });
    $('#myTable02').selectable({
        filter:'tbody tr',
        stop: function(event, ui){
            $(this).find("tr.ui-draggable").draggable("destroy");
            $(this).find("tr.ui-selected").draggable({
                helper: function() {
                    return $("<table></table>")
                        .append(
                            $(this).closest("tbody")
                                .find("tr.ui-selected").clone()
                        )[0];
                },
                appendTo: "body",
                revert: 'invalid',
            });
        }
    });


    //New categorie div creation on button click
    $("#add-categorie-btn").click(function() {
        var catName = $('#id_categorie_name').val()
        var btn = $('<a id="delete' + catName + '" class="btn btn-danger btn-create-project">Delete</a>').click(function () { alert('hi'); });
        var title = $('<div class="span8 description-span"><h3>' + catName + '</h3></div>');
        var elm = $('<div class="span12 project-span out" id="' + catName + 'div">' +
          '<div class="span8 description-span"><h3>' + catName + '</h3></div>' +
          '<div class="span4 span-create-project"><a id="delete' + catName + '"  class="btn btn-danger btn-create-project">Delete</a></div>' +
          '</div>');
        //var parent = $('<div class="span12 project-span"></div>').children().append(title).end();
        //var parent2 = $('<div class="span4 span-create-project"></div>').children().append(btn).end();
        //parent.children().append(parent2).end();
        //$('#categorie-container').children().append(parent).end();
        $(elm).appendTo($('#categorie-container'));
        $('#delete'+catName).bind('click', function(event) {
            $('#'+catName+'div').remove();
        });
        $('#'+catName+'div').droppable({
                //tolerance: 'touch',
                //accept: '.drag',
                over: function() {
                       $(this).removeClass('out').addClass('over');
                },
                out: function() {
                        $(this).removeClass('over').addClass('out');
                },
                drop: function() {
                        //var answer = confirm('Permantly delete this item?');
                        $(this).removeClass('over').addClass('out');
                },
        });
        //alert(title);

    });
    //$("#delete-btn").click(function() {
        //alert("prout");
        //var div = $(this).parent().parent();
        //alert(div);
    //});
});