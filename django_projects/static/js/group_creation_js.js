$(document).ready(function() {
        var sampleList = $('#sample_list').DataTable({
            dom: '<"tablewrapper"fti>',
            paging: false,
            select: {
                style: 'os',
                blurable: true
            },
        });

    // Variables and functions for attribute_construction div
    $('#attribute_construction').show();
    $('.sample_assignment').hide();

    // The number of attributes (experimental conditions) created by the user
    var numberAttributes = 1;

    $('#attribute_construction').on('click', '.add_condition_field', function (e) {
        // Add a new field to the attributes form. Incremement Django's management_form
        // form-TOTAL_FORMS variable to compensate for this, and ensure all forms are
        // handled.

        e.preventDefault();

        // Increment the TOTAL_FORMS variable for django's formset
        numberAttributes++;
        $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);

        // Clone the template field, clearing any cloned input.
        // Increment the id and name values of the fields
        // Django's formset form numbering starts at 0, whereas
        // numberAttributes starts at 0; use (numberAttributes - 1)
        // to update the form index
        var newField = $($('#attribute_form_template').clone().html().replace(/__prefix__/g, numberAttributes - 1));
        newField.find('input').val('');
        newField.appendTo('#attribute_fields');

        // For all except the last input-group, change the input-group-btn
        // button to have remove classes
        $('#attribute_fields').find('.add_condition_field:not(:last)')
            .removeClass('btn-success add_condition_field')
            .addClass('btn-danger remove_field')
            .html('<span class="glyphicon glyphicon-minus"></span>');

    });

    $('#attribute_fields').on('click', '.remove_field', function (e) {
        // Delete the field and reduce the form-TOTAL_FORMS variable for the
        // django management_form
        e.preventDefault();

        // remove the field
        $(this).parents('.input-group:first').remove();

        // Decrement the number of attributes and update the managerform variable
        numberAttributes--;
        $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);

        // Everytime an attribute field is removed the id and name values of all
        // fields must be reset, in case the attribute field removed is not == #attribute_field:last
        var attributeFieldDoms = $('#attribute_fields').find('.input-group');

        attributeFieldDoms.each(function(i, attributeField) {
            // Update the id and names of each remaining attributeField
            var updated = $(attributeField).html().replace(/(attributes-)[0-9]+(-)/g, '$1' + i  + '$2');
            $(attributeField).empty();
            $(attributeField).append(updated);
        });

    });

    $('#attribute_form').on('click', '#go_to_assignment', function (e) {
        e.preventDefault();
        $('#experiment_name').empty().append($('#group_input').val());

        var attributeFieldDoms = $('#attribute_fields').find('input');

        createAttributesDivs(attributeFieldDoms);

        $('#attribute_construction').hide();
        $('.sample_assignment').show();

    });

    $('.sample_assignment').on('click', '#go_to_create_attributes', function (e) {
        console.log("pressed!");
        e.preventDefault();
        $('.sample_assignment').hide();
        $('#attribute_construction').show();
    });

    // variables and functions for sample_assignment div
    function createAttributesDivs(attributeFieldDoms) {
        // TODO: Disable buttons when nothing is selected
        $('#attributes').children('div').remove();


        // Add the divs for each attribute
        var numberSampleAttributes = 0; // number of assignments of samples to attributes

        $.each(attributeFieldDoms, function (_, attribute) {
            // create a div and add and empty buttons
            var addButton = '<button class="btn btn-sm btn-success add"><span class="glyphicon glyphicon-plus"></span></button>';
            var emptyButton = '<button class="btn btn-sm btn-danger empty"><span class="glyphicon glyphicon-trash"></button>';
            var attributeControls = '<div class="btn-group pull-right">' + addButton + emptyButton + '</div>';
            var attributeDiv = '<div class="panel panel-default" id="' + attribute.value + '"><div class="panel-heading clearfix">' + attributeControls + '<h2 class="panel-title pull-left">' + attribute.value + '</h2></div><div class="panel-body"><ol></ol></div></div>';
            $('#attributes').append(attributeDiv);

        });

        $('.add').click(function (e) {
            // Add the selected samples to the selected condition
            e.preventDefault();

            // Begin adding of sample to attribute code

            // Increment the TOTAL_FORMS variable for django's formset
            numberSampleAttributes++;
            $('[name=samplesattributes-TOTAL_FORMS]').val(numberAttributes);

            // Clone the template field, clearing any cloned input.
            // Increment the id and name values of the fields
            // Django's formset form numbering starts at 0, whereas
            // numberAttributes starts at 0; use (numberAttributes - 1)
            // to update the form index
            var newField = $($('#attribute_form_template').clone().html().replace(/__prefix__/g, numberAttributes - 1));
            newField.find('input').val('');
            newField.appendTo('#attribute_fields');

            // For all except the last input-group, change the input-group-btn
            // button to have remove classes
            $('#attribute_fields').find('.add_condition_field:not(:last)')
                .removeClass('btn-success add_condition_field')
                .addClass('btn-danger remove_field')
                .html('<span class="glyphicon glyphicon-minus"></span>');

            // end adding of sample to attribute code


            var attributeDiv = $(this).parents('.panel');
            // Add the samples in the selected table rows
            // to the attributeDiv
            var samplesToAssign = sampleList.rows({
                selected: true
            });
            var sampleData = sampleList.rows({
                selected: true
            }).data();
            $.each(sampleData, function (_, sample) {
                attributeDiv.find('ol').append('<li data-id=' + sample[0] + '>' + sample[1] + '</li>');

            });
            samplesToAssign.remove().draw();
        });

        $('.empty').click(function (e) {
            e.preventDefault();
            var attributeDiv = $(this).parents('.panel');
            var liEls = attributeDiv.find('li');

           	$(liEls).each(function (_, listItem) {
                // liElId = current list element Id
                var liElId = parseInt($(listItem).attr('data-id'));
                sampleList.row.add([liElId, $(listItem).text()[0]]).draw();
            });
            attributeDiv.find('ol').empty();
        });
    }
});